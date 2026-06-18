---
description: Free-form Amazon catalog / product-type questions
argument-hint: <your question, e.g. "which product type for a leather wallet?">
---

Answer a free-form Amazon question using Listo's read-only catalog proxies + the brain.

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/bootstrap.py"` (auth + brain).
2. Use the server-side read proxies as needed (catalog search by EAN/UPC/ASIN,
   product-type definitions, listing status) — all via `{LISTO_API_URL}` with Bearer
   `LISTO_API_KEY`. Combine with the served learnings/MISTAKES for marketplace-specific nuance.
3. Answer concretely; cite the product type / browse node / attribute when relevant.

Read-only. Never handle Amazon credentials.
