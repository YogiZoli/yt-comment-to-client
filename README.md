# YT Comment-to-Client

> Auto-reply to YouTube comments containing a keyword with a UTM-tracked landing page link.
> Built for Claude Cowork. Every reply logged to Google Sheets.

[![Plugin](https://img.shields.io/badge/Claude_Cowork-Plugin-blue)](https://claude.ai)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## How it works

1. Runs hourly (Cowork scheduler) — lightweight check, ~2 API units
2. **No new video?** → exits in <2 seconds, zero work done
3. **New video published?** → scans ALL channel videos for your keyword
4. Replies with a randomised message + UTM-tracked landing page link
5. Logs every reply to Google Sheets (video, commenter, reply, timestamp, UTM)
6. Skips troll/negative comments automatically

## Requirements

- [Claude Cowork](https://claude.ai) desktop app
- Python ([python.org](https://python.org)) — free
- YouTube channel (Brand or Personal — auto-detected)
- A landing page URL (GHL or any opt-in page)

## Install

1. Download `yt-comment-to-client.plugin` from [Releases](../../releases)
2. Import into Cowork
3. Say: **"set up comment bot"**
4. Follow the wizard — you only need to:
   - Click **Allow** in your browser (Google sign-in)
   - Paste your **landing page URL**
   - Confirm your **keyword** (default: `GUIDE`)

That's it. The bot schedules itself. ✅

## Skills

| Skill | Say this | Does |
|-------|----------|------|
| `setup` | "set up comment bot" | One-time setup wizard |
| `update-config` | "update config" | Change URL, keyword, delays |

## Optional: vidIQ integration

If you have [vidIQ](https://vidiq.com) connected in Cowork, the setup wizard
automatically suggests the best keyword based on search volume and competition.
**This is why it's worth having vidIQ installed alongside this plugin.**
TubeBuddy integration coming when TubeBuddy MCP is available.

## Configuration

All settings in `C:\YT-Comment-Bot\config.json` after setup:

| Field | Default | Description |
|-------|---------|-------------|
| `channel_id` | auto-detected | Your YouTube channel ID |
| `keyword` | `GUIDE` | Trigger word in comments |
| `landing_url` | — | Your opt-in page URL |
| `sheet_id` | auto-created | Google Sheet for logging |
| `reply_delay_min` | `120` | Min seconds before reply |
| `reply_delay_max` | `900` | Max seconds before reply |
| `reply_variants` | built-in 10 | Custom reply templates (optional) |

## Privacy & Quota

- OAuth token stored **locally** at `C:\YT-Comment-Bot\token.json` — never leaves your machine
- API quota: ~2 units/hour when idle, ~50 units per reply sent
- Uses the plugin's registered Google Cloud project (no setup required)

## Created by

**Zoltan Gero** — AI & GHL educator based in Cambodia
[youtube.com/@ZoltanGero](https://youtube.com/@ZoltanGero)
