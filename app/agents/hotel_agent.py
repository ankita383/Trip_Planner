from langchain.agents import create_agent
from app.config.settings import llm_worker
from app.tools.web_search import web_search


hotel_agent = create_agent(
    model=llm_worker,
    tools=[web_search],
    system_prompt="""
You are a hotel expert.

Use web_search to find 5 hotels in the destination city.

Return concise hotel options with:
- hotel name
- rating
- price per night in INR as a numeric value when possible

Prefer a machine-readable JSON-style structure when possible.
"""
)
