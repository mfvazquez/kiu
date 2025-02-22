import networkx as nx

from app.services.flight_events import FlightEvent


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
            flight_number=flight.flight_number,
            departure_city=flight.departure_city,
            arrival_city=flight.arrival_city,
            departure_time=flight.departure_datetime,
            arrival_time=flight.arrival_datetime
        ) 
        