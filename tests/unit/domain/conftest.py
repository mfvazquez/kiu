import pytest
from datetime import datetime
from typing import List

from app.domain.flight_graph import FlightGraph
from app.services.flight_events import FlightEvent


@pytest.fixture
def flight_graph():
    return FlightGraph()


@pytest.fixture
def sample_flights():
    return [
        # BUE -> LON flights
        FlightEvent(
            flight_number="BA123",
            departure_city="BUE",
            arrival_city="LON",
            departure_datetime=datetime(2024, 9, 12, 8, 0),
            arrival_datetime=datetime(2024, 9, 12, 20, 0),
        ),
        # BUE -> MAD flights
        FlightEvent(
            flight_number="AA100",
            departure_city="BUE",
            arrival_city="MAD",
            departure_datetime=datetime(2024, 9, 12, 8, 0),
            arrival_datetime=datetime(2024, 9, 12, 22, 0),
        ),
        FlightEvent(
            flight_number="AA100",  # Same flight number, different date
            departure_city="BUE",
            arrival_city="MAD",
            departure_datetime=datetime(2024, 9, 13, 8, 0),
            arrival_datetime=datetime(2024, 9, 13, 22, 0),
        ),
        # MAD -> LON flights
        FlightEvent(
            flight_number="AA101",
            departure_city="MAD",
            arrival_city="LON",
            departure_datetime=datetime(2024, 9, 13, 10, 0),
            arrival_datetime=datetime(2024, 9, 13, 12, 0),
        ),
        # MAD -> BER flights (should not appear in BUE->LON paths)
        FlightEvent(
            flight_number="IB200",
            departure_city="MAD",
            arrival_city="BER",
            departure_datetime=datetime(2024, 9, 13, 11, 0),
            arrival_datetime=datetime(2024, 9, 13, 13, 30),
        ),
        # BER -> LON flights (should not appear in BUE->LON paths)
        FlightEvent(
            flight_number="LH300",
            departure_city="BER",
            arrival_city="LON",
            departure_datetime=datetime(2024, 9, 13, 15, 0),
            arrival_datetime=datetime(2024, 9, 13, 16, 30),
        ),
        # NY -> TYO flights
        FlightEvent(
            flight_number="NH100",
            departure_city="NY",
            arrival_city="TYO",
            departure_datetime=datetime(2024, 9, 13, 15, 0),
            arrival_datetime=datetime(2024, 9, 13, 16, 30),
        ),
    ]


@pytest.fixture
def flight_graph_with_flights(
    flight_graph: FlightGraph, sample_flights: List[FlightEvent]
):
    for flight in sample_flights:
        flight_graph.add_flight(flight)
    return flight_graph
