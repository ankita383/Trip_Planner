from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.graph.builder import graph_app


app = FastAPI(title="Multi-Agent Travel Planner")


class TripQuery(BaseModel):
    user_query: str


@app.post("/generate-plan")
async def generate_plan(request: TripQuery):
    result = graph_app.invoke({
        "messages": [HumanMessage(content=request.user_query)],
        "next_node": "",
        "origin": "",
        "destination": "",
        "budget": None,
        "nights": 5,
        "flights_done": False,
        "hotels_done": False,
        "activities_done": False,
        "budget_done": False,
        "flight_prices": [],
        "hotel_prices": [],
        "last_agent": "",
        "approved": False,
        "feedback": None
    })

    history = []

    for m in result["messages"]:
        sender = (
            m.name if hasattr(m, "name") and m.name
            else "User"
        )

        history.append({
            "agent": sender,
            "message": m.content
        })

    return {
        "status": "complete",
        "plan": history
    }
