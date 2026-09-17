# ChatGPT GPT-Live

The proxy exposes the public GPT-Live session routes and retains the Codex-compatible `POST /live` route. Clients authenticate to LiteLLM with their LiteLLM key. The selected deployment supplies the upstream credentials: the `chatgpt` provider uses its configured ChatGPT OAuth profile, while the `openai` provider uses its configured OpenAI API key. Do not send an upstream OAuth token as the proxy key

## Configure a deployment

The existing Codex model alias can keep its OAuth configuration:

```yaml
model_list:
  - model_name: gpt-live-1-codex
    litellm_params:
      model: chatgpt/gpt-live-1-codex
      chatgpt_auth_profile: account1
```

Use an OAuth profile already configured on the proxy. For a deployment using the public OpenAI API instead, configure `model: openai/gpt-live-1` and `api_key: os.environ/OPENAI_API_KEY` under its own model alias. The public API documentation uses `gpt-live-1`; the Codex alias and its backend capabilities are separate

## Public Live routes

Use the proxy host in place of `api.openai.com`. Send the configured LiteLLM alias in `session.model` when creating a session, or in the first `session.start` event for a primary WebSocket. Keep the returned session ID unchanged for subsequent operations

| Method | Path | Request and response |
| --- | --- | --- |
| POST | `/v1/live/sessions` | JSON `session` and `transport: {type: "webrtc", sdp: "<offer>"}`; returns 201 JSON with `session.id` and `transport.sdp` |
| POST | `/v1/live/sessions/{session_id}/fork` | JSON WebRTC `transport` and optional `session` overrides; returns 200 JSON with the new session ID and SDP answer |
| GET | `/v1/live/sessions/{session_id}/content` | Downloads stored recording content without converting it to JSON |
| POST | `/v1/live/sessions/{session_id}/accept` | JSON `session` with `type: "live"` and model; successful SIP acceptance returns an empty body |
| POST | `/v1/live/sessions/{session_id}/reject` | JSON with required integer `status_code` from 300 through 699 |
| POST | `/v1/live/sessions/{session_id}/refer` | JSON with `target_uri` for the SIP destination |
| POST | `/v1/live/sessions/{session_id}/hangup` | No request body |
| WebSocket | `/v1/live/sessions` | Start with `session.start`, then wait for `session.started` before sending audio or commands |
| WebSocket | `/v1/live/sessions/{session_id}/attach` | Attach to an existing session; do not send `session.start` or input audio |
| WebSocket | `/v1/live/sessions/{session_id}/fork` | Start with `session.start` and a required `session` overrides object, which may be empty |

Public WebRTC creation uses JSON, not the multipart or raw SDP formats used by the Codex compatibility route. `POST /live` and its existing aliases remain available for Codex clients using that format. WebRTC audio travels on media tracks; its data channel carries Live JSON events. Primary WebSocket audio uses base64 chunks in `session.input_audio.append` and `session.output_audio.delta`

The proxy preserves Live event payloads, including nested Responses events inside `response.event`, rather than translating them into Realtime events. Session routing rewrites the configured model alias to the selected upstream model. Audio, transcript, delegation and usage events retain their upstream format. Send `session.close` and wait for `session.closed` to obtain final usage; a disconnected socket alone does not confirm successful finalization

## Availability and verification

Route support does not establish that every configured backend or account supports every operation. The official API describes project API-key authentication; it does not guarantee equivalent capabilities for ChatGPT OAuth. An OAuth request reaching SDP validation proves only that the request reached that validation step. It does not prove a working audio session, recording, fork or SIP call. The routes listed here have not all been tested against a real upstream service

Session controls require a session known to the proxy and owned by the authenticated caller. Incoming SIP calls originate upstream. A proxy administrator can accept or reject the raw ID from a verified incoming-call webhook by supplying `x-litellm-live-model` with an alias that resolves to exactly one deployment. Successful acceptance returns the proxy-owned handle in `x-litellm-live-session-id`, preserving the API's empty response body. Use that handle for subsequent controls. Ordinary virtual keys cannot enroll arbitrary upstream session IDs; a trusted webhook-to-owner enrollment flow is still required for those keys

Live duration uses cumulative `usage.seconds`; legacy Codex milliseconds remain supported. WebRTC initialization has a 15-second minimum credited against running duration, not added to it. Nested terminal Responses usage is charged separately using its backend model and deduplicated by response ID. A failed observation connection cannot establish complete usage. Managed delegation also depends on receiving its backend usage events; the upstream sideband does not replay events emitted before attachment

Managed Responses delegation authorizes its backend model as well as the voice model. Use client delegation when budgets or request/token limits apply to the key, user, team, project, organization, team member, end user, or a model access group, since each backend invocation needs its own admission check. Keys scoped to access groups, projects, users, organizations, or teams are treated as model-restricted even if the key's own model list is empty. Managed WebRTC sessions with model restrictions must explicitly exclude `session.update` and wildcard events from frontend client events. That data channel connects directly to OpenAI and could otherwise change the backend model outside the proxy's checks. Client delegation does not need this restriction: the delegation type cannot change after startup or on a fork. Sparse sideband updates may omit the backend model to retain its current value

For both HTTP and WebSocket forks of managed sessions, restricted-model keys must explicitly provide an authorized `session.delegation.responses.model`. Empty overrides cannot safely authorize an inherited managed backend: the session handle records startup configuration, while later updates may have changed the upstream model. Client-delegation forks can use empty overrides because the delegation type is immutable

See the official [Live overview](https://developers.openai.com/api/docs/guides/live), [Live API reference](https://developers.openai.com/api/reference/resources/live), [session management](https://developers.openai.com/api/docs/guides/live-conversations), [WebRTC guide](https://developers.openai.com/api/docs/guides/voice-webrtc?api=live), [WebSocket guide](https://developers.openai.com/api/docs/guides/voice-websockets?api=live), [server controls](https://developers.openai.com/api/docs/guides/voice-server-controls?api=live) and [SIP guide](https://developers.openai.com/api/docs/guides/voice-sip?api=live) for the upstream contract. The voice guides also contain Realtime tabs with different routes and formats
