---
description: Create Amazon listings — points you into the native Listo engine project (the engine itself drives CP0→CP7; this command no longer emulates the pipeline)
argument-hint: "[path/to/supplier-feed] [brand]"
---

In the new architecture **Listo IS the engine** — you build listings by opening the provisioned engine
project and talking to it natively, not by emulating the pipeline from outside. So this command just
routes you to the right place. **NEVER ask for or handle Amazon SP-API credentials** — they live in the
Listo vault, and Amazon I/O routes through the Listo cloud automatically.

## If you are already inside the engine project (cwd is `~/.listo/engine`)
You don't need this command. Just **describe your feed to the engine**: its native workflow takes over —
the start box appears → pick Amazon → drop your supplier feed → it walks you through **CP0–CP7**. Amazon
reads/writes auto-route via the Listo cloud (no local credentials).

## Otherwise (you are not in the engine project)
Do **not** try to run the pipeline from here. Instead:

1. If you're not connected yet, run **`/listo:connect`** (one-time browser login).
2. Run **`/listo:open`** — it provisions/refreshes `~/.listo/engine` and creates the visible
   `~/Listo-Engine` symlink.
3. **Open `~/Listo-Engine` (= `~/.listo/engine`) as your Claude Code project** (Desktop: Open Folder →
   Listo-Engine; CLI: `cd ~/.listo/engine`), then describe your feed there.
