# ☀️ MorningBriefing — AI Executive Assistant for College Students

> **Wake up to a single, beautiful summary instead of 4 anxious browser tabs.**

MorningBriefing is an autonomous agent that runs while you sleep. It uses **Browser Use** to log into all of your fragmented university and work portals, scrapes only the data you actually care about, and delivers a clean morning summary — by email or right in your terminal.

---

## What It Checks

| Portal | What It Finds |
|---|---|
| 📚 **Canvas LMS** | Assignments / quizzes due in the next 48 hrs, class cancellations, new announcements |
| 💼 **Workday** | Upcoming work shifts, schedule changes |
| 📧 **Outlook / Microsoft 365** | Canceled/rescheduled classes, urgent emails, today's calendar |
| 🏦 **Bank** | Current balance, overdraft warnings, large recent transactions |

---

## Sample Output

```
╔══════════════════════════════════════════════════════════╗
║            ☀️  GOOD MORNING — Daily Briefing             ║
║               Monday, April 06 2026  06:00 AM            ║
╚══════════════════════════════════════════════════════════╝

📚 CANVAS
  Upcoming Deadlines (next 48 hrs):
  • [ASSIGNMENT] CS 301 Midterm Study Guide — CS 301  ⏰ 2026-04-06T23:59:00
  • [QUIZ]       Quiz 4 — Recursion — CS 301          ⏰ 2026-04-07T11:59:00
  Class Cancellations:
  🚫 ENG 101 on 2026-04-06: Professor out sick — no class today.

💼 WORKDAY — Upcoming Shifts
  • 2026-04-06  16:00 – 20:00  @ Campus Library Desk

📧 OUTLOOK
  Cancellations / Reschedules:
  🚫 ENG 101 — Class Canceled Today (from prof.jones@university.edu)
  Today's Calendar:
  📅 9:00 AM  CS 301 Lecture  @ Olson Hall 204

🏦 BANK
  Balance: $18.43 USD
  🚨 OVERDRAFT WARNING: Balance $18.43 is below threshold $25.00
  Large Transactions (last 24 hrs):
  • 2026-04-05  Amazon.com  –$67.99
```

---

## Quick Start

### 1 — Clone & Install

```bash
git clone https://github.com/nvutharkar/morningbriefing
cd morningbriefing

python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

### 2 — Configure

```bash
cp .env.example .env
# Edit .env with your credentials
```

Fill in only the portals you use — unconfigured ones are gracefully skipped.

### 3 — Try Demo Mode (no credentials needed)

```bash
python main.py --demo
```

This runs with fake sample data so you can see exactly what the output looks like before touching any passwords.

### 4 — Run Once

```bash
python main.py
```

### 5 — Schedule for Every Morning

```bash
python main.py --schedule    # uses BRIEFING_HOUR / BRIEFING_MINUTE from .env
```

Or use **cron** (Linux/macOS):

```bash
# Run at 6:00 AM every day
0 6 * * * cd /path/to/morningbriefing && .venv/bin/python main.py >> briefing.log 2>&1
```

Or **Task Scheduler** on Windows.

---

## Project Structure

```
morningbriefing/
├── main.py               # Orchestrator + CLI
├── briefing.py           # Renders the summary (text + HTML)
├── notifier.py           # Sends briefing via email
├── config.py             # All settings (reads from .env)
├── requirements.txt
├── .env.example
└── agents/
    ├── canvas_agent.py   # Canvas LMS browser agent
    ├── workday_agent.py  # Workday browser agent
    ├── outlook_agent.py  # Outlook / M365 browser agent
    └── bank_agent.py     # Online banking browser agent
```

---

## How It Works

Each agent is powered by **[Browser Use](https://github.com/browser-use/browser-use)** — an open-source library that lets LLMs control a real Chromium browser. The agents:

1. Launch a headless browser
2. Log into the portal using your credentials (stored only in your local `.env`)
3. Navigate to the relevant pages and extract structured data
4. Return clean JSON that the briefing renderer turns into your summary

Your passwords **never leave your machine** — they're passed directly to the browser, not sent to any API.

---

## Email Delivery Setup (Gmail)

1. Enable [2-Step Verification](https://myaccount.google.com/security) on your Google account  
2. Create an [App Password](https://myaccount.google.com/apppasswords) (select "Mail")  
3. Set `SMTP_USER`, `SMTP_PASSWORD` (the app password), and `NOTIFICATION_EMAIL` in `.env`

---

## Customizing Agents

Each agent file (`agents/*.py`) contains a `TASK` string — a plain-English prompt describing what the browser agent should do. You can edit it to scrape different data, navigate differently, or add new portals entirely.

---

## Requirements

- Python 3.10+
- An OpenAI or Anthropic API key
- Chromium (installed automatically by `playwright install chromium`)

---

## Built With

- [Browser Use](https://github.com/browser-use/browser-use) — LLM-powered browser automation
- [LangChain](https://github.com/langchain-ai/langchain) — LLM orchestration
- [Playwright](https://playwright.dev/python/) — browser engine
- [Rich](https://github.com/Textualize/rich) — beautiful terminal output
- [Jinja2](https://jinja.palletsprojects.com/) — HTML email rendering

---

## License

MIT — do whatever you want with it.
