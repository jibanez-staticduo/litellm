# Bounded Fallback Verification

- Probe window: `2026-08-19T08:36:19Z` through `2026-08-19T08:36:23Z`
- Requests sent: exactly 1
- Model: unqualified `gpt-5.6-sol`
- Controls: `store=false`, client retries 0, one provider-valid Responses request, streaming enabled
- Request and response content retained: none
- HTTP result: 200
- Failed/error SSE events: 0
- Terminal selected group: `chatgpt-account2/gpt-5.6-sol`
- Terminal deployment ID retained: no; one-way hash prefix `a015937e9f4b` used only to correlate the known account2 deployment

Final readback proves the public alias itself is account1-associated and its sole general fallback is matching account2. Terminal account2 selection on an HTTP 200 public request therefore proves advancement under the natural account1 failure/quota disposition without credential, profile, retry, cooldown, deployment, or source mutation

The bounded default container log window did not emit sanitized routing-attempt lines or a rate-limit line, so attempt ordering relies on structural live/persistent state plus terminal account2 correlation rather than a content-bearing raw log. No additional probe was sent
