import { createSdkMcpServer, query, type SDKUserMessage, type ThinkingConfig } from '@anthropic-ai/claude-agent-sdk';
import { CallToolRequestSchema, CallToolResultSchema, ListToolsRequestSchema, type CallToolResult } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { objectSchema, type JsonObject, type Message, type NativeProfile, type Request, type ToolDefinition } from './protocol.js';

export type EngineEvent = Readonly<{ type: 'stream'; event: JsonObject }> | Readonly<{ type: 'error' }>;
export type ExternalResult = Readonly<{ content: readonly JsonObject[]; isError: boolean }>;
export type EngineOptions = Readonly<{
  profile: NativeProfile;
  request: Request;
  input: AsyncIterable<Message>;
  beforeTool: (name: string, id: string, args: JsonObject) => Promise<boolean>;
  handleTool: (name: string, args: JsonObject, signal: AbortSignal) => Promise<ExternalResult>;
}>;
export type Engine = Readonly<{ events: AsyncIterable<EngineEvent>; close: () => void }>;
export type QueryFactory = (options: EngineOptions) => Engine;

export function nativeEnvironment(profile: NativeProfile, maxTokens?: number): Record<string, string | undefined> {
  return {
    ...Object.fromEntries(Object.keys(process.env).map(key => [key, undefined])),
    PATH: process.env['PATH'], HOME: profile.home, LANG: 'C.UTF-8',
    CLAUDE_CONFIG_DIR: profile.configDir,
    CLAUDE_AGENT_SDK_CLIENT_APP: 'litellm-anthropic-native-sdk/1.0',
    CLAUDE_CODE_MAX_RETRIES: '0', API_TIMEOUT_MS: '30000',
    ...(maxTokens ? { CLAUDE_CODE_MAX_OUTPUT_TOKENS: String(maxTokens) } : {}),
  };
}

function nativeThinking(request: Request): ThinkingConfig | undefined {
  const thinking = request.thinking;
  if (!thinking) return undefined;
  if (thinking.type === 'disabled') return { type: 'disabled' };
  if (thinking.type === 'adaptive') return { type: 'adaptive', ...(thinking.display ? { display: thinking.display } : {}) };
  return { type: 'enabled', budgetTokens: thinking.budget_tokens, ...(thinking.display ? { display: thinking.display } : {}) };
}

function toolValidator(tool: ToolDefinition): z.ZodType {
  return z.fromJSONSchema(tool.input_schema);
}

function toToolResult(result: ExternalResult): CallToolResult {
  return CallToolResultSchema.parse({ content: result.content, isError: result.isError });
}

export const createNativeEngine: QueryFactory = options => {
  const definitions = options.request.tools ?? [];
  const validators = new Map(definitions.map(tool => [tool.name, toolValidator(tool)]));
  const server = createSdkMcpServer({ name: 'caller', tools: [], alwaysLoad: true });
  server.instance.server.setRequestHandler(ListToolsRequestSchema, () => ({ tools: definitions.map(tool => ({ name: tool.name, description: tool.description ?? '', inputSchema: tool.input_schema, _meta: { 'anthropic/alwaysLoad': true } })) }));
  server.instance.server.setRequestHandler(CallToolRequestSchema, async (request, extra) => {
    const args = objectSchema.parse(request.params.arguments ?? {});
    const validator = validators.get(request.params.name);
    if (!validator || !validator.safeParse(args).success) {
      await options.handleTool(`mcp__caller__${request.params.name}`, args, AbortSignal.abort());
      return { content: [{ type: 'text', text: 'Caller tool arguments failed validation' }], isError: true };
    }
    return toToolResult(await options.handleTool(`mcp__caller__${request.params.name}`, args, extra.signal));
  });
  async function* inputs(): AsyncGenerator<SDKUserMessage> {
    for await (const message of options.input) {
      yield { type: 'user', parent_tool_use_id: null, message: message as SDKUserMessage['message'] };
    }
  }
  const thinking = nativeThinking(options.request);
  const system = options.request.system;
  const sdk = query({
    prompt: inputs(),
    options: {
      model: options.request.model,
      tools: [], skills: [], settingSources: [],
      mcpServers: { caller: server },
      allowedTools: definitions.map(tool => `mcp__caller__${tool.name}`),
      permissionMode: 'default',
      persistSession: false,
      verbatimPrompts: true,
      includePartialMessages: true,
      systemPrompt: system === undefined ? '' : typeof system === 'string' ? system : system.map(block => block.text),
      ...(thinking ? { thinking } : {}),
      ...(options.request.output_config?.effort ? { effort: options.request.output_config.effort } : {}),
      hooks: { PreToolUse: [{ matcher: 'mcp__caller__.*', hooks: [async input => {
        if (input.hook_event_name !== 'PreToolUse') return {};
        const admitted = await options.beforeTool(input.tool_name, input.tool_use_id, objectSchema.parse(input.tool_input));
        return { hookSpecificOutput: { hookEventName: 'PreToolUse', permissionDecision: admitted ? 'allow' : 'deny' } };
      }] }] },
      cwd: options.profile.home,
      env: nativeEnvironment(options.profile, options.request.max_tokens),
    },
  });
  async function* events(): AsyncGenerator<EngineEvent> {
    try {
      for await (const event of sdk) {
        if (event.type === 'stream_event') yield { type: 'stream', event: objectSchema.parse(event.event) };
        if (event.type === 'result' && event.is_error) yield { type: 'error' };
      }
    } catch {
      yield { type: 'error' };
    }
  }
  return { events: events(), close: () => sdk.close() };
};
