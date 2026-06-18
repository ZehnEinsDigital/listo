---
description: Content-update specific SKUs (partial update; preserves the ASIN/reviews)
argument-hint: <sku[,sku2,...]> <what to change>
---

Apply a partial content update to existing listings — never delete+recreate.

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/bootstrap.py"` (auth + brain).
2. For each SKU in `$1`, read its current state via the status proxy, then build a
   JSON-Patch payload locally with the engine (only the attributes to change).
3. Validate via `{LISTO_API_URL}/v1/amazon/validate` (op=patch), fix issues.
4. Submit via `{LISTO_API_URL}/v1/amazon/submit` (op=patch) — server decides dry-run/live.

Patch (UPDATE_PARTIAL on the wire), never delete. Never handle Amazon credentials.
