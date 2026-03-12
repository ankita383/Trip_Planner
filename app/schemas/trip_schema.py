from pydantic import BaseModel


class TripInfo(BaseModel):
    origin: str
    destination: str