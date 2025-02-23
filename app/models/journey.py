from pydantic import BaseModel, Field
from datetime import datetime
from typing import List
from dataclasses import dataclass


class PathFlight(BaseModel):
    flight_number: str
    from_: str = Field(..., alias="from")
    to: str
    departure_time: datetime
    arrival_time: datetime

    class Config:
        populate_by_name = True


@dataclass
class Journey:
    connections: int
    path: List[PathFlight]

    def __lt__(self, other: "Journey") -> bool:
        return self.connections < other.connections
