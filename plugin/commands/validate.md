---
description: Validate a built listing/payload against Amazon (server-side VALIDATION_PREVIEW)
argument-hint: <sku or path/to/payload.json>
---

Validate a listing payload without writing to Amazon.

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/bootstrap.py"` (auth + brain).
2. Build (or load) the listing payload for `$1` using the local engine.
3. POST it to `{LISTO_API_URL}/v1/amazon/validate` with Bearer `LISTO_API_KEY`
   (the gateway runs Amazon's VALIDATION_PREVIEW server-side — authoritative, no write).
4. Surface every issue with the engine's MISTAKES guidance; propose concrete fixes.

Note: the local offline check is NOT Amazon's full ruleset — the server VALIDATION_PREVIEW is.
Never call SP-API directly; never handle Amazon credentials.
