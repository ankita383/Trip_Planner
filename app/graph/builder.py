from langgraph.graph import StateGraph, START, END
from app.graph.state import AgentState
from app.graph.supervisor import supervisor_node
from app.graph.nodes import (
    call_flights,
    call_hotels,
    call_activities,
    call_budget,
    human_review
)

builder = StateGraph(AgentState)

builder.add_node("Supervisor", supervisor_node)
builder.add_node("Flights", call_flights)
builder.add_node("Hotels", call_hotels)
builder.add_node("Activities", call_activities)
builder.add_node("BudgetAnalyst", call_budget)
builder.add_node("HumanReview", human_review)

builder.add_edge(START, "Supervisor")

builder.add_conditional_edges(
    "Supervisor",
    lambda x: x["next_node"],
    {
        "Flights": "Flights",
        "Hotels": "Hotels",
        "Activities": "Activities",
        "BudgetAnalyst": "BudgetAnalyst",
        "FINISH": END
    }
)

builder.add_edge("Flights", "HumanReview")
builder.add_edge("Hotels", "HumanReview")
builder.add_edge("Activities", "HumanReview")
builder.add_edge("BudgetAnalyst", "HumanReview")

builder.add_conditional_edges(
    "HumanReview",
    lambda x: "Supervisor" if x.get("approved") else x.get("last_agent"),
    {
        "Supervisor": "Supervisor",
        "Flights": "Flights",
        "Hotels": "Hotels",
        "Activities": "Activities",
        "BudgetAnalyst": "BudgetAnalyst",
    }
)

graph_app = builder.compile()
