# Fedora quota sidecar compatibility

`chatgpt-auxiliary.patch` updates the independently installed quota controller from its September 8, 2026 revision. It includes regression tests and release checksums. Apply it to the operator source and a new release directory, with `operator_attest.py` copied from the operator source before applying the patch

The controller discovers ChatGPT GPT models and `codex-auto-review`, verifies their account identities, and rotates their neutral aliases using the existing weekly usage policy. Image, Realtime, GPT-Live and review aliases never receive the conversational `gpt-reserve` fallback. Their fallbacks remain account-specific deployments of the same model. Existing conversation reserve behavior and usage thresholds remain unchanged

Pause `quota-sidecar.timer` and wait for any active oneshot before changing the release or inventory. Back up Compose, operator source and the signed journal privately. Apply the patch with `patch --batch -p1`, verify `sha256sum -c SHA256SUMS`, and run `python3 -m unittest discover -s test -q`. Point only the sidecar source mount at the new release; the LiteLLM service image does not need to change

New deployments require fresh operator attestations from each running LiteLLM container. Under the journal lock, require ready state with no pending transaction, verify every previous deployment and profile binding against the fresh observations, and allow only the explicitly registered additions. Validate a fresh API snapshot and quota proposal before saving the expanded attestation with the existing journal key. Preserve the policy state, owned reserve entries, incidents and current routing. Never restore old fallback arrays or clear the journal to bypass a conflict

Run the controller once with `--apply` without `--notify`, then run it again and require `noop`, no pending transaction and ready journal state. Resume the timer afterward. These manual verification runs do not send notifications

On September 9, 2026, Fedora Compose switched its source mount to `releases/quota-sidecar-20260909`. Both installed source copies passed 95 tests and their checksum manifests. The live controller applied the four new NAS families and the following run returned `noop`. Backups are under `/home/staticduo/docker/litellm/backups/quota-auxiliary-20260909`. Fedora's LiteLLM image was not changed

Rollback requires reconciling any pending transaction first and preserving the current inventory. Restoring the old controller without updating its attestation would freeze on the added models, and its exhausted-quota policy could add an incompatible reserve route to auxiliary models. Prefer fixing forward while the timer is paused
