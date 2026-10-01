import { canonical, failure, isObject, objectSchema, type JsonObject, type Result, type ToolDefinition } from './protocol.js';
import { z } from 'zod';
import type { ExternalResult } from './engine.js';

export class Queue<T> implements AsyncIterable<T> {
  private readonly values: T[] = [];
  private waiter: ((value: IteratorResult<T>) => void) | undefined;
  private closed = false;

  push(value: T): void {
    if (this.closed) return;
    if (this.waiter) { const waiter = this.waiter; this.waiter = undefined; waiter({ done: false, value }); return; }
    this.values.push(value);
  }

  end(): void {
    this.closed = true;
    this.waiter?.({ done: true, value: undefined });
    this.waiter = undefined;
  }

  [Symbol.asyncIterator](): AsyncIterator<T> {
    return { next: async () => {
      const value = this.values.shift();
      if (value !== undefined) return { done: false, value };
      if (this.closed) return { done: true, value: undefined };
      return new Promise<IteratorResult<T>>(resolve => { this.waiter = resolve; });
    } };
  }
}

type Admission = Readonly<{ id: string; args: JsonObject; release: () => void }>;
type Expected = Readonly<{ name: string; args: JsonObject }>;
export type CallerResult = Readonly<{ id: string; result: ExternalResult }>;

export class ToolBridge {
  private readonly names: ReadonlyMap<string, string>;
  private readonly lanes = new Map<string, Promise<void>>();
  private readonly admissions = new Map<string, Admission>();
  private readonly hooks = new Set<string>();
  private readonly expected = new Map<string, Expected>();
  private readonly results = new Map<string, ExternalResult>();
  private readonly pending = new Map<string, (result: ExternalResult) => void>();
  private closed = false;

  constructor(tools: readonly ToolDefinition[], private readonly fail: () => void) {
    this.names = new Map(tools.map(tool => [`mcp__caller__${tool.name}`, tool.name]));
  }

  externalName(native: string): string | undefined { return this.names.get(native); }

  register(id: string, name: string, args: JsonObject): boolean {
    if (!this.names.has(name) || this.expected.has(id)) return false;
    this.expected.set(id, { name, args });
    return true;
  }

  async before(name: string, id: string, args: JsonObject): Promise<boolean> {
    if (this.closed || !this.names.has(name) || this.hooks.has(id)) { this.fail(); return false; }
    this.hooks.add(id);
    const previous = this.lanes.get(name) ?? Promise.resolve();
    let release: () => void = () => {};
    const consumed = new Promise<void>(resolve => { release = resolve; });
    this.lanes.set(name, previous.then(() => consumed));
    await previous;
    if (this.closed) { release(); return false; }
    if (this.admissions.has(name)) { release(); this.fail(); return false; }
    this.admissions.set(name, { id, args, release });
    return true;
  }

  async handle(name: string, args: JsonObject, signal: AbortSignal): Promise<ExternalResult> {
    const admission = this.admissions.get(name);
    if (!admission || canonical(admission.args) !== canonical(args) || this.closed) {
      this.fail();
      return { content: [{ type: 'text', text: 'Caller tool admission failed' }], isError: true };
    }
    this.admissions.delete(name);
    const response = new Promise<ExternalResult>(resolve => {
      const ready = this.results.get(admission.id);
      if (ready) { resolve(ready); return; }
      this.pending.set(admission.id, resolve);
    });
    admission.release();
    const canceled = (): void => this.fail();
    signal.addEventListener('abort', canceled, { once: true });
    if (signal.aborted) canceled();
    try { return await response; } finally { signal.removeEventListener('abort', canceled); }
  }

  accept(results: readonly CallerResult[], expectedIds: readonly string[]): Result<undefined> {
    const ids = results.map(result => result.id);
    if (new Set(ids).size !== ids.length) return failure(400, 'Duplicate tool_result IDs are not allowed');
    if (ids.length !== expectedIds.length || ids.some(id => !expectedIds.includes(id))) return failure(409, 'Tool results must match every pending tool_use ID from this conversation');
    if (ids.some(id => !this.expected.has(id) || this.results.has(id))) return failure(409, 'Tool_result ID is foreign or already completed');
    for (const result of results) this.results.set(result.id, result.result);
    for (const result of results) { this.pending.get(result.id)?.(result.result); this.pending.delete(result.id); }
    return { ok: true, value: undefined };
  }

  cancel(): void {
    this.closed = true;
    for (const admission of this.admissions.values()) admission.release();
    this.admissions.clear();
    for (const resolve of this.pending.values()) resolve({ content: [{ type: 'text', text: 'Native conversation canceled' }], isError: true });
    this.pending.clear();
  }
}

export function callerResults(content: string | readonly JsonObject[]): Result<readonly CallerResult[]> {
  if (typeof content === 'string' || content.length === 0 || content.some(block => block['type'] !== 'tool_result')) return failure(400, 'Pending tool continuation requires tool_result blocks only');
  const output: CallerResult[] = [];
  for (const block of content) {
    if (typeof block['tool_use_id'] !== 'string') return failure(400, 'Every tool_result requires its native tool_use_id');
    const value = block['content'] ?? '';
    const blocks = typeof value === 'string' ? [{ type: 'text', text: value }] : value;
    const parsed = z.array(objectSchema).safeParse(blocks);
    if (!parsed.success) return failure(400, 'Tool_result content must contain text or base64 image blocks');
    const transformed: JsonObject[] = [];
    for (const item of parsed.data) {
      if (item['type'] === 'text' && typeof item['text'] === 'string') { transformed.push(item); continue; }
      if (item['type'] === 'image' && isObject(item['source']) && item['source']['type'] === 'base64' && typeof item['source']['data'] === 'string' && typeof item['source']['media_type'] === 'string') {
        transformed.push({ type: 'image', data: item['source']['data'], mimeType: item['source']['media_type'] });
        continue;
      }
      return failure(400, 'Tool_result content supports text and base64 images only');
    }
    if (block['is_error'] !== undefined && typeof block['is_error'] !== 'boolean') return failure(400, 'tool_result.is_error must be boolean');
    output.push({ id: block['tool_use_id'], result: { content: transformed, isError: block['is_error'] === true } });
  }
  return { ok: true, value: output };
}
