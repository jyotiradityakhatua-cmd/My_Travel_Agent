
from pydantic import BaseModel


class ItineraryRequest(BaseModel):

    source: str

    destination: str

    departure_date: str

    return_date: str

    days: int

