from datetime import datetime
from typing import List
from pydantic import BaseModel


class FlightNode(BaseModel):
    """Represents a node (city) in the flight graph"""
    city_code: str
    name: str


class FlightEdge(BaseModel):
    """Represents an edge (flight) in the graph"""
    flight_number: str
    origin: str  # city code
    destination: str  # city code
    departure_time: datetime
    arrival_time: datetime 