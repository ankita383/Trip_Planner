from langchain.agents import create_agent
from app.config.settings import llm_worker
from app.tools.budget_tool import calculate_budget_manual

budget_agent = create_agent(
    model=llm_worker,
    tools=[calculate_budget_manual],
    system_prompt="""
You are a travel budget analyst.

Your job:
1. Extract flight_cost and hotel_cost from the conversation.
2. If hotel cost is per night, multiply it yourself before calling the tool.

CRITICAL RULES:
- Tool arguments must be pure numbers.
- Never send mathematical expressions like 15000*7.
- Always calculate the final number first.

Example:

Flight cost: 20000  
Hotel: 15000 per night for 7 nights  

You MUST call the tool with:

flight_cost = 20000
hotel_cost = 105000
"""
)