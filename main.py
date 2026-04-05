"""
MorningBriefing — main entry point.

Usage:
    python main.py              # run once right now
    python main.py --schedule   # run daily at BRIEFING_HOUR:BRIEFING_MINUTE (from .env)
    python main.py --demo       # run with fake data (no credentials needed)
"""
from __future__ import annotations
import asyncio, argparse, sys
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
import schedule, time

import config
from briefing import render_text, render_html
from notifier import send_email

console = Console()


# ── Demo / stub data ──────────────────────────────────────────────────────────
DEMO_DATA = {
    "canvas": {
        "upcoming_due": [
            {"title": "CS 301 Midterm Study Guide Submission", "course": "CS 301", "due": "2026-04-06T23:59:00", "type": "assignment"},
            {"title": "Quiz 4 — Recursion", "course": "CS 301", "due": "2026-04-07T11:59:00", "type": "quiz"},
        ],
        "announcements": [
            {"course": "MATH 220", "title": "Office hours moved", "body_snippet": "Office hours on Friday are moved to 3 PM..."},
        ],
        "class_cancellations": [
            {"course": "ENG 101", "date": "2026-04-06", "details": "Professor out sick — no class today."},
        ],
        "error": None,
    },
    "workday": {
        "shifts": [
            {"date": "2026-04-06", "start": "16:00", "end": "20:00", "location": "Campus Library Desk"},
            {"date": "2026-04-08", "start": "10:00", "end": "14:00", "location": "Campus Library Desk"},
        ],
        "changes": [],
        "error": None,
    },
    "outlook": {
        "cancellations": [
            {"subject": "ENG 101 — Class Canceled Today", "from": "prof.jones@university.edu", "snippet": "Due to illness I am canceling today's class..."},
        ],
        "urgent_emails": [],
        "todays_events": [
            {"title": "CS 301 Lecture", "time": "9:00 AM", "location": "Olson Hall 204"},
            {"title": "Study Group — Algorithms", "time": "2:00 PM", "location": "Library Room 3B"},
        ],
        "error": None,
    },
    "bank": {
        "balance": 18.43,
        "currency": "USD",
        "overdraft_warning": True,
        "overdraft_details": "Balance $18.43 is below threshold $25.00",
        "large_transactions": [
            {"description": "Amazon.com", "amount": 67.99, "date": "2026-04-05"},
        ],
        "error": None,
    },
}


# ── Core runner ───────────────────────────────────────────────────────────────
async def run_briefing(demo: bool = False) -> None:
    console.rule("[bold yellow]☀️  Morning Briefing[/]")

    if demo:
        console.print("[dim]Running in DEMO mode with sample data...[/dim]\n")
        canvas_data   = DEMO_DATA["canvas"]
        workday_data  = DEMO_DATA["workday"]
        outlook_data  = DEMO_DATA["outlook"]
        bank_data     = DEMO_DATA["bank"]
    else:
        from agents import canvas_agent, workday_agent, outlook_agent, bank_agent

        console.print("[cyan]▶ Checking Canvas...[/]")
        canvas_data = await canvas_agent.run()

        console.print("[cyan]▶ Checking Workday...[/]")
        workday_data = await workday_agent.run()

        console.print("[cyan]▶ Checking Outlook...[/]")
        outlook_data = await outlook_agent.run()

        console.print("[cyan]▶ Checking Bank...[/]")
        bank_data = await bank_agent.run()

    text_brief = render_text(canvas_data, workday_data, outlook_data, bank_data)
    html_brief = render_html(canvas_data, workday_data, outlook_data, bank_data)

    console.print(Panel(text_brief, title="Your Morning Summary", border_style="yellow"))

    if not demo:
        send_email(text_brief, html_brief)

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    with open(f"briefing_{ts}.html", "w") as f:
        f.write(html_brief)
    console.print(f"[green]Saved briefing_{ts}.html[/]")


def scheduled_job():
    asyncio.run(run_briefing(demo=False))


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="MorningBriefing Agent")
    parser.add_argument("--schedule", action="store_true", help="Run on a daily schedule")
    parser.add_argument("--demo",     action="store_true", help="Run with demo data (no credentials needed)")
    args = parser.parse_args()

    if args.schedule:
        t = f"{config.BRIEFING_HOUR:02d}:{config.BRIEFING_MINUTE:02d}"
        schedule.every().day.at(t).do(scheduled_job)
        console.print(f"[green]Scheduler started — briefing will run daily at {t}[/]")
        console.print("[dim]Press Ctrl-C to stop.[/dim]")
        while True:
            schedule.run_pending()
            time.sleep(30)
    else:
        asyncio.run(run_briefing(demo=args.demo))


if __name__ == "__main__":
    main()
