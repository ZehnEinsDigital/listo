---
description: Connect Listo to your account via the browser (like gh login — no key to paste)
argument-hint: ""
---

One-time setup: connect this device to the user's Listo account. **Do NOT ask the user to paste
their API key.** Run the browser device-auth flow instead.

1. Run:
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/connect.py"
   ```
   (For a LOCAL test stack, prefix it with `LISTO_API_URL="http://localhost:8000"`.)
2. It opens the Listo web app and prints a short confirmation code + a URL. Tell the user:
   "I've opened your browser — log in if needed, check the code matches, and click **Authorize**."
3. The script waits, receives the key automatically, and saves it to `~/.listo/.env`. When it prints
   "LISTO connected", confirm: "✅ Verbunden. Sag mir einfach, was du auf Amazon listen willst — z.B.
   *„erstelle Listings aus dieser Datei"*. Kein Befehl, kein Ordner nötig." (The create skill auto-triggers
   on that.)

Never request, display, or write the API key yourself — the browser flow handles it end to end.
