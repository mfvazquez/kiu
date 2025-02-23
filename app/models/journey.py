from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List
from dataclasses import dataclass


class PathFlight(BaseModel):
    flight_number: str
    from_: str = Field(..., alias="from")
    to: str
    departure_time: datetime
    arrival_time: datetime

    model_config = ConfigDict(populate_by_name=True)


@dataclass
class Journey:
    connections: int
    path: List[PathFlight]

    def __lt__(self, other: "Journey") -> bool:
        return self.connections < other.connections
