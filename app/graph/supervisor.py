from langchain_core.messages import SystemMessage, HumanMessage
from app.config.settings import llm_supervisor, llm_worker
from app.schemas.trip_schema import TripInfo
from app.schemas.router_schema import SupervisorRouter


def supervisor_node(state):
    user_query = state["messages"][0].content
    if not state.get("origin") or not state.get("destination"):
        extractor = llm_worker.with_structured_output(TripInfo)
        trip = extractor.invoke([
            SystemMessage(content="Extract origin and destination cities."),
            HumanMessage(content=user_query)
        ])
        state["origin"] = trip.origin
        state["destination"] = trip.destination
    prompt = f"""
You are a travel supervisor responsible for coordinating multiple travel planning agents.

Available agents:

Flights → finds flight options between two cities  
Hotels → finds hotels in a city  
Activities → finds tourist attractions  
BudgetAnalyst → calculates total trip cost  

Current trip context:

Origin: {state["origin"]}
Destination: {state["destination"]}

Completed information:

Flights_done: {state["flights_done"]}
Hotels_done: {state["hotels_done"]}
Activities_done: {state["activities_done"]}
Budget_done: {state["budget_done"]}

Rules:

• Call an agent only if needed  
• Never call an agent whose task is already done  
• When everything is complete return FINISH
"""

    router = llm_supervisor.with_structured_output(SupervisorRouter)
    decision = router.invoke(
        [SystemMessage(content=prompt)] + state["messages"]
    )
    print(f"Supervisor → {decision.next_step}")
    return {
        "next_node": decision.next_step,
        "origin": state["origin"],
        "destination": state["destination"]
    }
