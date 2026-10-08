import { createHash, timingSafeEqual } from 'node:crypto';
import { createServer, type IncomingMessage, type Server, type ServerResponse } from 'node:http';
import { realpath, mkdir } from 'node:fs/promises';
import { dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { Broker } from './session.js';
import { createNativeEngine, type QueryFactory } from './engine.js';
import { countSchema, createCounter, type Counter } from './counter.js';
import { parseRequest, scopeFromHeaders, type NativeProfile, type PublicError } from './protocol.js';

export type ServerOptions = Readonly<{ key: string; profiles: ReadonlyMap<string, NativeProfile>; factory?: QueryFactory; counter?: Counter }>;
function json(response: ServerResponse, status: number, body: unknown): void {
  response.writeHead(status, { 'content-type': 'application/json' }); response.end(JSON.stringify(body));
}
function error(response: ServerResponse, value: PublicError): void { json(response, value.status, value.body); }
async function body(request: IncomingMessage): Promise<unknown> {
  const chunks: Buffer[] = []; let size = 0;
  for await (const chunk of request) {
    const bytes = Buffer.isBuffer(chunk) ? chunk : Buffer.from(String(chunk)); size += bytes.length;
    if (size > 16777216) throw new Error('Body too large');
    chunks.push(bytes);
  }
  return JSON.parse(Buffer.concat(chunks).toString('utf8'));
}
export function createBrokerServer(options: ServerOptions): Server {
  if (!options.key) throw new Error('A private native service key is required');
  const broker = new Broker(options.profiles, options.factory ?? createNativeEngine);
  const counter = options.counter ?? createCounter();
  const expected = createHash('sha256').update(`Bearer ${options.key}`).digest();
  const server = createServer((request, response) => { void handle(request, response); });
  server.on('close', () => broker.close());
  async function handle(request: IncomingMessage, response: ServerResponse): Promise<void> {
    if (!timingSafeEqual(expected, createHash('sha256').update(request.headers.authorization ?? '').digest())) {
      error(response, { status: 401, body: { type: 'error', error: { type: 'authentication_error', message: 'Private native service authorization is required' } } }); return;
    }
    if (request.method === 'GET' && request.url === '/health/readiness') { json(response, 200, { status: 'ready', profiles: options.profiles.size }); return; }
    if (request.method !== 'POST' || !['/v1/messages', '/v1/messages/count_tokens'].includes(request.url ?? '')) { json(response, 404, { type: 'error', error: { type: 'not_found_error', message: 'Unknown native endpoint' } }); return; }
    const scope = scopeFromHeaders(request.headers); if (!scope.ok) { error(response, scope.error); return; }
    const profile = options.profiles.get(scope.value.profile);
    if (!profile) { error(response, { status: 403, body: { type: 'error', error: { type: 'permission_error', message: 'Native profile is not allowed' } } }); return; }
    const abort = new AbortController();
    response.on('close', () => { if (!response.writableEnded) abort.abort(); });
    try {
      const input = await body(request);
      if (request.url === '/v1/messages/count_tokens') {
        const parsed = countSchema.safeParse(input);
        if (!parsed.success) { error(response, { status: 400, body: { type: 'error', error: { type: 'invalid_request_error', message: 'Unsupported or invalid native count fields' } } }); return; }
        const result = await counter(profile, parsed.data, abort.signal);
        if (result.ok) json(response, 200, result.value); else error(response, result.error);
        return;
      }
      const parsed = parseRequest(input); if (!parsed.ok) { error(response, parsed.error); return; }
      const started = broker.begin(scope.value, parsed.value); if (!started.ok) { error(response, started.error); return; }
      abort.signal.addEventListener('abort', started.value.cancel, { once: true });
      if (abort.signal.aborted) started.value.cancel();
      if (parsed.value.stream) {
        response.writeHead(200, { 'content-type': 'text/event-stream', 'cache-control': 'no-cache', connection: 'keep-alive' }); response.flushHeaders();
        for await (const event of started.value.events) {
          if (response.destroyed) break;
          response.write(`event: ${String(event['type'])}\ndata: ${JSON.stringify(event)}\n\n`);
        }
        response.end();
      } else {
        const result = await started.value.done;
        if (result.ok) json(response, 200, result.value); else error(response, result.error);
      }
      abort.signal.removeEventListener('abort', started.value.cancel);
    } catch {
      if (!response.headersSent) error(response, { status: 400, body: { type: 'error', error: { type: 'invalid_request_error', message: 'Invalid native request body' } } });
      else response.end();
    }
  }
  return server;
}
export async function loadProfiles(root: string, names: readonly string[]): Promise<ReadonlyMap<string, NativeProfile>> {
  const resolvedRoot = await realpath(root);
  const profiles = await Promise.all(names.map(async name => {
    if (!/^[A-Za-z0-9_-]{1,64}$/.test(name)) throw new Error('Invalid native profile allowlist');
    const configDir = await realpath(join(resolvedRoot, name));
    const inside = (path: string): boolean => { const value = relative(resolvedRoot, path); return value !== '' && value !== '..' && !value.startsWith('../') && !value.startsWith('/'); };
    if (!inside(configDir)) throw new Error('Native profile escaped its root');
    await mkdir(join(configDir, 'home'), { recursive: true, mode: 0o700 });
    const home = await realpath(join(configDir, 'home'));
    if (!inside(home) || dirname(home) !== configDir) throw new Error('Native profile home escaped its directory');
    return [name, { name, configDir, home }] as const;
  }));
  return new Map(profiles);
}
async function main(): Promise<void> {
  const profiles = await loadProfiles(process.env['ANTHROPIC_NATIVE_SDK_ROOT'] ?? '/profiles', (process.env['ANTHROPIC_NATIVE_SDK_PROFILES'] ?? 'default').split(','));
  const port = Number(process.env['PORT'] ?? '4001');
  if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error('Invalid native service port');
  const server = createBrokerServer({ key: process.env['ANTHROPIC_NATIVE_SDK_KEY'] ?? '', profiles });
  server.listen(port, '0.0.0.0');
  for (const signal of ['SIGINT', 'SIGTERM'] as const) process.once(signal, () => { server.close(); server.closeAllConnections(); });
}
if (process.argv[1] === fileURLToPath(import.meta.url)) void main().catch(() => { console.error('Native broker startup failed. Verify service configuration and profile directories'); process.exitCode = 1; });
