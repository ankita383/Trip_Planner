from typing import Annotated, Any, Optional, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

    next_node: str

    origin: str
    destination: str
    budget: Optional[float]
    nights: int

    flights_done: bool
    hotels_done: bool
    activities_done: bool
    budget_done: bool
    flight_prices: list[dict[str, Any]]
    hotel_prices: list[dict[str, Any]]
    last_agent: str
    approved: bool
    feedback: Optional[str]
