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
<<<<<<< HEAD

    # Check if all tasks are done
    if state.get("flights_done", False) and state.get("hotels_done", False) and state.get("activities_done", False) and state.get("budget_done", False):
        decision = type('Decision', (), {'next_step': 'FINISH'})()
    else:
        prompt = f"""
=======
    prompt = f"""
>>>>>>> c1316848e5c722600af77cbc022a4ef2a5b2351a
You are a travel supervisor responsible for coordinating multiple travel planning agents.

User query: {user_query}

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

• Analyze the user query to determine which travel aspects are requested (flights, hotels, activities, budget)
• If the query is to plan a complete trip, call all agents in order: Flights, Hotels, Activities, BudgetAnalyst
• IMPORTANT: Only call agents whose _done flag is False. Never call an agent if its _done is True.
• Call agents in the logical order: Flights first, then Hotels, then Activities, then BudgetAnalyst
• Call BudgetAnalyst only after all other relevant agents are done (their _done is True)
• When all relevant _done flags are True, return FINISH
• If nothing is requested or all relevant tasks are done, return FINISH
• Do not repeat agents that are already done
"""
<<<<<<< HEAD
        router = llm_supervisor.with_structured_output(SupervisorRouter)
        decision = router.invoke(
            [SystemMessage(content=prompt)] + state["messages"]
        )
=======

    router = llm_supervisor.with_structured_output(SupervisorRouter)
    decision = router.invoke(
        [SystemMessage(content=prompt)] + state["messages"]
    )
>>>>>>> c1316848e5c722600af77cbc022a4ef2a5b2351a
    print(f"Supervisor → {decision.next_step}")
    return {
        "next_node": decision.next_step,
        "origin": state["origin"],
        "destination": state["destination"]
    }
