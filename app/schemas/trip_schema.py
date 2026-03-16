from typing import Optional
from pydantic import BaseModel


class TripInfo(BaseModel):
    origin: str
    destination: str
    budget: Optional[float] = None
    nights: Optional[int] = None
