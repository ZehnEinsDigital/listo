---
description: Teach Listo a correction so it improves next time (submitted as a review candidate)
argument-hint: "<what was wrong + the right way to do it>"
---

Capture a correction the user made (e.g. "you missed the variant families", "material X should map to Y",
"GPSR needs the responsible person's name") as a **learning candidate** so it can improve the brain after
review. It does NOT take effect immediately — the Listo team promotes good candidates into the master.

1. If not connected yet, run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/bootstrap.py"` first.
2. Distil the correction into a **general, reusable rule** (no customer PII, no product data, no prices):
   - `marketplace` (e.g. `amazon`)
   - `category` (e.g. `variants`, `mapping`, `gpsr`)
   - `problem` — what went wrong / the trap
   - `solution` — the rule to apply next time
   - `severity` (`info` | `warning` | `critical`)
3. Submit it: `POST {LISTO_API_URL}/v1/learnings` with that JSON, header `Authorization: Bearer ${LISTO_API_KEY}`.
4. Confirm to the user: "Captured as a review candidate — it'll apply to everyone once the Listo team
   approves it." Do NOT claim it is live immediately, and never submit anything containing personal data.
