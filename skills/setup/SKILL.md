---
description: "First-time setup for YT Comment-to-Client automation. Installs dependencies, authorizes Google access, detects YouTube channel, optionally uses vidIQ for keyword suggestions, creates Google Sheet log, and schedules the hourly poller. Trigger phrases: 'set up comment bot', 'install comment-to-client', 'connect YouTube comments', 'first time setup', 'setup', 'configure comment reply', 'get started'."
---

# YT Comment-to-Client: Setup Wizard

Run this one-time setup for a new user. Complete all steps in order. Do not skip steps.
Communicate progress clearly in plain language — no file paths, no technical jargon.

---

## Step 1 — Find Python

Use Desktop Commander `start_process` to run `python --version`.
If that fails, try `C:\Python314\python.exe --version`.
Store the working executable path as PYTHON_PATH.
If Python is not found at any path, tell user: "Python is needed to run the comment bot.
Please install it from python.org (it's free) and then run setup again." Stop.

---

## Step 2 — Install required packages

Run via Desktop Commander `start_process`:
```
{PYTHON_PATH} -m pip install google-auth google-auth-oauthlib google-api-python-client gspread --quiet
```
Tell user: "Installing required packages..." Wait for completion.

---

## Step 3 — Create bot directory and copy scripts

Use Desktop Commander `create_directory` to create `C:\YT-Comment-Bot\` if it doesn't exist.

Use Glob to find the plugin's `references/` folder by searching for `yt_comment_poller.py` across
all plugin directories. Once found, note the parent directory path as REFS_DIR.

Copy these three files from REFS_DIR to `C:\YT-Comment-Bot\` using Desktop Commander
`read_file` + `write_file`:
- `yt_comment_poller.py`
- `get_token.py`
- `client_secrets.json`

---

## Step 4 — Google Authorization

Tell user: "A browser window is about to open. Sign in with the Google account that
**owns your YouTube channel**, then click Allow. Come back here when the page says the flow is complete."

Run via Desktop Commander `start_process`:
```
{PYTHON_PATH} C:\YT-Comment-Bot\get_token.py
```
Wait for the process to complete and confirm `token.json` was saved (check output for "Authorization complete").

---

## Step 5 — Detect YouTube channel

Write a temporary detection script to `C:\YT-Comment-Bot\_detect.py` via Desktop Commander:

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
creds = Credentials.from_authorized_user_file(
    r'C:\YT-Comment-Bot\token.json',
    ['https://www.googleapis.com/auth/youtube.force-ssl']
)
yt = build('youtube', 'v3', credentials=creds)
r = yt.channels().list(part='snippet,contentDetails', mine=True).execute()
for ch in r.get('items', []):
    print(json.dumps({'name': ch['snippet']['title'], 'id': ch['id']}))
```

Run it: `{PYTHON_PATH} C:\YT-Comment-Bot\_detect.py`
Parse JSON. Tell user: "Found your channel: **[name]**. Is this correct?"
If wrong, ask which Google account owns the correct channel and re-run Step 4.
Store channel ID as CHANNEL_ID.

---

## Step 5b — Optional: vidIQ keyword enhancement

Try calling the vidIQ keyword research tool with query "GUIDE" (or a keyword matching the channel's niche).

- **vidIQ available:** Show top 3 keyword suggestions with search volume + competition scores.
  Ask user to pick one or type their own. Mention: "vidIQ is connected — this is why it's
  worth having it installed alongside this plugin."
- **vidIQ NOT available:** Skip silently. Proceed to Step 6 without mentioning this step.
- **TubeBuddy users:** No direct integration yet — note it when TubeBuddy MCP becomes available.

Store chosen keyword as KEYWORD_SUGGESTION.

---

## Step 6 — Collect settings

Ask the user (use AskUserQuestion):
1. **Landing URL** — the opt-in page URL (your GHL landing page)
2. **Keyword** — trigger word viewers type (default: GUIDE, or pre-fill KEYWORD_SUGGESTION)

Store as LANDING_URL and KEYWORD.

---

## Step 7 — Create Google Sheet log

Use Google Docs MCP `createSpreadsheet` to create: "YT Comment-to-Client — [channel name]"
Note the spreadsheet ID as SHEET_ID.
Add header row to Sheet1:
`video_id | video_title | video_published | comment_id | author_name | author_channel_url | comment_text | keyword_detected | sentiment | reply_sent | reply_text | reply_timestamp | utm_link`
Share the sheet link with the user.

---

## Step 8 — Write config.json

Write `C:\YT-Comment-Bot\config.json` via Desktop Commander:
```json
{
  "channel_id": "<CHANNEL_ID>",
  "keyword": "<KEYWORD>",
  "landing_url": "<LANDING_URL>",
  "sheet_id": "<SHEET_ID>",
  "reply_delay_min": 120,
  "reply_delay_max": 900
}
```

---

## Step 9 — Create scheduled task

Use `mcp__scheduled-tasks__create_scheduled_task`:
- `taskId`: `"yt-c2c-"` + first 8 chars of CHANNEL_ID (lowercase)
- `description`: `"YT Comment-to-Client — [channel name] (hourly new-video check)"`
- `cronExpression`: `"0 * * * *"`
- `prompt`:
```
Run the YouTube Comment-to-Client bot.
Use Desktop Commander start_process:
  command: "<PYTHON_PATH>"
  args: ["C:\\YT-Comment-Bot\\yt_comment_poller.py"]
  working_dir: "C:\\YT-Comment-Bot\\"
  timeout_seconds: 600
Read output and report one-line summary (new video found or skipped).
```

---

## Step 10 — Cleanup and confirm

Delete temp script: Desktop Commander `start_process` → `del C:\YT-Comment-Bot\_detect.py`

Tell user:
> ✅ **Setup complete!**
> - **Channel:** [name]
> - **Keyword:** [keyword] — viewers type this in comments
> - **Landing page:** [URL]
> - **Log sheet:** [link]
> - **Runs:** Every hour — only does real work when a new video is published
>
> To update your landing URL or keyword at any time, say **"update config"**.
