import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM ──────────────────────────────────────────────────────────────────────
OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_PROVIDER     = os.getenv("LLM_PROVIDER", "openai")   # "openai" | "anthropic"
LLM_MODEL        = os.getenv("LLM_MODEL", "gpt-4o-mini")

# ── Canvas ────────────────────────────────────────────────────────────────────
CANVAS_URL       = os.getenv("CANVAS_URL", "https://canvas.instructure.com")
CANVAS_EMAIL     = os.getenv("CANVAS_EMAIL", "")
CANVAS_PASSWORD  = os.getenv("CANVAS_PASSWORD", "")

# ── Workday ───────────────────────────────────────────────────────────────────
WORKDAY_URL      = os.getenv("WORKDAY_URL", "")           # e.g. https://wd5.myworkday.com/myuniversity
WORKDAY_EMAIL    = os.getenv("WORKDAY_EMAIL", "")
WORKDAY_PASSWORD = os.getenv("WORKDAY_PASSWORD", "")

# ── Outlook / Microsoft 365 ───────────────────────────────────────────────────
OUTLOOK_EMAIL    = os.getenv("OUTLOOK_EMAIL", "")
OUTLOOK_PASSWORD = os.getenv("OUTLOOK_PASSWORD", "")

# ── Bank ──────────────────────────────────────────────────────────────────────
BANK_URL         = os.getenv("BANK_URL", "")
BANK_USERNAME    = os.getenv("BANK_USERNAME", "")
BANK_PASSWORD    = os.getenv("BANK_PASSWORD", "")
OVERDRAFT_THRESHOLD = float(os.getenv("OVERDRAFT_THRESHOLD", "25.0"))  # warn if balance < $25

# ── Notification ─────────────────────────────────────────────────────────────
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "")  # your email for the morning briefing
SMTP_HOST          = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT          = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER          = os.getenv("SMTP_USER", "")
SMTP_PASSWORD      = os.getenv("SMTP_PASSWORD", "")       # gmail app password

# ── Schedule ──────────────────────────────────────────────────────────────────
BRIEFING_HOUR    = int(os.getenv("BRIEFING_HOUR", "6"))   # 6 AM local time
BRIEFING_MINUTE  = int(os.getenv("BRIEFING_MINUTE", "0"))
