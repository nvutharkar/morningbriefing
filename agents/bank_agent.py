"""
Bank Agent
Logs in and fetches: current balance, any overdraft warnings, large recent transactions.
"""
from __future__ import annotations
import json, re
from browser_use import Agent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import config


TASK = """
You are a helpful assistant checking a student's online bank account.

Steps:
1. Navigate to {bank_url}
2. Log in with username={username} and password={password}
3. Find the checking account balance (or the primary account balance).
4. Check for any overdraft fees or negative balance warnings.
5. List any large transactions (over $50) posted in the last 24 hours.

Return a JSON object (and ONLY the JSON, no extra text) with this schema:
{{
  "balance": 0.00,
  "currency": "USD",
  "overdraft_warning": false,
  "overdraft_details": "",
  "large_transactions": [
    {{"description": "...", "amount": 0.00, "date": "YYYY-MM-DD"}}
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
    if not config.BANK_URL or not config.BANK_USERNAME:
        return {"error": "Bank credentials not configured", "balance": None, "overdraft_warning": False, "large_transactions": []}

    task = TASK.format(
        bank_url=config.BANK_URL,
        username=config.BANK_USERNAME,
        password=config.BANK_PASSWORD,
    )

    agent = Agent(task=task, llm=_make_llm())
    history = await agent.run()
    raw = history.final_result() or ""

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            if data.get("balance") is not None and data["balance"] < config.OVERDRAFT_THRESHOLD:
                data["overdraft_warning"] = True
                data["overdraft_details"] = f"Balance ${data['balance']:.2f} is below threshold ${config.OVERDRAFT_THRESHOLD:.2f}"
            return data
        except json.JSONDecodeError:
            pass

    return {"error": "Could not parse bank response", "balance": None, "overdraft_warning": False, "large_transactions": [], "raw": raw[:500]}
