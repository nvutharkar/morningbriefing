"""
Workday Agent
Logs in and checks: upcoming shifts, schedule changes, new messages.
"""
from __future__ import annotations
import json, re
from browser_use import Agent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import config


TASK = """
You are a helpful assistant checking a student worker's Workday portal.

Steps:
1. Navigate to {workday_url}
2. Log in with email={email} and password={password}
3. Find the 'Time' or 'Schedule' section and look for the next 7 days of shifts.
4. Check for any messages or notifications about schedule changes.

Return a JSON object (and ONLY the JSON, no extra text) with this exact schema:
{{
  "shifts": [
    {{"date": "YYYY-MM-DD", "start": "HH:MM", "end": "HH:MM", "location": "..."}}
  ],
  "changes": [
    {{"description": "..."}}
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
    if not config.WORKDAY_URL or not config.WORKDAY_EMAIL:
        return {"error": "Workday credentials not configured", "shifts": [], "changes": []}

    task = TASK.format(
        workday_url=config.WORKDAY_URL,
        email=config.WORKDAY_EMAIL,
        password=config.WORKDAY_PASSWORD,
    )

    agent = Agent(task=task, llm=_make_llm())
    history = await agent.run()
    raw = history.final_result() or ""

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {"error": "Could not parse Workday response", "shifts": [], "changes": [], "raw": raw[:500]}
