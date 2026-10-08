import Anthropic from '@anthropic-ai/sdk';
import type { MessageCountTokensParams } from '@anthropic-ai/sdk/resources/messages/messages.js';
import { query, type SDKUserMessage } from '@anthropic-ai/claude-agent-sdk';
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { z } from 'zod';
import { nativeEnvironment } from './engine.js';
import { Queue } from './tools.js';
import { failure, requestSchema, type NativeProfile, type Result } from './protocol.js';

export const countSchema = requestSchema.omit({ max_tokens: true, stream: true, output_config: true }).extend({ max_tokens: z.number().int().positive().optional() });
export type CountRequest = z.infer<typeof countSchema>;
export type CountQuery = Readonly<{ authenticate: () => Promise<void>; close: () => void }>;
export type CounterDependencies = Readonly<{
  open: (profile: NativeProfile, model: string) => CountQuery;
  readAccess: (profile: NativeProfile) => Promise<string>;
  count: (access: string, body: CountRequest, signal: AbortSignal) => Promise<number>;
}>;
export type Counter = (profile: NativeProfile, body: CountRequest, signal: AbortSignal) => Promise<Result<Readonly<{ input_tokens: number }>>>;
const credentialsSchema = z.object({ claudeAiOauth: z.object({ accessToken: z.string().min(1) }) });
export const nativeCounterDependencies: CounterDependencies = {
  open: (profile, model) => {
    const input = new Queue<SDKUserMessage>();
    const engine = query({ prompt: input, options: { model, tools: [], skills: [], settingSources: [], mcpServers: {}, persistSession: false, cwd: profile.home, env: nativeEnvironment(profile) } });
    return { authenticate: async () => { await engine.supportedModels(); await engine.getContextUsage({ detail: 'full' }); }, close: () => { input.end(); engine.close(); } };
  },
  readAccess: async profile => credentialsSchema.parse(JSON.parse(await readFile(join(profile.configDir, '.credentials.json'), 'utf8'))).claudeAiOauth.accessToken,
  count: async (access, body, signal) => {
    const client = new Anthropic({ apiKey: null, authToken: access, baseURL: 'https://api.anthropic.com', maxRetries: 0, timeout: 30000, defaultHeaders: { 'anthropic-beta': 'oauth-2025-04-20', 'User-Agent': 'litellm-anthropic-native-sdk/1.0' } });
    const { max_tokens: unused, ...payload } = body; void unused;
    return (await client.messages.countTokens(payload as unknown as MessageCountTokensParams, { signal })).input_tokens;
  },
};
export function createCounter(dependencies: CounterDependencies = nativeCounterDependencies): Counter {
  return async (profile, body, signal) => {
    let engine: CountQuery | undefined;
    const combined = AbortSignal.any([signal, AbortSignal.timeout(45000)]);
    let aborted: (() => void) | undefined;
    try {
      if (combined.aborted) return failure(502, 'Native token count was canceled', 'api_error');
      engine = dependencies.open(profile, body.model);
      const canceled = new Promise<never>((_, reject) => {
        aborted = () => reject(new Error('Canceled'));
        combined.addEventListener('abort', aborted, { once: true });
      });
      await Promise.race([engine.authenticate(), canceled]);
      const access = await dependencies.readAccess(profile);
      if (combined.aborted) return failure(502, 'Native token count was canceled', 'api_error');
      const inputTokens = await dependencies.count(access, body, combined);
      if (!Number.isSafeInteger(inputTokens) || inputTokens < 0) return failure(502, 'Native token count returned an invalid result', 'api_error');
      return { ok: true, value: { input_tokens: inputTokens } };
    } catch { return failure(502, 'Native token count failed. Verify the dedicated native profile login', 'api_error'); }
    finally { if (aborted) combined.removeEventListener('abort', aborted); engine?.close(); }
  };
}
