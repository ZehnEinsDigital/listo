---
name: diagnose
description: Find out why an Amazon SKU/listing was rejected, suppressed, errored, or isn't showing — and fix it. Use whenever the user asks why a listing failed/is suppressed/has errors/isn't live and wants it sorted.
when_to_use: 'Trigger on: "warum wurde X abgelehnt", "warum ist mein Listing unterdrückt", "SKU Y wird nicht angezeigt", "warum hat Amazon das geblockt", "fix my rejected listing", "why was my SKU rejected".'
---

Help the user fix an Amazon problem, in plain language, right here in this chat. Hide technical detail
(no "gateway", "bootstrap", paths). Answer in the user's language. Never tell them to open a folder.

1. Silent: if `~/.listo/.env` has no `LISTO_API_KEY`, ask them to run `/listo:connect` once, then stop.
   Otherwise run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/bootstrap.py"` quietly (auth + brain).
2. Gather evidence server-side (read-only): the feed processing report for a just-submitted feed, and/or
   the listing's `issues[]` via `{LISTO_API_URL}/v1/amazon/listings/<sku>/issues` (Bearer `LISTO_API_KEY`).
3. Reason over it WITH Listo's served MISTAKES + learnings (the brain) and name the root cause in plain words.
4. Build the corrective patch, validate it, and re-submit (op=patch) via the cloud — ONLY after the user confirms.

Never handle Amazon credentials; all reads/writes run server-side via Listo.
