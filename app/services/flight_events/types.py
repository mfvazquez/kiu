from datetime import datetime
from pydantic import BaseModel


class FlightEvent(BaseModel):
    flight_number: str
    departure_city: str
    arrival_city: str
    departure_datetime: datetime
    arrival_datetime: datetime
