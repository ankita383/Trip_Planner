from pydantic import BaseModel, Field


class FlightOption(BaseModel):
    airline: str
    price: float


class FlightSearchResult(BaseModel):
    flights: list[FlightOption] = Field(default_factory=list)


class HotelOption(BaseModel):
    name: str
    price_per_night: float


class HotelSearchResult(BaseModel):
    hotels: list[HotelOption] = Field(default_factory=list)
