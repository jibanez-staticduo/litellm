import { z } from 'zod';

export type Json = null | boolean | number | string | Json[] | { [key: string]: Json };
export type JsonObject = { [key: string]: Json };
export const jsonSchema: z.ZodType<Json> = z.json();
export const objectSchema = z.record(z.string(), jsonSchema);
const blockSchema = z.intersection(objectSchema, z.object({ type: z.string() }));
const messageSchema = z.object({
  role: z.enum(['user', 'assistant']),
  content: z.union([z.string(), z.array(blockSchema)]),
}).strict();
const toolSchema = z.object({
  type: z.literal('custom').optional(),
  name: z.string().regex(/^[A-Za-z0-9_-]{1,64}$/),
  description: z.string().optional(),
  input_schema: objectSchema,
  cache_control: objectSchema.optional(),
}).strict();
const thinkingSchema = z.discriminatedUnion('type', [
  z.object({ type: z.literal('enabled'), budget_tokens: z.number().int().positive(), display: z.enum(['summarized', 'omitted']).optional() }).strict(),
  z.object({ type: z.literal('adaptive'), display: z.enum(['summarized', 'omitted']).optional() }).strict(),
  z.object({ type: z.literal('disabled') }).strict(),
]);
export const requestSchema = z.object({
  model: z.string().regex(/^claude-[A-Za-z0-9_.-]+$/),
  max_tokens: z.number().int().positive(),
  messages: z.array(messageSchema).min(1),
  system: z.union([z.string(), z.array(z.object({ type: z.literal('text'), text: z.string(), cache_control: objectSchema.optional() }).strict())]).optional(),
  tools: z.array(toolSchema).optional(),
  stream: z.boolean().optional(),
  thinking: thinkingSchema.optional(),
  tool_choice: z.object({ type: z.literal('auto'), disable_parallel_tool_use: z.literal(false).optional() }).strict().optional(),
  output_config: z.object({ effort: z.enum(['low', 'medium', 'high', 'xhigh', 'max']).optional() }).strict().optional(),
}).strict();
export type Message = z.infer<typeof messageSchema>;
export type ToolDefinition = z.infer<typeof toolSchema>;
export type Request = z.infer<typeof requestSchema>;
export type Scope = Readonly<{ owner: string; profile: string; deployment: string }>;
export type NativeProfile = Readonly<{ name: string; configDir: string; home: string }>;
export type PublicError = Readonly<{ status: number; body: JsonObject }>;
export type Result<T> = Readonly<{ ok: true; value: T }> | Readonly<{ ok: false; error: PublicError }>;

export function failure(status: number, message: string, type = 'invalid_request_error'): Result<never> {
  return { ok: false, error: { status, body: { type: 'error', error: { type, message } } } };
}

export function canonical(value: Json): string {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value !== null && typeof value === 'object') {
    return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical(value[key] ?? null)}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

export function isObject(value: Json | undefined): value is JsonObject {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

export function parseRequest(input: unknown): Result<Request> {
  const parsed = requestSchema.safeParse(input);
  if (!parsed.success) {
    const issues = parsed.error.issues.flatMap(issue => {
      const paths = issue.code === 'unrecognized_keys' ? issue.keys.map(key => [...issue.path, key]) : [issue.path];
      return paths.map(path => `${path.map(part => String(part)).join('.') || '$'} (${issue.code})`);
    }).slice(0, 12);
    return failure(400, `Unsupported or invalid Messages fields: ${issues.join(', ')}. Native controls support max_tokens, thinking, output_config.effort and automatic tool_choice only`);
  }
  const tools = parsed.data.tools ?? [];
  if (new Set(tools.map(tool => tool.name)).size !== tools.length) return failure(400, 'Tool names must be unique');
  if (tools.some(tool => tool.input_schema['type'] !== 'object')) return failure(400, 'Tool input_schema must describe an object');
  if (parsed.data.thinking?.type === 'enabled' && parsed.data.thinking.budget_tokens >= parsed.data.max_tokens) return failure(400, 'thinking.budget_tokens must be lower than max_tokens');
  return { ok: true, value: parsed.data };
}

export function scopeFromHeaders(headers: Readonly<Record<string, string | string[] | undefined>>): Result<Scope> {
  const owner = headers['x-litellm-native-owner'];
  const profile = headers['x-litellm-native-profile'];
  const deployment = headers['x-litellm-native-deployment'];
  const valid = (value: string | string[] | undefined): value is string => typeof value === 'string' && /^[!-~]{1,256}$/.test(value);
  if (!valid(owner) || !valid(profile) || !valid(deployment)) return failure(400, 'Trusted profile, owner and deployment headers are required');
  return { ok: true, value: { owner, profile, deployment } };
}

export function controls(request: Request): string {
  return canonical(controlValues(request));
}

function controlValues(request: Request): JsonObject {
  return objectSchema.parse(normalizeControls(toJson({
    model: request.model,
    max_tokens: request.max_tokens,
    system: request.system ?? '',
    tools: request.tools ?? [],
    thinking: request.thinking ?? null,
    output_config: request.output_config ?? null,
    tool_choice: request.tool_choice ?? null,
  })));
}

export function changedControls(original: Request, incoming: Request): readonly string[] {
  const before = controlValues(original);
  const after = controlValues(incoming);
  const fields = ['model', 'max_tokens', 'system', 'tools', 'thinking', 'output_config', 'tool_choice'] as const;
  return fields.filter(field => canonical(before[field] ?? null) !== canonical(after[field] ?? null));
}

export function sameMessages(left: readonly Message[], right: readonly Message[]): boolean {
  return canonical(toJson(left.map(normalizeMessage))) === canonical(toJson(right.map(normalizeMessage)));
}

export function toJson(value: unknown): Json { return jsonSchema.parse(JSON.parse(JSON.stringify(value))); }

function normalizeBlock(block: JsonObject): JsonObject {
  return Object.fromEntries(Object.entries(block).filter(([key]) => key !== 'cache_control').map(([key, value]) => {
    if (key === 'content' && block['type'] === 'tool_result' && Array.isArray(value)) {
      return [key, value.map(item => isObject(item) ? normalizeBlock(item) : item)];
    }
    return [key, value];
  }));
}

function normalizeMessage(message: Message): Message {
  return { ...message, content: typeof message.content === 'string' ? message.content : message.content.map(block => ({ ...normalizeBlock(block), type: block.type })) };
}

function normalizeControls(value: Json): Json {
  if (!isObject(value)) return value;
  return { ...value,
    system: Array.isArray(value['system']) ? value['system'].map(block => isObject(block) ? normalizeBlock(block) : block) : value['system'] ?? '',
    tools: Array.isArray(value['tools']) ? value['tools'].map(block => isObject(block) ? normalizeBlock(block) : block) : [],
  };
}
