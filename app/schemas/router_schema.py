from pydantic import BaseModel
from typing import Literal


class SupervisorRouter(BaseModel):
    next_step: Literal[
        "Flights",
        "Hotels",
        "Activities",
        "BudgetAnalyst",
        "FINISH"
    ]
    reasoning: str