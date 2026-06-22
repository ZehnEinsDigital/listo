---
name: status
description: Check the current Amazon status of a SKU/listing — what's live, suppressed, or erroring right now. Use whenever the user asks about the state of a listing or whether a SKU is online.
when_to_use: 'Trigger on: "status von SKU X", "ist mein Listing live", "was sagt Amazon zu Y", "läuft mein Produkt schon", "is my listing live", "check my SKU".'
---

Tell the user what Amazon currently says about a listing, in plain language, right here. Hide technical
detail; answer in the user's language. Never tell them to open a folder.

1. Silent: if `~/.listo/.env` has no `LISTO_API_KEY`, ask them to run `/listo:connect` once, then stop.
   Otherwise run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/bootstrap.py"` quietly (auth + brain).
2. GET `{LISTO_API_URL}/v1/amazon/listings/<sku>/issues?marketplace=DE` with Bearer `LISTO_API_KEY`
   (read-only proxy — the server calls SP-API with the vaulted creds).
3. Summarize in plain words: what is live, suppressed, or erroring — and why.

Read-only. Never handle Amazon credentials; the call runs server-side via Listo.
