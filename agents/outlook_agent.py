"""
Outlook / Microsoft 365 Agent
Logs in and checks: meeting cancellations, urgent emails, today's calendar.
"""
from __future__ import annotations
import json, re
from browser_use import Agent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import config


TASK = """
You are a helpful assistant checking a student's Microsoft Outlook / 365 account.

Steps:
1. Navigate to https://outlook.office.com
2. Log in with email={email} and password={password}
3. Check the inbox for any emails received in the last 24 hours that contain words like
   "canceled", "cancelled", "rescheduled", "postponed", "no class", or "urgent".
4. Check the Calendar for today's events.

Return a JSON object (and ONLY the JSON, no extra text) with this schema:
{{
  "cancellations": [
    {{"subject": "...", "from": "...", "snippet": "..."}}
  ],
  "urgent_emails": [
    {{"subject": "...", "from": "...", "snippet": "..."}}
  ],
  "todays_events": [
    {{"title": "...", "time": "...", "location": "..."}}
  ],
  "error": null
}}
If you cannot log in or find data, set "error" to a short description.
"""


def _make_llm():
    if config.LLM_PROVIDER == "anthropic":
        return ChatAnthropic(model=config.LLM_MODEL, api_key=config.ANTHROPIC_API_KEY)
    return ChatOpenAI(model=config.LLM_MODEL, api_key=config.OPENAI_API_KEY)


async def run() -> dict:
    if not config.OUTLOOK_EMAIL:
        return {"error": "Outlook credentials not configured", "cancellations": [], "urgent_emails": [], "todays_events": []}

    task = TASK.format(email=config.OUTLOOK_EMAIL, password=config.OUTLOOK_PASSWORD)

    agent = Agent(task=task, llm=_make_llm())
    history = await agent.run()
    raw = history.final_result() or ""

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {"error": "Could not parse Outlook response", "cancellations": [], "urgent_emails": [], "todays_events": [], "raw": raw[:500]}
