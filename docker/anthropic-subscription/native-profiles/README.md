# Manual native access snapshots

Fedora owns the Claude native sessions in `~/.claude-homes/staticduo` and `~/.claude-homes/defend1`, each containing `.credentials.json` and `.claude.json`. Run native Claude with that profile's `CLAUDE_CONFIG_DIR` to renew access

Install `export.py` on Fedora at `/home/staticduo/.local/share/claude-native-profiles/export.py`. Keep `export.py` beside `sync.py` on NAS, then manually run `python3 sync.py`. Existing SSH access to `fedora` must be configured. No deployment or SSH configuration is performed by these helpers

The export writes private JSON to stdout only for the SSH pipe. Never run it through a logging command or redirect it to a public file. Sync prints profile names and expiry only. It writes snapshots to `/volume2/docker/litellm/anthropic-native-client/{profile}` with directories `0700` and files `0600`. Mount this directory read-only at `/app/data/anthropic-auth/native-client` in the proxy container

Only accessToken, expiresAt, scopes, optional subscriptionType, and oauthAccount.accountUuid are copied. Refresh tokens, email addresses and other native settings never leave Fedora. Source files and every directory component must be real paths, not symlinks. Access must include user:inference and remain valid for more than 60 seconds. Expired profiles are omitted with a warning so another valid profile can sync independently. Their NAS snapshots stay unchanged and can return provider authentication errors until native Claude runs on Fedora and the profile is synced again. Export fails if no profile remains valid. Malformed sources and unsafe paths always fail. Each file is replaced atomically, the two files and multiple profiles are not a transaction

Run synthetic behavioral tests with `python3 -m unittest discover -s docker/anthropic-subscription/native-profiles -p 'test_*.py'`
