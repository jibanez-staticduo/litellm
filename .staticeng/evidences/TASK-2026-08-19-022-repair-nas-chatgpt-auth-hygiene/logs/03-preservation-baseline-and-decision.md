# Preservation, Fresh Baseline, And Deployment Decision

## Runtime And Topology

- NAS image remained `docker.staticduo.com/litellm:rollback-nas-1.92.0-20260818`
- NAS image ID remained `sha256:8ae33df6e1c13eaaca70ce179d4a724507a481ebcf4019be88182aa030b07afa`
- Container start remained `2026-08-18T17:10:37.602506412Z`, restart count 0, OOM false, status running, health healthy
- In-container readiness and liveliness returned HTTP 200
- Model count remained 40: nine public GPT rows, eight account2-qualified rows, eight account3-qualified rows, and eight default-qualified rows
- Router settings remained 16 fallback rules with `simple-shuffle`; the eight scoped public GPT fallback rows and all three profile target families remain registered
- No model, deployment, fallback, database, Compose, wrapper, tag, or route was changed

Fedora remained healthy on candidate digest `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`, restart count 0, and OOM false

Two independent read-only lookups for `docker.staticduo.com/litellm:stable` returned not found. The task made no registry mutation, but the prior stable digest `sha256:b52c0949442e8855289df706621725670d1cff28738a277c245b273b388873e0` could not be re-established at this gate

## Just-In-Time Metadata Baseline

Captured at `2026-08-18T23:52:10Z`

- Token directory: regular non-symlink directory, owner `0:0`, mode `0700`, device `64769`, inode `113449098`, mtime/ctime `1787096921`
- Exact entry count: 10 regular non-symlink files
- All entries: owner `0:0`, mode `0600`
- Non-empty entry count: 7; empty approved lock count: 3
- `auth.json`: size 3823, mtime `1787095139`, ctime `1787095139`, inode `113462982`
- `account2.json`: size 4051, mtime `1787095139`, ctime `1787095139`, inode `113462903`
- `account3.json`: size 3855, mtime `1787096921`, ctime `1787096921`, inode `113462912`
- Historical files retained: four, all non-empty, regular, non-symlink, owner `0:0`, mode `0600`
- Lock files retained: three, all empty, regular, non-symlink, owner `0:0`, mode `0600`

This baseline is structurally safe for a later comparison, but it is not an authorization baseline because account3 is invalid and production independently re-entered device authentication. The account3 change since the earlier inspection was positively correlated with another device-auth marker write and remains a mandatory deployment rejection event

## Decision

**REJECT NAS DEPLOYMENT**

Permissions and two profiles are repaired, and topology/runtime preservation passed. Deployment cannot resume because account3 refresh is provider-rejected, account3 production traffic has an active interactive-auth lock, the required account3 direct check cannot pass safely, and the stable tag could not be resolved
