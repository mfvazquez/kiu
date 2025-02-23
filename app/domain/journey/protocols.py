from typing import Protocol, List, Tuple
from datetime import datetime, date

from app.models.journey import Journey, PathFlight
from ..flight_graph import FlightGraph


class JourneyPathBuilder(Protocol):
    def build_path(
        self, path: List[Tuple[str, str, str]], graph: FlightGraph
    ) -> List[PathFlight]:
        """Build a journey path from graph path"""
        ...


class JourneySorter(Protocol):
    def sort(self, journeys: List[Journey]) -> List[Journey]:
        """Sort journeys by defined criteria"""
        ...


class JourneyValidator(Protocol):

    def is_valid_connection(
        self, arrival_time: datetime, departure_time: datetime
    ) -> bool:
        """Check if connection time between flights is valid"""
        ...

    def is_valid_departure_date(
        self, flight_datetime: datetime, departure_date: date
    ) -> bool:
        """Check if flight departs on or after the departure date"""
        ...

    def is_valid_total_time(self, journey: Journey) -> bool:
        """Check if total journey time is within limits"""
        ...
