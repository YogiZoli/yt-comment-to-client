---
description: "Update YT Comment-to-Client settings after initial setup. Change landing page URL, keyword, reply delays, or reply message variants. Trigger phrases: 'update config', 'change landing URL', 'update keyword', 'change my link', 'configure', 'settings', 'update comment bot', 'change reply message'."
---

# YT Comment-to-Client: Update Settings

Read and update the bot's configuration. Use this after setup to change any setting without re-running the full setup wizard.

---

## Read current config

Use Desktop Commander `read_file` to read `C:\YT-Comment-Bot\config.json`.
Show the user their current settings in a clean format:
- Channel ID
- Keyword (the trigger word)
- Landing URL
- Sheet ID
- Reply delay (min / max seconds)

---

## Ask what to change

Ask the user what they want to update. Common changes:
- **Landing URL** — update when GHL funnel domain changes
- **Keyword** — change the trigger word
- **Reply delays** — adjust the anti-spam randomised wait time
- **Reply variants** — add custom reply messages (store as `reply_variants` array in config.json)

---

## Apply changes

Update only the fields the user specified. Write the modified config back to `C:\YT-Comment-Bot\config.json` via Desktop Commander `write_file`. Preserve all unchanged fields.

---

## Confirm

Tell the user what was updated. Remind them the change takes effect on the next hourly run automatically — no restart needed.
