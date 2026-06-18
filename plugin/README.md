# Listo — your Amazon listing copilot for Claude Code

Listo turns supplier feeds into upload-ready Amazon listings and helps you check, update, and fix
existing listings — **inside your own Claude Code**. The AI reasoning runs on **your** Claude plan;
your **Amazon credentials and the actual uploads stay in the Listo cloud** and never touch your
machine. Flat monthly subscription — no per-token bill from us.

## Before you start

1. **Claude Code on a paid Claude plan.** That means the **Code** tab of the Claude Desktop app, the
   Claude Code CLI, or an IDE extension. (The Desktop **Chat** tab, custom connectors, and ChatGPT
   can't run it — Listo needs Bash + sub-agents.)
2. **A Listo account** with an active subscription — sign up at the Listo web app. A fresh signup is
   active right away during the test phase.

## Setup — 3 steps

**1 · Install the plugin** (no terminal needed)
In Claude Code: **+** menu → **Plugins** → **Add marketplace** → **Add from a repository** → paste
`ZehnEinsDigital/listo` → install **listo**. Or by command:
```
/plugin marketplace add ZehnEinsDigital/listo
/plugin install listo@listo
```

**2 · Connect your account** (one click — nothing to paste)
In Claude Code run:
```
/listo:connect
```
It opens your browser to the Listo web app — log in if needed, click **Authorize**, done. The key is
delivered to your machine and saved to `~/.listo/.env` automatically; you never copy or paste it.
(Advanced/CLI: set `LISTO_API_KEY` in `~/.listo/.env` yourself.) Never enter Amazon or Anthropic keys.

**3 · Use it**
```
/listo:create ./my-supplier-feed.csv
```
The engine downloads itself on first run (into `~/.listo/engine`), pulls the current Listo "brain", and
walks you through the listing step by step, pausing whenever it needs a decision from you.

> Amazon credentials live only in the Listo web app's encrypted vault — store them there once.

## Commands

| Command | What it does |
|---------|--------------|
| `/listo:connect` | One-time: save your Listo API key |
| `/listo:create <feed> [brand]` | Build Amazon listings from a supplier feed |
| `/listo:validate <sku\|payload>` | Server-side validation preview (no write) |
| `/listo:status <sku>` | What Amazon reports about a listing right now |
| `/listo:update <skus> <change>` | Partial content update (keeps ASIN/reviews) |
| `/listo:diagnose <sku>` | Explain a rejection/suppression + propose a fix |
| `/listo:ask <question>` | Free-form catalog / product-type questions |

## How it works (and why it's safe)

- The reasoning + the deterministic engine run **locally on your plan** — we never see your tokens.
- Each run pulls the current **brain** (learnings + marketplace rules) from Listo, **gated by your
  subscription**. No active plan → no fresh brain, no upload.
- Every Amazon read/write goes through the **Listo cloud gateway**, which holds your credentials and
  performs the call server-side. The plugin can **never** write to a marketplace directly — uploads are
  subscription-gated and dry-run by default until you approve.
