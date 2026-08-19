# Deployment Attempts And Mandatory Stop

## Attempt 1

- Exact candidate selector installed and only `litellm` recreated with `--no-deps`
- Candidate reached container startup, then the harness rejected a blank trailing line from `litellm --version`
- Automated rollback restored NAS 1.92.0 plus the protected wrapper/Compose pair
- Fedora was immediately reverse-rolled back to its pre-release digest under the split-state rule

## Attempt 2

- Stopped before recreation because rollback restoration had changed live operational-file ownership to root, and the atomic image-selector writer rejected the ownership transition
- No candidate service was deployed in this attempt
- The protected temporary `.env` file was removed and live ownership/modes were restored to `1000:10` / 0777

## Attempt 3

- Fresh T0 passed and only NAS `litellm` was recreated by the exact candidate reference
- Candidate reached startup, then the harness compared the running Docker config ID against the manifest digest and rejected it
- Independent readback proved the expected distinct identities: manifest `42d365...115b`, config ID `45a019...c73`
- Automated rollback again restored NAS 1.92.0 and the exact protected wrapper/Compose pair

After three bounded attempts, no further deployment was made. Candidate Responses, Codex, and LazyMCP tests were not run after the mandatory stop

Result: **REJECT AND ESCALATE**
