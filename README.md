# Frontend Job Hunt

Simple repo for daily Frontend / React job leads.

- `job-leads.md` — curated openings (appended by the Cursor automation)
  - Columns include **Date found** and **Time found** (IST) so you can see which automation run added each lead
- `job-leads.html` — apply board UI (open in a browser)
- Regenerate the HTML after markdown updates:

```bash
python3 scripts/build-job-leads-html.py
open job-leads.html
```

## Setup for Cursor Automations

1. Push this repo to GitHub.
2. In the automation, select this repo and the `main` branch.
3. The agent will append new leads to `job-leads.md` each day.
4. Re-run the HTML build script (or ask the agent to) so `job-leads.html` stays in sync.
