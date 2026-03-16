from langchain_core.messages import SystemMessage, HumanMessage
from app.config.settings import llm_supervisor, llm_worker
from app.schemas.trip_schema import TripInfo
from app.schemas.router_schema import SupervisorRouter


AGENT_ORDER = ["Flights", "Hotels", "Activities", "BudgetAnalyst"]


def _is_done(state, agent_name):
    done_flags = {
        "Flights": state["flights_done"],
        "Hotels": state["hotels_done"],
        "Activities": state["activities_done"],
        "BudgetAnalyst": state["budget_done"],
    }
    return done_flags.get(agent_name, False)


def _next_unfinished_agent(state, start_from=None):
    start_index = 0
    if start_from in AGENT_ORDER:
        start_index = AGENT_ORDER.index(start_from) + 1

    for agent_name in AGENT_ORDER[start_index:]:
        if not _is_done(state, agent_name):
            return agent_name

    return "FINISH"


def supervisor_node(state):
    user_query = state["messages"][0].content
    if (
        not state.get("origin")
        or not state.get("destination")
        or "budget" not in state
    ):
        extractor = llm_worker.with_structured_output(TripInfo)
        trip = extractor.invoke([
            SystemMessage(content="""
Extract the trip details from the user's request.

Return:
- origin
- destination
- budget
- nights

Budget rules:
- Convert values like "1 lakh" to 100000
- Convert values like "2 lakh INR" to 200000
- Convert values like "50k" to 50000
- Convert values like "budget 75000" or "under 50000" to the numeric amount
- If no budget is provided, return null for budget
- Return only the numeric value for budget, with no currency symbols or text

Night rules:
- Extract the number of nights if the user mentions trip duration like "for 5 nights"
- If nights are not provided, return null for nights
"""),
            HumanMessage(content=user_query)
        ])
        state["origin"] = trip.origin
        state["destination"] = trip.destination
        state["budget"] = trip.budget
        state["nights"] = trip.nights if trip.nights is not None else state.get("nights", 5)
    prompt = f"""
You are a travel supervisor responsible for coordinating multiple travel planning agents.

User query: {user_query}

Available agents:

Flights -> finds flight options between two cities
Hotels -> finds hotels in a city
Activities -> finds tourist attractions
BudgetAnalyst -> calculates total trip cost

Current trip context:

Origin: {state["origin"]}
Destination: {state["destination"]}
Budget: {state.get("budget")}
Nights: {state.get("nights")}

Completed information:

Flights_done: {state["flights_done"]}
Hotels_done: {state["hotels_done"]}
Activities_done: {state["activities_done"]}
Budget_done: {state["budget_done"]}

Rules:

- Analyze the user query to determine which travel aspects are requested (flights, hotels, activities, budget)
- If the query is to plan a complete trip, call all agents in order: Flights, Hotels, Activities, BudgetAnalyst
- IMPORTANT: Only call agents whose _done flag is False. Never call an agent if its _done is True.
- Call agents in the logical order: Flights first, then Hotels, then Activities, then BudgetAnalyst
- Call BudgetAnalyst only after all other relevant agents are done (their _done is True)
- When all relevant _done flags are True, return FINISH
- If nothing is requested or all relevant tasks are done, return FINISH
- Do not repeat agents that are already done
"""

    router = llm_supervisor.with_structured_output(SupervisorRouter)
    decision = router.invoke(
        [SystemMessage(content=prompt)] + state["messages"]
    )

    next_step = decision.next_step
    if next_step != "FINISH" and _is_done(state, next_step):
        next_step = _next_unfinished_agent(state, start_from=next_step)

    print(f"Supervisor -> {next_step}")
    return {
        "next_node": next_step,
        "origin": state["origin"],
        "destination": state["destination"],
        "budget": state.get("budget"),
        "nights": state.get("nights", 5)
    }
