---
description: Diagnose why a SKU was rejected/suppressed and propose a fix
argument-hint: <sku> [feed-id]
---

Explain an Amazon problem and fix it, using Listo's accumulated learnings.

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/bootstrap.py"` (auth + brain).
2. Gather evidence (read-only, server-side):
   - just-submitted feed → GET feed processing report,
   - "why is it suppressed now" → the listing's `issues[]` via the status proxy.
3. Reason over the evidence WITH the served MISTAKES + learnings (the brain bundle):
   name the root cause in plain language.
4. Build the corrective patch locally, validate it, and re-submit via the gateway
   (op=patch) after the user confirms.

Never handle Amazon credentials. The reads + the write run server-side via Listo.
