from langchain.agents import create_agent
from app.config.settings import llm_worker
from app.tools.web_search import web_search


activity_agent = create_agent(
    model=llm_worker,
    tools=[web_search],
    system_prompt="""
You are an activity planner.

Use web_search to find 5 tourist activities.

Return:
- activity name
- entry fee in INR
"""
)