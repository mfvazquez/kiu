from typing import List, Tuple
from app.models.journey import PathFlight
from ..flight_graph import FlightGraph


class DefaultJourneyPathBuilder:
    def build_path(
        self, path: List[Tuple[str, str, str]], graph: FlightGraph
    ) -> List[PathFlight]:
        flight_path = []
        for edge in path:
            flight = graph.get_flight_details(edge)
            # Pydantic handles from_ correctly at runtime
            flight_path.append(
                PathFlight(
                    flight_number=flight.flight_number,
                    from_=flight.departure_city,  # type: ignore[call-arg]
                    to=flight.arrival_city,
                    departure_time=flight.departure_datetime,
                    arrival_time=flight.arrival_datetime,
                )
            )
        return flight_path
