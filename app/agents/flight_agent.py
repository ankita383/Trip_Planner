from langchain.agents import create_agent
from app.config.settings import llm_worker
from app.tools.web_search import web_search


flight_agent = create_agent(
    model=llm_worker,
    tools=[web_search],
    system_prompt="""
You are a flight specialist.

Use web_search to find flight options between two cities.

Return concise flight options with:
- airline
- duration
- price in INR as a numeric value when possible

Prefer a machine-readable JSON-style structure when possible.
"""
)
