# Routing Change And Readback

## Transaction

- Transaction count assertion: exactly 5 targets
- Updated count assertion: exactly 5
- Post-clear assertion: zero target rows retain `chatgpt_auth_profile`
- Inventory assertion: 27 before and after
- Protected non-target fingerprint: `e601f1c9b810aae7141bc977b9ad693b` before and after
- Sol mutation: none
- Qualified deployment mutation: none
- Transaction result: committed

The protected fingerprint covered every model row's identity, alias, all deployment parameters except the authorized field, model metadata, and blocked state in deterministic identity order. Any mismatch raised inside the transaction and would have rolled it back. An initial dry attempt selected zero because it asserted plaintext provider-model values against encrypted storage; PostgreSQL rolled that transaction back automatically before any update. The final transaction removed that invalid predicate while retaining exact aliases, bound row identities, exact before-values, qualified-route assertions, Sol assertion, and non-target fingerprint protection

## Supported Fallback Writes

Exactly six `POST /fallback` writes returned HTTP 200, in this order:

1. `gpt-5.4 -> chatgpt-account2/gpt-5.4`
2. `gpt-5.4-mini -> chatgpt-account2/gpt-5.4-mini`
3. `gpt-5.5 -> chatgpt-account2/gpt-5.5`
4. `gpt-5.6-luna -> chatgpt-account2/gpt-5.6-luna`
5. `gpt-5.6-sol -> chatgpt-account2/gpt-5.6-sol`
6. `gpt-5.6-terra -> chatgpt-account2/gpt-5.6-terra`

## Final Readback

- Public absent-profile account1 associations: 6 of 6
- Qualified account1 absent-profile records: 6 of 6
- Qualified account2 profile-associated records: 6 of 6
- Persistent fallback GETs: six HTTP 200 responses with exact account2 targets
- Live router: six exact account2 public fallback rules
- Inventory: 27
- Router retry, failure, cooldown, strategy, and cross-profile policy: unchanged
- Image: unchanged immutable digest
- Restart count: 0
- Source, containers, clients, NAS, and non-Fedora state: untouched
