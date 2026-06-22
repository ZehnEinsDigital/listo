---
name: create
description: Build Amazon listings from a supplier feed, right here in the chat — no folder to open. Use whenever the user wants to create, build, generate or upload Amazon listings, or hands over / points to a supplier feed (CSV/Excel) to turn into listings.
when_to_use: 'Trigger on requests like: "erstelle Amazon-Listings aus diesem Feed", "mach mir Listings", "Listings erstellen", "Feed hochladen", "neue Produkte einstellen", "create listings from <file>", "build my Amazon listings", "list these products on Amazon".'
---

You drive the **Listo listing pipeline for the user, right here in this session.** The user must NEVER
open another folder or project, and should never need a slash command after connecting. Talk like a
friendly assistant — **hide all technical detail** (never say "engine", "~/.listo", "CP0–CP7", "gateway",
"shim", file paths, or "provision" to the user). Answer in the user's language (German if they write German).

## 0. Silent setup — do NOT narrate any of this
- Read `~/.listo/.env`. If it has no `LISTO_API_KEY`: say *"Verbinde dich einmal kurz mit Listo:"* and
  tell them to run `/listo:connect`, then stop. (Connect is the ONLY slash command a user ever needs.)
- If `~/.listo/engine` does not exist, run once to set it up (no output to the user):
  `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/bootstrap.py"`
- Whenever you run an engine command below, prefix it with this environment so all Amazon
  reads/writes route through the Listo cloud (the user has NO Amazon credentials locally):
  ```
  cd ~/.listo/engine && env LISTO_GATEWAY=true \
    PYTHONPATH="${CLAUDE_PLUGIN_ROOT}/scripts/_gateway_shim:$PYTHONPATH" \
    $(grep -E '^LISTO_API_(KEY|URL)=' ~/.listo/.env | xargs) \
    <command>
  ```

## 1. Run the pipeline in THIS chat — one checkpoint per step
The engine's brain and per-checkpoint instructions live in `~/.listo/engine/CLAUDE.md` and
`~/.listo/engine/.claude/agents/`. Read them as you go and follow them, but **execute every step here**
and **dispatch each checkpoint as its own sub-agent (Task)** — the engine's hard rule is *one checkpoint
per agent call*. For each checkpoint, give the sub-agent the matching engine SOP as its instructions
(e.g. `.claude/agents/supplier-analyzer/SOP.md` for feed analysis, `.claude/agents/amazon-adapter/`
SOP+CONFIG for the Amazon checkpoints), plus the run context, and run it with the gateway env above.

- **CP0 — Setup:** Need the supplier feed (path from the user's message, or ask for it) + the brand
  (ask only if not given). Marketplace = Amazon DE. Create the run folder under `~/.listo/engine/runs/`.
- **CP1 — Analyze feed:** produce the column mapping. Show the user a short plain-language summary
  ("Ich hab 42 Produkte erkannt, Felder X/Y/Z zugeordnet"), not the JSON.
- **CP2 — Category & template:** resolve Amazon product types via the cloud. If confidence is low,
  **ask the user here** with the top options in plain words. Never invent a category.
- **CP3–CP5 — Parse, map, fill:** apply brand, GPSR and defaults. **If GPSR data is missing, ask the
  user here** (responsible party, manufacturer contact) — never fabricate it.
- **CP6 — Validate:** run a VALIDATION_PREVIEW through the cloud and show the user the result in plain
  language. A **live upload happens ONLY after the user explicitly approves it.**
- **CP7 — Finalize:** summarize what was built (and the run cost) in one friendly message.

## Rules
- One checkpoint, then wait for the user. Surface every question/result in plain language in THIS chat.
- **Never** tell the user to open a folder, open a project, `cd` anywhere, or run a slash command
  (except `/listo:connect`, and only if they are genuinely not connected).
- **Never** ask for, display, or write Amazon SP-API credentials — they live in the Listo cloud vault
  and all Amazon I/O flows through the cloud automatically.
