from pydantic import BaseModel


class CostExtraction(BaseModel):
    flight_cost: float
    hotel_cost: float