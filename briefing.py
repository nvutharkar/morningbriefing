"""
Briefing Generator
Takes raw data from all agents and produces a clean, human-readable morning summary.
"""
from __future__ import annotations
from datetime import datetime
from jinja2 import Template

TEMPLATE = """
╔══════════════════════════════════════════════════════════╗
║            ☀️  GOOD MORNING — Daily Briefing             ║
║                 {{ now }}                  
╚══════════════════════════════════════════════════════════╝

{% if canvas.error %}
📚 CANVAS  ⚠️  {{ canvas.error }}
{% else %}
📚 CANVAS
{% if canvas.upcoming_due %}
  Upcoming Deadlines (next 48 hrs):
  {% for item in canvas.upcoming_due %}
  • [{{ item.type | upper }}] {{ item.title }} — {{ item.course }}  ⏰ {{ item.due }}
  {% endfor %}
{% else %}
  ✅ No assignments or quizzes due in the next 48 hours.
{% endif %}
{% if canvas.class_cancellations %}
  Class Cancellations:
  {% for c in canvas.class_cancellations %}
  🚫 {{ c.course }} on {{ c.date }}: {{ c.details }}
  {% endfor %}
{% endif %}
{% if canvas.announcements %}
  Announcements:
  {% for a in canvas.announcements %}
  📢 [{{ a.course }}] {{ a.title }} — {{ a.body_snippet }}
  {% endfor %}
{% endif %}
{% endif %}

{% if workday.error %}
💼 WORKDAY  ⚠️  {{ workday.error }}
{% else %}
💼 WORKDAY — Upcoming Shifts
{% if workday.shifts %}
  {% for s in workday.shifts %}
  • {{ s.date }}  {{ s.start }} – {{ s.end }}  @ {{ s.location }}
  {% endfor %}
{% else %}
  ✅ No shifts scheduled in the next 7 days.
{% endif %}
{% if workday.changes %}
  Schedule Changes:
  {% for ch in workday.changes %}
  ⚠️  {{ ch.description }}
  {% endfor %}
{% endif %}
{% endif %}

{% if outlook.error %}
📧 OUTLOOK  ⚠️  {{ outlook.error }}
{% else %}
📧 OUTLOOK
{% if outlook.cancellations %}
  Cancellations / Reschedules:
  {% for e in outlook.cancellations %}
  🚫 {{ e.subject }} (from {{ e.from }}) — {{ e.snippet }}
  {% endfor %}
{% endif %}
{% if outlook.urgent_emails %}
  Urgent Emails:
  {% for e in outlook.urgent_emails %}
  🔴 {{ e.subject }} (from {{ e.from }}) — {{ e.snippet }}
  {% endfor %}
{% endif %}
{% if outlook.todays_events %}
  Today's Calendar:
  {% for ev in outlook.todays_events %}
  📅 {{ ev.time }}  {{ ev.title }}  {% if ev.location %}@ {{ ev.location }}{% endif %}
  {% endfor %}
{% else %}
  ✅ No calendar events for today.
{% endif %}
{% endif %}

{% if bank.error %}
🏦 BANK  ⚠️  {{ bank.error }}
{% else %}
🏦 BANK
{% if bank.balance is not none %}
  Balance: ${{ "%.2f" | format(bank.balance) }} {{ bank.currency }}
{% endif %}
{% if bank.overdraft_warning %}
  🚨 OVERDRAFT WARNING: {{ bank.overdraft_details }}
{% else %}
  ✅ Balance looks healthy.
{% endif %}
{% if bank.large_transactions %}
  Large Transactions (last 24 hrs):
  {% for t in bank.large_transactions %}
  • {{ t.date }}  {{ t.description }}  –${{ "%.2f" | format(t.amount) }}
  {% endfor %}
{% endif %}
{% endif %}

══════════════════════════════════════════════════════════
"""


def render_text(canvas: dict, workday: dict, outlook: dict, bank: dict) -> str:
    now = datetime.now().strftime("%A, %B %d %Y  %I:%M %p")
    return Template(TEMPLATE).render(canvas=canvas, workday=workday, outlook=outlook, bank=bank, now=now)


def render_html(canvas: dict, workday: dict, outlook: dict, bank: dict) -> str:
    """Returns a minimal HTML version of the briefing for email delivery."""
    now = datetime.now().strftime("%A, %B %d %Y  %I:%M %p")
    lines = []
    lines.append(f"<h2>☀️ Morning Briefing — {now}</h2>")

    # Canvas
    lines.append("<h3>📚 Canvas</h3>")
    if canvas.get("error"):
        lines.append(f"<p style='color:red'>⚠️ {canvas['error']}</p>")
    else:
        if canvas.get("upcoming_due"):
            lines.append("<ul>")
            for d in canvas["upcoming_due"]:
                lines.append(f"<li><b>{d['type'].upper()}</b>: {d['title']} — {d['course']} ⏰ {d['due']}</li>")
            lines.append("</ul>")
        else:
            lines.append("<p style='color:green'>✅ No assignments due in 48 hrs.</p>")
        for c in canvas.get("class_cancellations", []):
            lines.append(f"<p>🚫 <b>{c['course']}</b> — {c['details']}</p>")
        for a in canvas.get("announcements", []):
            lines.append(f"<p>📢 [{a['course']}] {a['title']}</p>")

    # Workday
    lines.append("<h3>💼 Workday</h3>")
    if workday.get("error"):
        lines.append(f"<p style='color:red'>⚠️ {workday['error']}</p>")
    else:
        if workday.get("shifts"):
            lines.append("<ul>")
            for s in workday["shifts"]:
                lines.append(f"<li>{s['date']}  {s['start']}–{s['end']} @ {s['location']}</li>")
            lines.append("</ul>")
        else:
            lines.append("<p style='color:green'>✅ No shifts this week.</p>")
        for ch in workday.get("changes", []):
            lines.append(f"<p>⚠️ {ch['description']}</p>")

    # Outlook
    lines.append("<h3>📧 Outlook</h3>")
    if outlook.get("error"):
        lines.append(f"<p style='color:red'>⚠️ {outlook['error']}</p>")
    else:
        for e in outlook.get("cancellations", []):
            lines.append(f"<p>🚫 {e['subject']} — {e['snippet']}</p>")
        for e in outlook.get("urgent_emails", []):
            lines.append(f"<p>🔴 {e['subject']} — {e['snippet']}</p>")
        if outlook.get("todays_events"):
            lines.append("<ul>")
            for ev in outlook["todays_events"]:
                loc = f" @ {ev['location']}" if ev.get("location") else ""
                lines.append(f"<li>📅 {ev['time']} {ev['title']}{loc}</li>")
            lines.append("</ul>")
        else:
            lines.append("<p style='color:green'>✅ No events today.</p>")

    # Bank
    lines.append("<h3>🏦 Bank</h3>")
    if bank.get("error"):
        lines.append(f"<p style='color:red'>⚠️ {bank['error']}</p>")
    else:
        if bank.get("balance") is not None:
            lines.append(f"<p>Balance: <b>${bank['balance']:.2f}</b> {bank.get('currency','USD')}</p>")
        if bank.get("overdraft_warning"):
            lines.append(f"<p style='color:red'>🚨 {bank['overdraft_details']}</p>")
        else:
            lines.append("<p style='color:green'>✅ Balance looks healthy.</p>")
        for t in bank.get("large_transactions", []):
            lines.append(f"<p>{t['date']}: {t['description']} –${t['amount']:.2f}</p>")

    return "<html><body style='font-family:sans-serif;max-width:600px;margin:auto'>" + "\n".join(lines) + "</body></html>"
