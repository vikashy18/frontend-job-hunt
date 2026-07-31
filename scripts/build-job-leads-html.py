#!/usr/bin/env python3
"""Build job-leads.html from job-leads.md for easy applying."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "job-leads.md"
HTML_PATH = ROOT / "job-leads.html"


def parse_leads(text: str) -> list[dict]:
    rows: list[dict] = []
    for line in text.splitlines():
        if not line.startswith("|") or "Date found" in line or re.match(r"^\|[-| ]+\|$", line):
            continue
        parts = [c.strip() for c in line.strip("|").split("|")]
        if len(parts) < 10:
            continue
        date, time, title, company, location, mode, source, url, why, status = parts[:10]
        if url in ("—", "-", ""):
            continue
        rows.append(
            {
                "date": date,
                "time": time,
                "title": title,
                "company": company,
                "location": location,
                "mode": mode,
                "source": source,
                "url": url,
                "why": why,
                "status": status,
            }
        )
    return rows


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Frontend Job Leads — Apply Board</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Newsreader:opsz,wght@6..72,500;6..72,600&display=swap" rel="stylesheet" />
  <style>
    :root {{
      --bg: #f3efe6;
      --ink: #1c1915;
      --muted: #5c564c;
      --line: #d8d0c2;
      --panel: #fffdf8;
      --accent: #0f6e56;
      --accent-soft: #d8f0e7;
      --warn: #8a4b12;
      --warn-soft: #f5e6d4;
      --done: #3d4f3f;
      --done-soft: #e4ebe5;
      --shadow: 0 1px 0 rgba(28, 25, 21, 0.04), 0 12px 32px rgba(28, 25, 21, 0.06);
    }}

    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; }}
    body {{
      font-family: "IBM Plex Sans", system-ui, sans-serif;
      color: var(--ink);
      background:
        radial-gradient(1200px 500px at 10% -10%, #e8f2ee 0%, transparent 55%),
        radial-gradient(900px 420px at 100% 0%, #efe6d8 0%, transparent 50%),
        var(--bg);
      min-height: 100vh;
    }}

    .wrap {{
      width: min(1120px, calc(100% - 2rem));
      margin: 0 auto;
      padding: 2rem 0 4rem;
    }}

    header {{
      display: grid;
      gap: 0.75rem;
      margin-bottom: 1.5rem;
    }}

    h1 {{
      font-family: Newsreader, Georgia, serif;
      font-weight: 600;
      font-size: clamp(1.8rem, 3vw, 2.4rem);
      letter-spacing: -0.02em;
      margin: 0;
    }}

    .subtitle {{
      color: var(--muted);
      max-width: 42rem;
      line-height: 1.5;
      margin: 0;
    }}

    .stats {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }}

    .chip {{
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 999px;
      padding: 0.35rem 0.75rem;
      font-size: 0.85rem;
      color: var(--muted);
    }}

    .chip strong {{ color: var(--ink); font-weight: 600; }}

    .toolbar {{
      position: sticky;
      top: 0;
      z-index: 5;
      display: grid;
      gap: 0.75rem;
      padding: 0.85rem;
      margin-bottom: 1rem;
      background: color-mix(in srgb, var(--panel) 92%, transparent);
      backdrop-filter: blur(10px);
      border: 1px solid var(--line);
      border-radius: 14px;
      box-shadow: var(--shadow);
    }}

    .filters {{
      display: grid;
      grid-template-columns: 1.4fr repeat(3, minmax(0, 1fr));
      gap: 0.6rem;
    }}

    @media (max-width: 800px) {{
      .filters {{ grid-template-columns: 1fr 1fr; }}
    }}

    label {{
      display: grid;
      gap: 0.25rem;
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--muted);
    }}

    input, select {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 0.65rem 0.75rem;
      background: #fff;
      color: var(--ink);
      font: inherit;
    }}

    input:focus, select:focus {{
      outline: 2px solid color-mix(in srgb, var(--accent) 35%, white);
      border-color: var(--accent);
    }}

    .toolbar-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      align-items: center;
      justify-content: space-between;
    }}

    .hint {{
      color: var(--muted);
      font-size: 0.9rem;
    }}

    button {{
      font: inherit;
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--ink);
      border-radius: 10px;
      padding: 0.55rem 0.85rem;
      cursor: pointer;
    }}

    button:hover {{ border-color: #b9b0a0; }}
    a.btn {{
      display: inline-flex;
      align-items: center;
      text-decoration: none;
      font: inherit;
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--ink);
      border-radius: 10px;
      padding: 0.55rem 0.85rem;
      cursor: pointer;
    }}
    a.btn.primary {{
      background: var(--accent);
      border-color: var(--accent);
      color: #fff;
      font-weight: 600;
    }}
    a.btn.primary:hover {{ filter: brightness(1.05); }}
    button.ghost {{ background: transparent; }}

    .list {{
      display: grid;
      gap: 0.75rem;
    }}

    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 1rem 1.1rem;
      box-shadow: var(--shadow);
      display: grid;
      gap: 0.7rem;
      transition: opacity 0.15s ease, border-color 0.15s ease;
    }}

    .card.applied {{
      opacity: 0.62;
      border-color: #c9d2cb;
    }}

    .card.skipped {{
      opacity: 0.45;
    }}

    .card-top {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem 1rem;
      justify-content: space-between;
      align-items: start;
    }}

    .title-block {{
      display: grid;
      gap: 0.2rem;
      min-width: min(100%, 28rem);
    }}

    .title {{
      font-family: Newsreader, Georgia, serif;
      font-size: 1.2rem;
      font-weight: 600;
      margin: 0;
      letter-spacing: -0.01em;
    }}

    .company {{
      color: var(--muted);
      font-weight: 500;
    }}

    .meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem;
    }}

    .tag {{
      font-size: 0.78rem;
      border-radius: 999px;
      padding: 0.22rem 0.55rem;
      background: #efeae1;
      color: var(--muted);
    }}

    .tag.mode {{ background: var(--accent-soft); color: var(--accent); }}
    .tag.time {{ background: var(--warn-soft); color: var(--warn); }}
    .tag.done {{ background: var(--done-soft); color: var(--done); }}

    .why {{
      margin: 0;
      color: var(--muted);
      line-height: 1.45;
      font-size: 0.95rem;
    }}

    .actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.45rem;
      align-items: center;
    }}

    .empty {{
      text-align: center;
      padding: 3rem 1rem;
      color: var(--muted);
      border: 1px dashed var(--line);
      border-radius: 14px;
      background: color-mix(in srgb, var(--panel) 70%, transparent);
    }}

    footer {{
      margin-top: 2rem;
      color: var(--muted);
      font-size: 0.85rem;
    }}

    a.sr-only-focusable {{
      position: absolute;
      left: -9999px;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>Frontend Job Leads</h1>
      <p class="subtitle">Browse curated React / Frontend roles, open the posting, and mark what you’ve applied to. Progress is saved in this browser.</p>
      <div class="stats" id="stats"></div>
    </header>

    <section class="toolbar" aria-label="Filters">
      <div class="filters">
        <label>Search
          <input id="q" type="search" placeholder="Title, company, city, stack…" />
        </label>
        <label>Date
          <select id="date"></select>
        </label>
        <label>Work mode
          <select id="mode">
            <option value="">All modes</option>
          </select>
        </label>
        <label>Status
          <select id="status">
            <option value="open">To apply</option>
            <option value="applied">Applied</option>
            <option value="skipped">Skipped</option>
            <option value="all">All</option>
          </select>
        </label>
      </div>
      <div class="toolbar-actions">
        <p class="hint" id="showing"></p>
        <div class="actions">
          <button type="button" class="ghost" id="resetStatus">Clear applied/skipped</button>
        </div>
      </div>
    </section>

    <main class="list" id="list" aria-live="polite"></main>
    <footer>Generated from <code>job-leads.md</code>. Re-run <code>python3 scripts/build-job-leads-html.py</code> after new automation merges.</footer>
  </div>

  <script>
    const LEADS = __LEADS_JSON__;

    const STORE_KEY = "frontend-job-hunt-status-v1";
    const listEl = document.getElementById("list");
    const statsEl = document.getElementById("stats");
    const showingEl = document.getElementById("showing");
    const qEl = document.getElementById("q");
    const dateEl = document.getElementById("date");
    const modeEl = document.getElementById("mode");
    const statusEl = document.getElementById("status");

    function loadStatus() {{
      try {{ return JSON.parse(localStorage.getItem(STORE_KEY) || "{{}}"); }}
      catch {{ return {{}}; }}
    }}

    function saveStatus(map) {{
      localStorage.setItem(STORE_KEY, JSON.stringify(map));
    }}

    let statusMap = loadStatus();

    function leadKey(lead) {{
      return lead.url;
    }}

    function getLeadStatus(lead) {{
      return statusMap[leadKey(lead)] || "open";
    }}

    function setLeadStatus(lead, value) {{
      const key = leadKey(lead);
      if (value === "open") delete statusMap[key];
      else statusMap[key] = value;
      saveStatus(statusMap);
      render();
    }}

    function uniqueSorted(values) {{
      return [...new Set(values.filter(Boolean))].sort().reverse();
    }}

    function populateFilters() {{
      const dates = uniqueSorted(LEADS.map((l) => l.date));
      dateEl.innerHTML = '<option value="">All dates</option>' + dates.map((d) => `<option value="${{d}}">${{d}}</option>`).join("");

      const modes = [...new Set(LEADS.map((l) => l.mode).filter(Boolean))].sort();
      modeEl.innerHTML = '<option value="">All modes</option>' + modes.map((m) => `<option value="${{m}}">${{m}}</option>`).join("");
    }}

    function matches(lead) {{
      const q = qEl.value.trim().toLowerCase();
      const date = dateEl.value;
      const mode = modeEl.value;
      const status = statusEl.value;
      const leadStatus = getLeadStatus(lead);

      if (date && lead.date !== date) return false;
      if (mode && lead.mode !== mode) return false;
      if (status !== "all" && leadStatus !== status) return false;
      if (q) {{
        const hay = [lead.title, lead.company, lead.location, lead.mode, lead.source, lead.why].join(" ").toLowerCase();
        if (!hay.includes(q)) return false;
      }}
      return true;
    }}

    function escapeHtml(str) {{
      return String(str)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
    }}

    function renderStats() {{
      const applied = LEADS.filter((l) => getLeadStatus(l) === "applied").length;
      const skipped = LEADS.filter((l) => getLeadStatus(l) === "skipped").length;
      const open = LEADS.length - applied - skipped;
      statsEl.innerHTML = `
        <span class="chip"><strong>${{LEADS.length}}</strong> total</span>
        <span class="chip"><strong>${{open}}</strong> to apply</span>
        <span class="chip"><strong>${{applied}}</strong> applied</span>
        <span class="chip"><strong>${{skipped}}</strong> skipped</span>
      `;
    }}

    function render() {{
      renderStats();
      const filtered = LEADS.filter(matches);
      showingEl.textContent = `Showing ${{filtered.length}} of ${{LEADS.length}}`;

      if (!filtered.length) {{
        listEl.innerHTML = `<div class="empty">No leads match these filters.</div>`;
        return;
      }}

      listEl.innerHTML = filtered.map((lead, index) => {{
        const st = getLeadStatus(lead);
        const statusLabel = st === "applied" ? "Applied" : st === "skipped" ? "Skipped" : "To review";
        return `
          <article class="card ${{st}}" data-url="${{escapeHtml(lead.url)}}">
            <div class="card-top">
              <div class="title-block">
                <h2 class="title">${{escapeHtml(lead.title)}}</h2>
                <div class="company">${{escapeHtml(lead.company)}}</div>
              </div>
              <div class="meta">
                <span class="tag time">${{escapeHtml(lead.date)}} · ${{escapeHtml(lead.time)}}</span>
                <span class="tag mode">${{escapeHtml(lead.mode)}}</span>
                <span class="tag">${{escapeHtml(lead.location)}}</span>
                <span class="tag">${{escapeHtml(lead.source)}}</span>
                <span class="tag done">${{statusLabel}}</span>
              </div>
            </div>
            <p class="why">${{escapeHtml(lead.why)}}</p>
            <div class="actions">
              <a class="btn primary" href="${{escapeHtml(lead.url)}}" target="_blank" rel="noopener noreferrer">Open &amp; apply</a>
              <button type="button" data-action="applied">Mark applied</button>
              <button type="button" data-action="skipped">Skip</button>
              <button type="button" class="ghost" data-action="open">Reset</button>
            </div>
          </article>
        `;
      }}).join("");
    }}

    listEl.addEventListener("click", (event) => {{
      const btn = event.target.closest("button[data-action]");
      if (!btn) return;
      const card = btn.closest(".card");
      if (!card) return;
      const lead = LEADS.find((l) => l.url === card.dataset.url);
      if (!lead) return;
      setLeadStatus(lead, btn.dataset.action);
    }});

    document.getElementById("resetStatus").addEventListener("click", () => {{
      if (!confirm("Clear all applied/skipped marks saved in this browser?")) return;
      statusMap = {{}};
      saveStatus(statusMap);
      render();
    }});

    [qEl, dateEl, modeEl, statusEl].forEach((el) => el.addEventListener("input", render));

    populateFilters();
    render();
  </script>
</body>
</html>
"""


def main() -> None:
    leads = parse_leads(MD_PATH.read_text())
    html = TEMPLATE.replace("__LEADS_JSON__", json.dumps(leads, ensure_ascii=False))
    HTML_PATH.write_text(html)
    print(f"Wrote {HTML_PATH.name} with {len(leads)} leads")


if __name__ == "__main__":
    main()
