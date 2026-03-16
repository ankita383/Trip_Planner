from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.types import interrupt, Command
from app.config.settings import llm_worker
from app.agents.flight_agent import flight_agent
from app.agents.hotel_agent import hotel_agent
from app.agents.activity_agent import activity_agent
from app.schemas.search_schema import FlightSearchResult, HotelSearchResult
from app.tools.budget_tool import calculate_budget_manual


def _parse_flights(raw_content):
    extractor = llm_worker.with_structured_output(FlightSearchResult)
    parsed = extractor.invoke([
        SystemMessage(content="""
Extract structured flight options from the provided text.

Rules:
- Return only flights that include a price.
- Convert prices to numeric INR values.
- If the price is not available or unknown, set it to null.
- If no valid flights are present, return an empty list.
"""),
        HumanMessage(content=raw_content)
    ])
    # Filter out any flights where price is null
    return [
        flight.model_dump()
        for flight in parsed.flights
        if flight.price is not None
    ]


def _parse_hotels(raw_content):
    extractor = llm_worker.with_structured_output(HotelSearchResult)
    parsed = extractor.invoke([
        SystemMessage(content="""
Extract structured hotel options from the provided text.

Rules:
- Return only hotels that include a per-night price.
- Convert prices to numeric INR values.
- If the price is not available or unknown, set it to null.
- If no valid hotels are present, return an empty list.
"""),
        HumanMessage(content=raw_content)
    ])
    # Filter out any hotels where price_per_night is null
    return [
        hotel.model_dump()
        for hotel in parsed.hotels
        if hotel.price_per_night is not None
    ]


def _format_flights(flights):
    if not flights:
        return "No structured flight prices found."
    lines = [
        f"{flight['airline']} - INR {flight['price']:.2f}"
        for flight in flights
    ]
    return "\n".join(lines)


def _format_hotels(hotels):
    if not hotels:
        return "No structured hotel prices found."
    lines = [
        f"{hotel['name']} - INR {hotel['price_per_night']:.2f}/night"
        for hotel in hotels
    ]
    return "\n".join(lines)


def _format_preferences(preferences):
    """Format accumulated preferences as context for agents."""
    if not preferences:
        return ""
    lines = "\n".join(f"- {p}" for p in preferences)
    return f"\n\nUser preferences from earlier decisions:\n{lines}"


def call_flights(state):
    origin = state["origin"]
    destination = state["destination"]
    query = f"Find flights from {origin} to {destination}"

    if state.get("feedback"):
        query += f"\nUser feedback: {state['feedback']}"

    query += _format_preferences(state.get("preferences"))

    response = flight_agent.invoke({
        "messages": [HumanMessage(content=query)]
    })
    raw_content = response["messages"][-1].content
    flight_prices = _parse_flights(raw_content)
    return {
        "messages": [
            AIMessage(
                content=f"FLIGHT DATA FOUND:\n{_format_flights(flight_prices)}",
                name="FlightAgent"
            )
        ],
        "flights_done": True,
        "flight_prices": flight_prices,
        "last_agent": "Flights",
        "feedback": None
    }


def call_hotels(state):
    destination = state["destination"]
    query = f"Find hotels in {destination}"

    if state.get("feedback"):
        query += f"\nUser feedback: {state['feedback']}"

    query += _format_preferences(state.get("preferences"))

    response = hotel_agent.invoke({
        "messages": [HumanMessage(content=query)]
    })
    raw_content = response["messages"][-1].content
    hotel_prices = _parse_hotels(raw_content)
    return {
        "messages": [
            AIMessage(
                content=f"HOTEL DATA FOUND:\n{_format_hotels(hotel_prices)}",
                name="HotelAgent"
            )
        ],
        "hotels_done": True,
        "hotel_prices": hotel_prices,
        "last_agent": "Hotels",
        "feedback": None
    }


def call_activities(state):
    destination = state["destination"]
    query = f"Find tourist activities in {destination}"

    if state.get("feedback"):
        query += f"\nUser feedback: {state['feedback']}"

    query += _format_preferences(state.get("preferences"))

    response = activity_agent.invoke({
        "messages": [HumanMessage(content=query)]
    })
    content = response["messages"][-1].content
    return {
        "messages": [
            AIMessage(
                content=f"ACTIVITY DATA FOUND: {content}",
                name="ActivityAgent"
            )
        ],
        "activities_done": True,
        "last_agent": "Activities",
        "feedback": None
    }


def call_budget(state):
    budget_limit = state.get("budget")
    if budget_limit is None:
        budget_limit = 250000
    nights = state.get("nights", 5) or 5

    flight_values = [
        float(flight["price"])
        for flight in state.get("flight_prices", [])
        if flight.get("price") is not None
    ]
    hotel_values = [
        float(hotel["price_per_night"])
        for hotel in state.get("hotel_prices", [])
        if hotel.get("price_per_night") is not None
    ]

    if not flight_values or not hotel_values:
        missing_sources = []
        if not flight_values:
            missing_sources.append("flight prices")
        if not hotel_values:
            missing_sources.append("hotel prices")

        content = (
            "Unable to calculate budget from retrieved values because "
            f"structured {' and '.join(missing_sources)} were not available."
        )
        return {
            "messages": [
                AIMessage(
                    content=f"BUDGET ANALYSIS COMPLETE: {content}",
                    name="BudgetAnalyst"
                )
            ],
            "budget_done": True,
            "last_agent": "BudgetAnalyst",
            "feedback": None
        }

    flight_avg = sum(flight_values) / len(flight_values)
    hotel_avg = sum(hotel_values) / len(hotel_values)
    hotel_total = hotel_avg * nights

    budget_result = calculate_budget_manual.invoke({
        "flight_cost": round(flight_avg, 2),
        "hotel_cost": round(hotel_total, 2),
        "budget_limit": float(budget_limit)
    })

    content = (
        f"Average flight cost: INR {flight_avg:.2f}\n"
        f"Average hotel cost per night: INR {hotel_avg:.2f}\n"
        f"Nights: {nights}\n"
        f"Total hotel cost: INR {hotel_total:.2f}\n"
        f"Budget limit: INR {float(budget_limit):.2f}\n"
        f"Total: INR {budget_result['total']:.2f}\n"
        f"Status: {budget_result['status']}"
    )
    return {
        "messages": [
            AIMessage(
                content=f"BUDGET ANALYSIS COMPLETE: {content}",
                name="BudgetAnalyst"
            )
        ],
        "budget_done": True,
        "last_agent": "BudgetAnalyst",
        "feedback": None
    }


def human_review(state):
    """
    Suspends mid-execution using interrupt().
    Sends the last agent's output to the client for review.
    Resumes when /resume calls Command(resume={...}) with the human decision.

    On approval: optionally accepts a preference note (e.g. "I will take IndiGo flight")
                 which is appended to the cumulative preferences list in state.
    On rejection: accepts feedback to re-run the same agent with corrections.
    """
    last_agent = state.get("last_agent", "Flights")
    last_message = state["messages"][-1]

    decision = interrupt({
        "agent": last_agent,
        "message": last_message.content,
        "instructions": (
            "Approve or reject. "
            "If approving, you may add an optional preference note (e.g. 'I will take IndiGo flight'). "
            "If rejecting, provide feedback for the agent to try again."
        )
    })

    approved = decision.get("approved", False)
    feedback = decision.get("feedback", None)
    preference = decision.get("preference", None)

    existing_preferences = state.get("preferences") or []
    updated_preferences = existing_preferences + [preference] if preference else existing_preferences

    if approved:
        return Command(
            goto="Supervisor",
            update={
                "approved": True,
                "feedback": None,
                "last_agent": last_agent,
                "preferences": updated_preferences
            }
        )

    return Command(
        goto=last_agent,
        update={
            "approved": False,
            "feedback": feedback,
            "last_agent": last_agent,
            "preferences": updated_preferences
        }
    )