---
description: Provision/refresh your Listo engine and open it as a Claude Code project — the one-step entry to building listings
argument-hint: ""
---

The one-step entry. In the new architecture **Listo IS the engine**: the user opens the provisioned
engine project in Claude Code and talks to it natively (its own `CLAUDE.md` + agents + skills drive
CP0→CP7). Your job here is only to provision the engine and tell the user how to open it — you do NOT
run the pipeline yourself.

## 1. Provision / refresh the engine
Run:
```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/bootstrap.py"
```
This pulls the subscription-gated brain into `~/.listo/engine`, seeds it (learnings + Amazon cache),
and hardens the engine's Claude settings. **Abort and report on any error it prints** (e.g. 402 = no
active subscription → tell the user to fix their subscription, then re-run `/listo:open`).

## 2. Make the engine folder easy to find
`~/.listo` is hidden, so a GUI folder-picker can't see it. Create/refresh a VISIBLE symlink at the
user's home, pointing at the engine:
```
ln -sfn ~/.listo/engine ~/Listo-Engine
```

## 3. Tell the user to open the engine as their project
Explain clearly:

- **Open `~/Listo-Engine` (= `~/.listo/engine`) as your Claude Code project.**
  - In the **Desktop** Code tab: **Open Folder → Listo-Engine**.
  - In the **CLI**: `cd ~/.listo/engine` and start Claude Code there.
- Once you're inside the engine project, **just talk to Listo's engine natively**: its start box
  appears → pick Amazon → drop your supplier feed → it walks you through **CP0–CP7**.
- **Amazon reads and writes route automatically through the Listo cloud** — no Amazon credentials are
  needed on your machine. (The session shim handles this transparently.)
- **Prerequisite:** store your Amazon credentials in the **Listo web app** first; the cloud uses them
  on your behalf. You never paste Amazon SP-API credentials locally.
