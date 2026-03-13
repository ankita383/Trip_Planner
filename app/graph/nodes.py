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
        "flights_done": True,
        "last_agent": "Flights"
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
        "hotels_done": True,
        "last_agent": "Hotels"
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
        "activities_done": True,
        "last_agent": "Activities"
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
        "budget_done": True,
        "last_agent": "BudgetAnalyst"
    }

def human_review(state):

    last_message = state["messages"][-1]
    agent_name = last_message.name if hasattr(last_message, 'name') else None

    if agent_name == "FlightAgent":
        agent = "Flights"
    elif agent_name == "HotelAgent":
        agent = "Hotels"
    elif agent_name == "ActivityAgent":
        agent = "Activities"
    elif agent_name == "BudgetAnalyst":
        agent = "BudgetAnalyst"
    else:
        agent = "Flights"

    print("\n---------------------------")
    print(f"HUMAN REVIEW AFTER {agent}")
    print("---------------------------\n")

    info = state["messages"][-1].content
    print(info)

    decision = input("\nApprove this result? (yes/no): ").strip().lower()

    if decision == "yes":

        print(f"{agent} approved.\n")

        next_node = "Supervisor"
        approved = True
        reset_flags = {}

    else:

        if agent == "BudgetAnalyst":
            print("Budget rejected, restarting planning process from Flights...\n")
            next_node = "Supervisor"
            approved = False
            # Reset all done flags to start over from Flights
            reset_flags = {
                "flights_done": False,
                "hotels_done": False,
                "activities_done": False,
                "budget_done": False
            }
        else:
            print(f"{agent} will run again...\n")
            next_node = agent
            approved = False
            reset_flags = {}

    return {
        "approved": approved,
        "last_agent": agent,
        "next_node": next_node,
        **reset_flags
    }