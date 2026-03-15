from langchain_core.messages import HumanMessage, AIMessage
from app.agents.flight_agent import flight_agent
from app.agents.hotel_agent import hotel_agent
from app.agents.activity_agent import activity_agent
from app.agents.budget_agent import budget_agent


def call_flights(state):
    origin = state["origin"]
    destination = state["destination"]
    query = f"Find flights from {origin} to {destination}"

    if state.get("feedback"):
        query += f"\nUser feedback: {state['feedback']}"

    response = flight_agent.invoke({
        "messages": [
            HumanMessage(
                content=query
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
        "last_agent": "Flights",
        "feedback": None
    }


def call_hotels(state):
    destination = state["destination"]
    query = f"Find hotels in {destination}"

    if state.get("feedback"):
        query += f"\nUser feedback: {state['feedback']}"

    response = hotel_agent.invoke({
        "messages": [
            HumanMessage(
                content=query
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
        "last_agent": "Hotels",
        "feedback": None
    }


def call_activities(state):
    destination = state["destination"]
    query = f"Find tourist activities in {destination}"

    if state.get("feedback"):
        query += f"\nUser feedback: {state['feedback']}"

    response = activity_agent.invoke({
        "messages": [
            HumanMessage(
                content=query
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
        "last_agent": "Activities",
        "feedback": None
    }


def call_budget(state):
    review_message = HumanMessage(content="Calculate total travel cost.")

    if state.get("feedback"):
        review_message = HumanMessage(
            content=f"Calculate total travel cost.\nUser feedback: {state['feedback']}"
        )

    response = budget_agent.invoke({
        "messages": state["messages"][-3:] + [
            review_message
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
        "last_agent": "BudgetAnalyst",
        "feedback": None
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

        return {
            "approved": True,
            "feedback": None,
            "last_agent": agent,
            "next_node": "Supervisor"
        }

    feedback = input("Enter feedback: ").strip()
    print(f"{agent} will run again with your feedback...\n")

    return {
        "approved": False,
        "feedback": feedback,
        "last_agent": agent,
        "next_node": agent
    }
