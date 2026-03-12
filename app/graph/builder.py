from langgraph.graph import StateGraph, START, END

from app.graph.state import AgentState
from app.graph.supervisor import supervisor_node
from app.graph.nodes import (
    call_flights,
    call_hotels,
    call_activities,
    call_budget
)

builder = StateGraph(AgentState)

builder.add_node("Supervisor", supervisor_node)
builder.add_node("Flights", call_flights)
builder.add_node("Hotels", call_hotels)
builder.add_node("Activities", call_activities)
builder.add_node("BudgetAnalyst", call_budget)

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

for node in ["Flights", "Hotels", "Activities", "BudgetAnalyst"]:
    builder.add_edge(node, "Supervisor")

graph_app = builder.compile()