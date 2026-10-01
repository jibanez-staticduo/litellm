import test from 'node:test';
import assert from 'node:assert/strict';
import { once } from 'node:events';
import { mkdtemp, mkdir, symlink, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { Broker, type Generation } from '../src/session.js';
import { Queue, ToolBridge } from '../src/tools.js';
import { createBrokerServer, loadProfiles } from '../src/server.js';
import { createCounter, countSchema } from '../src/counter.js';
import { nativeEnvironment, type EngineEvent, type EngineOptions, type QueryFactory } from '../src/engine.js';
import { parseRequest, sameMessages, controls, type JsonObject, type Message, type NativeProfile, type Request, type Result } from '../src/protocol.js';

const profile: NativeProfile = { name: 'default', configDir: '/profiles/default', home: '/profiles/default/home' };
const profiles = new Map([['default', profile], ['other', { ...profile, name: 'other' }]]);
const scope = { owner: 'alice', profile: 'default', deployment: 'model-one' };
const request = (messages: Message[] = [{ role: 'user', content: 'Hello' }]): Request => ({ model: 'claude-test', max_tokens: 100, messages, system: 'Caller system' });
function value<T>(result: Result<T>): T { assert.equal(result.ok, true, JSON.stringify(result)); if (!result.ok) throw new Error('Unexpected failure'); return result.value; }
function failed<T>(result: Result<T>, status: number): void { assert.equal(result.ok, false); if (!result.ok) assert.equal(result.error.status, status); }
class Fake {
  readonly events = new Queue<EngineEvent>();
  closed = false;
  constructor(readonly options: EngineOptions) {}
  push(event: JsonObject): void { this.events.push({ type: 'stream', event }); }
  close(): void { this.closed = true; this.events.end(); }
  message(blocks: readonly JsonObject[], output = 7, stop = 'end_turn'): void {
    this.push({ type: 'message_start', message: { type: 'message', id: 'native-id', model: this.options.request.model, role: 'assistant', content: [], stop_reason: null, stop_sequence: null, usage: { input_tokens: 13, output_tokens: 0, cache_read_input_tokens: 5 } } });
    blocks.forEach((block, index) => {
      this.push({ type: 'content_block_start', index, content_block: block });
      this.push({ type: 'content_block_stop', index });
    });
    this.push({ type: 'message_delta', delta: { stop_reason: stop, stop_sequence: null }, usage: { output_tokens: output } });
    this.push({ type: 'message_stop' });
  }
}
function setup() {
  const engines: Fake[] = [];
  const factory: QueryFactory = options => { const fake = new Fake(options); engines.push(fake); return { events: fake.events, close: () => fake.close() }; };
  return { engines, factory, broker: new Broker(profiles, factory) };
}
async function response(generation: Generation): Promise<JsonObject> { return value(await generation.done); }
function assistant(message: JsonObject): Message { return { role: 'assistant', content: message['content'] as Message['content'] }; }

test('exact native history, signatures, tool inputs and scoped ownership are required', async () => {
  const { broker, engines } = setup();
  const initial = request(); const generation = value(broker.begin(scope, initial));
  const fake = engines[0]!;
  fake.message([{ type: 'thinking', thinking: 'Reason', signature: 'signed' }, { type: 'text', text: 'Hello back' }]);
  const result = await response(generation);
  const history = [...initial.messages, assistant(result), { role: 'user', content: 'Next' } as const];
  for (const changed of [{ ...scope, owner: 'bob' }, { ...scope, profile: 'other' }, { ...scope, deployment: 'model-two' }]) failed(broker.begin(changed, request(history)), 409);
  failed(broker.begin(scope, { ...request(history), model: 'claude-different' }), 409);
  const tampered = structuredClone(history); (tampered[1]!.content as JsonObject[])[0]!['signature'] = 'forged';
  failed(broker.begin(scope, request(tampered)), 409);
  failed(broker.begin(scope, { ...request(history), max_tokens: 200 }), 409);
  const cached = structuredClone(history); (cached[1]!.content as JsonObject[])[1]!['cache_control'] = { type: 'ephemeral' };
  const continued = value(broker.begin(scope, request(cached)));
  fake.message([{ type: 'text', text: 'Next done' }], 3);
  const next = await response(continued);
  assert.deepEqual(next['usage'], { input_tokens: 13, output_tokens: 3, cache_read_input_tokens: 5 });
  assert.equal(engines.length, 1);
  broker.close();
});

test('parallel identical tools preserve IDs and resolve reversed results, atomically reject duplicates and foreign IDs', async () => {
  const { broker, engines } = setup();
  const tool = { name: 'repeat', input_schema: { type: 'object', properties: { label: { type: 'string' } } } };
  const initial = { ...request(), tools: [tool] };
  const started = value(broker.begin(scope, initial)); const fake = engines[0]!;
  const args = { label: 'same' };
  fake.message(['a', 'b'].map(id => ({ type: 'tool_use', id, name: 'mcp__caller__repeat', input: args })), 9, 'tool_use');
  const generated = await response(started);
  assert.deepEqual((generated['content'] as JsonObject[]).map(block => block['name']), ['repeat', 'repeat']);
  await fake.options.beforeTool('mcp__caller__repeat', 'a', args);
  const first = fake.options.handleTool('mcp__caller__repeat', args, new AbortController().signal);
  await fake.options.beforeTool('mcp__caller__repeat', 'b', args);
  const second = fake.options.handleTool('mcp__caller__repeat', args, new AbortController().signal);
  const turn = (ids: string[]) => ({ ...initial, messages: [...initial.messages, assistant(generated), { role: 'user' as const, content: ids.map(id => ({ type: 'tool_result', tool_use_id: id, content: `result-${id}` })) }] });
  failed(broker.begin(scope, turn(['a', 'a'])), 400);
  failed(broker.begin(scope, turn(['a', 'foreign'])), 409);
  const continued = value(broker.begin(scope, turn(['b', 'a'])));
  assert.deepEqual((await first).content, [{ type: 'text', text: 'result-a' }]);
  assert.deepEqual((await second).content, [{ type: 'text', text: 'result-b' }]);
  fake.message([{ type: 'text', text: 'Both returned' }]); await response(continued);
  failed(broker.begin(scope, turn(['b', 'a'])), 409);
  broker.close();
});

test('cache normalization keeps cache_control in arbitrary tool input meaningful', () => {
  const original: Message[] = [{ role: 'assistant', content: [{ type: 'tool_use', id: 'a', name: 'tool', input: { cache_control: 'caller-value' }, cache_control: { type: 'ephemeral' } }] }];
  const metadata = structuredClone(original); delete (metadata[0]!.content as JsonObject[])[0]!['cache_control'];
  assert.equal(sameMessages(original, metadata), true);
  const changed = structuredClone(metadata); ((changed[0]!.content as JsonObject[])[0]!['input'] as JsonObject)['cache_control'] = 'modified';
  assert.equal(sameMessages(original, changed), false);
  assert.equal(controls({ ...request(), system: [{ type: 'text', text: 'System', cache_control: { type: 'ephemeral' } }] }), controls({ ...request(), system: [{ type: 'text', text: 'System' }] }));
});

test('cancellation and output limit close only the selected native query', async () => {
  const { broker, engines } = setup();
  const first = value(broker.begin(scope, request())); const second = value(broker.begin({ ...scope, owner: 'bob' }, request()));
  first.cancel(); failed(await first.done, 502);
  assert.equal(engines[0]!.closed, true); assert.equal(engines[1]!.closed, false);
  engines[1]!.message([{ type: 'text', text: 'Truncated' }], 100, 'max_tokens');
  const truncated = await response(second); assert.equal(truncated['stop_reason'], 'max_tokens'); assert.equal(engines[1]!.closed, true);
  failed(broker.begin({ ...scope, owner: 'bob' }, request([...request().messages, assistant(truncated), { role: 'user', content: 'Continue' }])), 409);
  broker.close();
});

test('unknown tools cannot be admitted or executed and failure cancels pending lanes', async () => {
  let failures = 0; const bridge = new ToolBridge([], () => { failures++; bridge.cancel(); });
  assert.equal(await bridge.before('Bash', 'id', { command: 'touch /tmp/never' }), false);
  assert.equal(failures, 1);
  const environment = nativeEnvironment(profile);
  assert.equal(environment['ANTHROPIC_API_KEY'], undefined);
  assert.equal(environment['CLAUDE_CODE_OAUTH_TOKEN'], undefined);
  assert.equal(environment['HOME'], profile.home);
});

test('unsupported sampling and forced tools fail explicitly', () => {
  for (const extra of [{ temperature: 0 }, { stop_sequences: ['stop'] }, { tool_choice: { type: 'any' } }, { tool_choice: { type: 'auto', disable_parallel_tool_use: true } }]) failed(parseRequest({ ...request(), ...extra }), 400);
});

test('counter authenticates with native refresh before reading account access, counts arbitrary history and always closes', async () => {
  const calls: string[] = [];
  const submitted = countSchema.parse({ model: 'claude-test', messages: [{ role: 'assistant', content: 'unowned' }, { role: 'user', content: 'arbitrary' }] });
  const counter = createCounter({
    open: selected => { calls.push(`open:${selected.name}`); return { authenticate: async () => { calls.push('refresh'); }, close: () => { calls.push('close'); } }; },
    readAccess: async selected => { calls.push(`read:${selected.name}`); return 'private-access'; },
    count: async (access, payload) => { assert.equal(access, 'private-access'); assert.deepEqual(payload.messages, submitted.messages); calls.push('count'); return payload.messages.length * 11; },
  });
  assert.deepEqual(value(await counter(profiles.get('other')!, submitted, new AbortController().signal)), { input_tokens: 22 });
  assert.deepEqual(calls, ['open:other', 'refresh', 'read:other', 'count', 'close']);
  const failing = createCounter({ open: () => ({ authenticate: async () => { throw new Error('private-access'); }, close: () => { calls.push('closed-failure'); } }), readAccess: async () => 'never', count: async () => 1 });
  const result = await failing(profile, submitted, new AbortController().signal);
  failed(result, 502); assert.equal(JSON.stringify(result).includes('private-access'), false); assert.equal(calls.at(-1), 'closed-failure');
});

test('HTTP authenticates, rejects unknown profiles and returns native SSE events with individual usage', async () => {
  const { factory, engines } = setup();
  const server = createBrokerServer({ key: 'service-private', profiles, factory, counter: async () => ({ ok: true, value: { input_tokens: 17 } }) });
  server.listen(0, '127.0.0.1'); await once(server, 'listening');
  const address = server.address(); assert.ok(address && typeof address !== 'string'); const url = `http://127.0.0.1:${address.port}`;
  const headers = { authorization: 'Bearer service-private', 'content-type': 'application/json', 'x-litellm-native-profile': 'default', 'x-litellm-native-owner': 'alice', 'x-litellm-native-deployment': 'one' };
  try {
    assert.equal((await fetch(`${url}/health/readiness`)).status, 401);
    assert.equal((await fetch(`${url}/health/readiness`, { headers })).status, 200);
    assert.equal((await fetch(`${url}/v1/messages`, { method: 'POST', headers: { ...headers, 'x-litellm-native-profile': '../escape' }, body: JSON.stringify(request()) })).status, 403);
    const streamed = await fetch(`${url}/v1/messages`, { method: 'POST', headers, body: JSON.stringify({ ...request(), stream: true }) });
    const reading = streamed.text();
    engines[0]!.message([{ type: 'text', text: '' }], 4);
    const output = await reading; assert.match(output, /event: message_start/); assert.match(output, /event: message_stop/);
    const data = output.split('\n').filter(line => line.startsWith('data: ')).map(line => JSON.parse(line.slice(6)) as JsonObject);
    const start = data.find(event => event['type'] === 'message_start')!['message'] as JsonObject;
    const delta = data.find(event => event['type'] === 'message_delta')!;
    assert.deepEqual({ ...(start['usage'] as JsonObject), ...(delta['usage'] as JsonObject) }, { input_tokens: 13, output_tokens: 4, cache_read_input_tokens: 5 });
    const counted = await fetch(`${url}/v1/messages/count_tokens`, { method: 'POST', headers, body: JSON.stringify({ model: 'claude-test', messages: [{ role: 'assistant', content: 'arbitrary' }] }) });
    assert.deepEqual(await counted.json(), { input_tokens: 17 });
  } finally { server.close(); server.closeAllConnections(); await once(server, 'close'); }
});

test('profile allowlist rejects directory and HOME symlink escape', async () => {
  const root = await mkdtemp(join(tmpdir(), 'native-profiles-')); const outside = await mkdtemp(join(tmpdir(), 'native-outside-'));
  try {
    await mkdir(join(root, 'default'));
    await symlink(outside, join(root, 'escape'));
    await assert.rejects(loadProfiles(root, ['escape']));
    await symlink(outside, join(root, 'default', 'home'));
    await assert.rejects(loadProfiles(root, ['default']));
    await assert.rejects(loadProfiles(root, ['../escape']));
  } finally { await rm(root, { recursive: true, force: true }); await rm(outside, { recursive: true, force: true }); }
});

test('native deltas preserve text, thinking signature and JSON tool arguments; output limit settles before message_stop', async () => {
  const { broker, engines } = setup();
  const started = value(broker.begin(scope, { ...request(), tools: [{ name: 'repeat', input_schema: { type: 'object' } }] })); const fake = engines[0]!;
  fake.push({ type: 'message_start', message: { id: 'native', type: 'message', role: 'assistant', model: 'claude-test', content: [], usage: { input_tokens: 10, output_tokens: 0 } } });
  fake.push({ type: 'content_block_start', index: 0, content_block: { type: 'thinking', thinking: '', signature: '' } });
  fake.push({ type: 'content_block_delta', index: 0, delta: { type: 'thinking_delta', thinking: 'Think' } });
  fake.push({ type: 'content_block_delta', index: 0, delta: { type: 'signature_delta', signature: 'signed' } });
  fake.push({ type: 'content_block_stop', index: 0 });
  fake.push({ type: 'content_block_start', index: 1, content_block: { type: 'text', text: '' } });
  fake.push({ type: 'content_block_delta', index: 1, delta: { type: 'text_delta', text: 'Partial' } });
  fake.push({ type: 'content_block_stop', index: 1 });
  fake.push({ type: 'content_block_start', index: 2, content_block: { type: 'tool_use', id: 'native-tool', name: 'mcp__caller__repeat', input: {} } });
  fake.push({ type: 'content_block_delta', index: 2, delta: { type: 'input_json_delta', partial_json: '{"label":' } });
  fake.push({ type: 'content_block_delta', index: 2, delta: { type: 'input_json_delta', partial_json: '"same"}' } });
  fake.push({ type: 'content_block_stop', index: 2 });
  fake.push({ type: 'message_delta', delta: { stop_reason: 'max_tokens', stop_sequence: null }, usage: { output_tokens: 100 } });
  const result = await response(started);
  assert.equal(fake.closed, true);
  assert.deepEqual(result['content'], [{ type: 'thinking', thinking: 'Think', signature: 'signed' }, { type: 'text', text: 'Partial' }, { type: 'tool_use', id: 'native-tool', name: 'repeat', input: { label: 'same' } }]);
  assert.deepEqual(result['usage'], { input_tokens: 10, output_tokens: 100 });
  const delivered: JsonObject[] = []; for await (const event of started.events) delivered.push(event);
  assert.equal(delivered.at(-1)!['type'], 'message_stop');
  assert.deepEqual(delivered.find(event => event['type'] === 'content_block_start')!['content_block'], { type: 'thinking', thinking: '', signature: '' });
  broker.close();
});

test('empty tool JSON delta retains native empty arguments and signed thinking through caller continuation', async () => {
  const { broker, engines } = setup();
  const initial: Request = { ...request(), max_tokens: 4096, thinking: { type: 'enabled', budget_tokens: 1024 }, tools: [{ name: 'get_answer', input_schema: { type: 'object', properties: {}, additionalProperties: false } }] };
  const started = value(broker.begin(scope, initial)); const fake = engines[0]!;
  fake.push({ type: 'message_start', message: { id: 'signed-native', type: 'message', role: 'assistant', model: initial.model, content: [], usage: { input_tokens: 10, output_tokens: 0 } } });
  fake.push({ type: 'content_block_start', index: 0, content_block: { type: 'thinking', thinking: '', signature: '' } });
  fake.push({ type: 'content_block_delta', index: 0, delta: { type: 'thinking_delta', thinking: 'Use the caller tool' } });
  fake.push({ type: 'content_block_delta', index: 0, delta: { type: 'signature_delta', signature: 'native-signature' } });
  fake.push({ type: 'content_block_stop', index: 0 });
  fake.push({ type: 'content_block_start', index: 1, content_block: { type: 'tool_use', id: 'native-empty-tool', name: 'mcp__caller__get_answer', input: {} } });
  fake.push({ type: 'content_block_delta', index: 1, delta: { type: 'input_json_delta', partial_json: '' } });
  fake.push({ type: 'content_block_stop', index: 1 });
  fake.push({ type: 'message_delta', delta: { stop_reason: 'tool_use', stop_sequence: null }, usage: { output_tokens: 37 } });
  fake.push({ type: 'message_stop' });
  const first = await response(started);
  assert.deepEqual(first['content'], [{ type: 'thinking', thinking: 'Use the caller tool', signature: 'native-signature' }, { type: 'tool_use', id: 'native-empty-tool', name: 'get_answer', input: {} }]);
  assert.equal(await fake.options.beforeTool('mcp__caller__get_answer', 'native-empty-tool', {}), true);
  const pending = fake.options.handleTool('mcp__caller__get_answer', {}, new AbortController().signal);
  const continued = value(broker.begin(scope, { ...initial, messages: [...initial.messages, assistant(first), { role: 'user', content: [{ type: 'tool_result', tool_use_id: 'native-empty-tool', content: 'VERIFIED' }] }] }));
  assert.deepEqual((await pending).content, [{ type: 'text', text: 'VERIFIED' }]);
  fake.message([{ type: 'text', text: 'VERIFIED' }]);
  assert.deepEqual((await response(continued))['content'], [{ type: 'text', text: 'VERIFIED' }]);
  broker.close();
});
