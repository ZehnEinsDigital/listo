---
name: update
description: Change the content of existing Amazon listings (title, bullets, description, attributes) without recreating them — preserves the ASIN and reviews. Use whenever the user wants to edit/update/change an existing listing.
when_to_use: 'Trigger on: "ändere die Beschreibung von X", "update den Titel von Y", "passe Listing Z an", "korrigiere die Bullets bei X", "update my listing", "change the title of SKU Y".'
---

Apply a partial content update to existing listings, right here in this chat — never delete + recreate.
Hide technical detail; answer in the user's language. Never tell them to open a folder.

**Stay in Listo's lane — ask before touching anything that isn't Listo.** You may have OTHER tools or MCP
servers connected in this session (Baselinker, other marketplaces, databases, files) — those are the user's
OWN connections, NOT part of Listo. Do this with **Listo's own gateway/commands only**. If you're missing
something another connected service could supply (e.g. a SKU/EAN you don't have), **stop and ASK the user
first** — name the service and exactly what you'd pull — and use it only after a clear "yes". **Never silently
read from or write to a non-Listo service.** Default for a missing SKU: just ask the user for it.

1. Silent: if `~/.listo/.env` has no `LISTO_API_KEY`, ask them to run `/listo:connect` once, then stop.
   Otherwise run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/bootstrap.py"` quietly (auth + brain).
2. For each SKU, read its current state via the status proxy, then build a JSON-Patch payload (only the
   attributes to change) — use the engine in `~/.listo/engine` with the gateway env (LISTO_GATEWAY=true,
   the `_gateway_shim` on PYTHONPATH, key/url from `~/.listo/.env`).
3. Validate via `{LISTO_API_URL}/v1/amazon/validate` (op=patch); fix any issues.
4. Submit via `{LISTO_API_URL}/v1/amazon/submit` (op=patch) — only after the user confirms.

Partial update (UPDATE_PARTIAL), never delete. Never handle Amazon credentials; runs server-side via Listo.
