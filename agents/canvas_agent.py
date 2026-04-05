"""
Canvas LMS Agent
Logs in and scrapes: upcoming assignments, quizzes, announcements.
"""
from __future__ import annotations
import json, re
from browser_use import Agent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import config


TASK = """
You are a helpful assistant checking a student's Canvas LMS dashboard.

Steps:
1. Navigate to {canvas_url}/login
2. Log in with email={email} and password={password}
3. Go to the Dashboard and then "Calendar" or "Upcoming" view.
4. Find ALL assignments, quizzes, or exams due within the next 48 hours.
5. Also check for any new Announcements posted today.
6. Check if any classes show a cancellation announcement.

Return a JSON object (and ONLY the JSON, no extra text) with this exact schema:
{{
  "upcoming_due": [
    {{"title": "...", "course": "...", "due": "ISO datetime string", "type": "assignment|quiz|exam"}}
  ],
  "announcements": [
    {{"course": "...", "title": "...", "body_snippet": "..."}}
  ],
  "class_cancellations": [
    {{"course": "...", "date": "...", "details": "..."}}
  ],
  "error": null
}}
If you cannot log in or find any data, set "error" to a short description.
"""


def _make_llm():
    if config.LLM_PROVIDER == "anthropic":
        return ChatAnthropic(model=config.LLM_MODEL, api_key=config.ANTHROPIC_API_KEY)
    return ChatOpenAI(model=config.LLM_MODEL, api_key=config.OPENAI_API_KEY)


async def run() -> dict:
    if not config.CANVAS_EMAIL:
        return {"error": "Canvas credentials not configured", "upcoming_due": [], "announcements": [], "class_cancellations": []}

    task = TASK.format(
        canvas_url=config.CANVAS_URL,
        email=config.CANVAS_EMAIL,
        password=config.CANVAS_PASSWORD,
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

    return {
        "error": "Could not parse Canvas response",
        "upcoming_due": [],
        "announcements": [],
        "class_cancellations": [],
        "raw": raw[:500],
    }
