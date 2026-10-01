import { controls, failure, isObject, sameMessages, objectSchema, type JsonObject, type Message, type NativeProfile, type Request, type Result, type Scope } from './protocol.js';
import { Queue, ToolBridge, callerResults } from './tools.js';
import type { Engine, QueryFactory } from './engine.js';

export type Generation = Readonly<{ events: AsyncIterable<JsonObject>; done: Promise<Result<JsonObject>>; cancel: () => void }>;
type Active = Readonly<{ events: Queue<JsonObject>; resolve: (result: Result<JsonObject>) => void }>;

class Session {
  readonly input = new Queue<Message>();
  readonly bridge: ToolBridge;
  readonly fingerprint: string;
  readonly history: Message[] = [];
  readonly engine: Engine;
  active: Active | undefined;
  pendingIds: readonly string[] = [];
  touched = Date.now();
  closed = false;
  private message: JsonObject | undefined;
  private readonly blocks = new Map<number, JsonObject>();
  private readonly inputs = new Map<number, string>();

  constructor(readonly scope: Scope, readonly request: Request, profile: NativeProfile, factory: QueryFactory, private readonly remove: () => void) {
    this.fingerprint = controls(request);
    this.bridge = new ToolBridge(request.tools ?? [], () => this.cancel());
    this.engine = factory({ profile, request, input: this.input, beforeTool: (name, id, args) => this.bridge.before(name, id, args), handleTool: (name, args, signal) => this.bridge.handle(name, args, signal) });
  }

  start(message: Message, initial: boolean): Result<Generation> {
    if (this.closed) return failure(409, 'Native conversation is closed. Start a new conversation');
    if (this.active) return failure(409, 'A generation is already active for this conversation');
    const results = this.pendingIds.length ? callerResults(message.content) : undefined;
    if (results && !results.ok) return results;
    if (!results && typeof message.content !== 'string' && message.content.some(block => block.type === 'tool_result')) return failure(409, 'No tool results are pending for this conversation');
    const events = new Queue<JsonObject>();
    const done = new Promise<Result<JsonObject>>(resolve => { this.active = { events, resolve }; });
    if (results?.ok) {
      const accepted = this.bridge.accept(results.value, this.pendingIds);
      if (!accepted.ok) { this.active = undefined; events.end(); return accepted; }
      this.pendingIds = [];
    }
    this.history.push(message);
    this.touched = Date.now();
    if (!results) this.input.push(message);
    if (initial) void this.read();
    return { ok: true, value: { events, done, cancel: () => this.cancel() } };
  }

  cancel(): void {
    if (this.closed) return;
    this.closed = true;
    this.bridge.cancel(); this.input.end(); this.engine.close(); this.remove();
    const error = failure(502, 'Native conversation failed or was canceled. Start a new conversation', 'api_error');
    if (this.active && !error.ok) { this.active.events.push(error.error.body); this.active.events.end(); this.active.resolve(error); }
    this.active = undefined;
  }

  private async read(): Promise<void> {
    try {
      for await (const item of this.engine.events) {
        if (this.closed) return;
        if (item.type === 'error') { this.cancel(); return; }
        if (!this.consume(item.event)) { this.cancel(); return; }
      }
      this.cancel();
    } catch { this.cancel(); }
  }

  private consume(raw: JsonObject): boolean {
    if (!this.active) return false;
    const type = raw['type'];
    let event = raw;
    if (type === 'message_start') {
      if (this.message || !isObject(raw['message'])) return false;
      this.message = { ...raw['message'] }; this.blocks.clear(); this.inputs.clear();
    } else if (type === 'content_block_start') {
      if (typeof raw['index'] !== 'number' || !isObject(raw['content_block']) || this.blocks.has(raw['index'])) return false;
      const block = raw['content_block'];
      const name = block['type'] === 'tool_use' && typeof block['name'] === 'string' ? this.bridge.externalName(block['name']) : undefined;
      if (block['type'] === 'tool_use' && !name) return false;
      const external = name ? { ...block, name } : { ...block };
      this.blocks.set(raw['index'], { ...external });
      event = { ...raw, content_block: external };
    } else if (type === 'content_block_delta') {
      if (typeof raw['index'] !== 'number' || !isObject(raw['delta'])) return false;
      const block = this.blocks.get(raw['index']); const delta = raw['delta'];
      if (!block) return false;
      if (delta['type'] === 'input_json_delta' && typeof delta['partial_json'] === 'string') this.inputs.set(raw['index'], (this.inputs.get(raw['index']) ?? '') + delta['partial_json']);
      else if (delta['type'] === 'text_delta' && typeof delta['text'] === 'string') block['text'] = String(block['text'] ?? '') + delta['text'];
      else if (delta['type'] === 'thinking_delta' && typeof delta['thinking'] === 'string') block['thinking'] = String(block['thinking'] ?? '') + delta['thinking'];
      else if (delta['type'] === 'signature_delta' && typeof delta['signature'] === 'string') block['signature'] = String(block['signature'] ?? '') + delta['signature'];
      else return false;
    } else if (type === 'content_block_stop') {
      if (typeof raw['index'] !== 'number') return false;
      const block = this.blocks.get(raw['index']); if (!block) return false;
      const partial = this.inputs.get(raw['index']);
      if (partial !== undefined && partial !== '') block['input'] = objectSchema.parse(JSON.parse(partial));
      if (block['type'] === 'tool_use') {
        if (typeof block['id'] !== 'string' || typeof block['name'] !== 'string' || !isObject(block['input'])) return false;
        if (!this.bridge.register(block['id'], `mcp__caller__${block['name']}`, block['input'])) return false;
      }
    } else if (type === 'message_delta') {
      if (!this.message || !isObject(raw['delta']) || !isObject(raw['usage'])) return false;
      const usage = isObject(this.message['usage']) ? this.message['usage'] : {};
      this.message = { ...this.message, ...raw['delta'], usage: { ...usage, ...raw['usage'] } };
      if (raw['delta']['stop_reason'] === 'max_tokens') {
        this.active.events.push(event);
        const finished = this.consume({ type: 'message_stop' });
        this.cancel();
        return finished;
      }
    } else if (type === 'message_stop') {
      if (!this.message) return false;
      const content = [...this.blocks.entries()].sort(([left], [right]) => left - right).map(([, block]) => block);
      const message: JsonObject = { ...this.message, content };
      this.pendingIds = content.filter(block => block['type'] === 'tool_use').map(block => String(block['id']));
      this.history.push({ role: 'assistant', content: content.map(block => ({ ...block, type: String(block['type']) })) });
      this.active.events.push(event); this.active.events.end(); this.active.resolve({ ok: true, value: message });
      this.active = undefined; this.message = undefined; this.touched = Date.now();
      if (message['stop_reason'] === 'max_tokens') this.cancel();
      return true;
    } else if (type !== 'ping') return false;
    this.active.events.push(event);
    return true;
  }
}

export class Broker {
  private readonly sessions = new Set<Session>();
  constructor(private readonly profiles: ReadonlyMap<string, NativeProfile>, private readonly factory: QueryFactory, private readonly capacity = 128, private readonly idleMs = 1800000) {}

  begin(scope: Scope, request: Request): Result<Generation> {
    const profile = this.profiles.get(scope.profile);
    if (!profile) return failure(403, 'Native profile is not allowed', 'permission_error');
    for (const session of this.sessions) if (!session.active && Date.now() - session.touched > this.idleMs) session.cancel();
    const prefix = request.messages.slice(0, -1); const last = request.messages.at(-1);
    if (!last || last.role !== 'user') return failure(400, 'A Messages request must end with a user turn');
    const candidates = [...this.sessions].filter(session => session.scope.owner === scope.owner && session.scope.profile === scope.profile && session.scope.deployment === scope.deployment && session.request.model === request.model && sameMessages(session.history, prefix));
    if (candidates.length > 1) return failure(409, 'Conversation history is ambiguous. Start a distinct conversation');
    const existing = candidates[0];
    if (existing) {
      if (existing.fingerprint !== controls(request)) return failure(409, 'Native conversation controls changed. Start a new conversation');
      return existing.start(last, false);
    }
    if (prefix.length) return failure(409, 'History is not owned by this native conversation. Start with one user message');
    if (this.sessions.size >= this.capacity) return failure(429, 'Native conversation capacity reached', 'rate_limit_error');
    try {
      const session = new Session(scope, request, profile, this.factory, () => this.sessions.delete(session));
      this.sessions.add(session);
      const result = session.start(last, true);
      if (!result.ok) session.cancel();
      return result;
    } catch { return failure(502, 'Native engine initialization failed', 'api_error'); }
  }

  close(): void { for (const session of this.sessions) session.cancel(); }
}
