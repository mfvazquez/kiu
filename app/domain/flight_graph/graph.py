import networkx as nx
from typing import List, Tuple

from app.services.flight_events import FlightEvent
from .exceptions import EdgeNotFoundError


class FlightGraph:
    """
    Manages the flight network using a MultiDiGraph.
    Multiple flights can exist between the same cities.
    Flights are directional (from origin to destination).
    """

    def __init__(self):
        """Initialize the flight graph"""
        self.graph = nx.MultiDiGraph()

    def _create_edge_key(self, flight: FlightEvent) -> str:
        """Creates a unique key for a flight edge"""
        departure_datetime_iso = flight.departure_datetime.isoformat()
        return f"{flight.flight_number}_{departure_datetime_iso}"

    def _ensure_nodes_exist(self, flight: FlightEvent) -> None:
        """Ensures both cities exist as nodes in the graph"""
        if not self.graph.has_node(flight.departure_city):
            self.graph.add_node(flight.departure_city)
        if not self.graph.has_node(flight.arrival_city):
            self.graph.add_node(flight.arrival_city)

    def add_flight(self, flight: FlightEvent) -> None:
        """Add a flight to the graph"""
        self._ensure_nodes_exist(flight)
        edge_key = self._create_edge_key(flight)

        self.graph.add_edge(
            flight.departure_city,
            flight.arrival_city,
            key=edge_key,
            flight_event=flight,
        )

    def get_flight_details(self, edge: Tuple[str, str, str]) -> FlightEvent:
        """Get complete flight information for an edge"""
        try:
            return self.graph.edges[edge]["flight_event"]
        except KeyError:
            raise EdgeNotFoundError(edge)

    def find_paths(
        self, origin: str, destination: str, max_flights: int
    ) -> List[List[Tuple[str, str, str]]]:
        """
        Find all possible paths between origin and destination

        Args:
            origin: Departure city
            destination: Arrival city
            max_flights: Maximum number of flights in path

        Returns:
            List of paths, where each path is a list of edges
            Each edge is a tuple of (from_city, to_city, edge_key)
        """
        return list(
            nx.all_simple_edge_paths(  # type: ignore[arg-type]
                self.graph,  # type: ignore[arg-type]
                origin,  # type: ignore[arg-type]
                destination,  # type: ignore[arg-type]
                cutoff=max_flights,
            )
        )
