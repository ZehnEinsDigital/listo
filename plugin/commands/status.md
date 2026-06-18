---
description: Check the current Amazon status of a SKU — live issues/errors Amazon reports now
argument-hint: <sku> [credential-id]
---

Show what Amazon currently says about a listing.

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/bootstrap.py"` (auth + brain).
2. GET `{LISTO_API_URL}/v1/amazon/listings/$1/issues?credential_id=<cred>&marketplace=DE`
   with Bearer `LISTO_API_KEY` (read-only proxy — the server calls SP-API with the vaulted creds).
3. Summarize the summaries/issues/offers: what is live, suppressed, or erroring, and why.

This is read-only. Never handle Amazon credentials; the call runs server-side.
