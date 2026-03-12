from langchain_core.messages import HumanMessage, AIMessage
from app.agents.flight_agent import flight_agent
from app.agents.hotel_agent import hotel_agent
from app.agents.activity_agent import activity_agent
from app.agents.budget_agent import budget_agent


def call_flights(state):
    origin = state["origin"]
    destination = state["destination"]
    response = flight_agent.invoke({
        "messages": [
            HumanMessage(
                content=f"Find flights from {origin} to {destination}"
            )
        ]
    })
    content = response["messages"][-1].content
    return {
        "messages": [
            AIMessage(
                content=f"FLIGHT DATA FOUND: {content}",
                name="FlightAgent"
            )
        ],
        "flights_done": True
    }


def call_hotels(state):
    destination = state["destination"]
    response = hotel_agent.invoke({
        "messages": [
            HumanMessage(
                content=f"Find hotels in {destination}"
            )
        ]
    })
    content = response["messages"][-1].content
    return {
        "messages": [
            AIMessage(
                content=f"HOTEL DATA FOUND: {content}",
                name="HotelAgent"
            )
        ],
        "hotels_done": True
    }


def call_activities(state):
    destination = state["destination"]
    response = activity_agent.invoke({
        "messages": [
            HumanMessage(
                content=f"Find tourist activities in {destination}"
            )
        ]
    })
    content = response["messages"][-1].content
    return {
        "messages": [
            AIMessage(
                content=f"ACTIVITY DATA FOUND: {content}",
                name="ActivityAgent"
            )
        ],
        "activities_done": True
    }


def call_budget(state):
    response = budget_agent.invoke({
        "messages": state["messages"][-3:] + [
            HumanMessage(content="Calculate total travel cost.")
        ]
    })
    content = response["messages"][-1].content
    return {
        "messages": [
            AIMessage(
                content=f"BUDGET ANALYSIS COMPLETE: {content}",
                name="BudgetAnalyst"
            )
        ],
        "budget_done": True
    }