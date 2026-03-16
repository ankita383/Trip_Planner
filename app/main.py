import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from app.graph.builder import graph_app

app = FastAPI(title="Multi-Agent Travel Planner")


class TripQuery(BaseModel):
    user_query: str


class ResumeRequest(BaseModel):
    thread_id: str
    approved: bool
    feedback: Optional[str] = None    
    preference: Optional[str] = None  


def _extract_history(state: dict) -> list[dict]:
    history = []
    for m in state["messages"]:
        sender = (
            m.name if hasattr(m, "name") and m.name
            else "User"
        )
        history.append({"agent": sender, "message": m.content})
    return history


def _find_interrupt(result: dict) -> dict | None:
    """
    LangGraph surfaces interrupt payloads under the '__interrupt__' key
    in the last chunk when using invoke(). Extract it if present.
    """
    interrupts = result.get("__interrupt__")
    if interrupts:
        return interrupts[0].value
    return None


@app.post("/generate-plan")
async def generate_plan(request: TripQuery):
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    result = graph_app.invoke(
        {
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
            "feedback": None,
            "preferences": [],
        },
        config=config,
    )

    interrupt_payload = _find_interrupt(result)
    if interrupt_payload:
        return {
            "status": "awaiting_review",
            "thread_id": thread_id,
            "pending_review": interrupt_payload,
            "message": "Agent output is ready for your review. Call POST /resume to approve or reject."
        }

    return {
        "status": "complete",
        "thread_id": thread_id,
        "plan": _extract_history(result)
    }


@app.post("/resume")
async def resume(request: ResumeRequest):
    config = {"configurable": {"thread_id": request.thread_id}}

    snapshot = graph_app.get_state(config)
    if not snapshot or not snapshot.next:
        raise HTTPException(
            status_code=404,
            detail="No paused graph found for this thread_id. It may have already completed."
        )

    result = graph_app.invoke(
        Command(resume={
            "approved": request.approved,
            "feedback": request.feedback or None,
            "preference": request.preference or None
        }),
        config=config
    )

    interrupt_payload = _find_interrupt(result)
    if interrupt_payload:
        return {
            "status": "awaiting_review",
            "thread_id": request.thread_id,
            "pending_review": interrupt_payload,
            "message": "Next agent output is ready for your review. Call POST /resume again."
        }

    return {
        "status": "complete",
        "thread_id": request.thread_id,
        "plan": _extract_history(result)
    }