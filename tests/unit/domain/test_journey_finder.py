import pytest
from datetime import datetime, timedelta

from app.domain.journey.journey_finder import JourneyFinder
from app.domain.flight_graph import FlightGraph
from app.services.flight_events import FlightEvent


@pytest.fixture
def journey_finder(flight_graph_with_flights: FlightGraph):
    return JourneyFinder(
        flight_graph=flight_graph_with_flights,
        max_flight_events=2,
        min_connection_time=timedelta(hours=1),
        max_connection_time=timedelta(hours=4),
    )


def test_valid_connection_time(journey_finder: JourneyFinder):
    """Should validate connection times correctly"""
    arrival = datetime(2024, 9, 12, 10, 0)

    # Too short connection (30 min)
    departure1 = arrival + timedelta(minutes=30)
    assert not journey_finder._is_valid_connection(arrival, departure1)

    # Valid connection (2 hours)
    departure2 = arrival + timedelta(hours=2)
    assert journey_finder._is_valid_connection(arrival, departure2)

    # Too long connection (5 hours)
    departure3 = arrival + timedelta(hours=5)
    assert not journey_finder._is_valid_connection(arrival, departure3)


@pytest.fixture
def complex_graph():
    """Creates a graph with multiple possible paths"""
    graph = FlightGraph()
    flights = [
        # Direct flight
        FlightEvent(
            flight_number="BA200",
            departure_city="BUE",
            arrival_city="LON",
            departure_datetime=datetime(2024, 9, 12, 9, 0),
            arrival_datetime=datetime(2024, 9, 12, 23, 30),
        ),
        # Path 1: BUE -> MAD -> LON
        FlightEvent(
            flight_number="AA100",
            departure_city="BUE",
            arrival_city="MAD",
            departure_datetime=datetime(2024, 9, 12, 8, 0),
            arrival_datetime=datetime(2024, 9, 12, 22, 0),
        ),
        FlightEvent(
            flight_number="IB301",
            departure_city="MAD",
            arrival_city="LON",
            departure_datetime=datetime(2024, 9, 13, 6, 0),
            arrival_datetime=datetime(2024, 9, 13, 8, 0),
        ),
        # Invalid connection (too short)
        FlightEvent(
            flight_number="IB302",
            departure_city="MAD",
            arrival_city="LON",
            departure_datetime=datetime(
                2024, 9, 12, 22, 30
            ),  # Only 30min connection
            arrival_datetime=datetime(2024, 9, 13, 0, 30),
        ),
    ]

    for flight in flights:
        graph.add_flight(flight)
    return graph


def test_find_journeys_direct_and_connection(complex_graph):
    """Should find both direct flights and valid connections"""
    finder = JourneyFinder(
        flight_graph=complex_graph,
        max_flight_events=2,
        min_connection_time=timedelta(hours=1),
        max_connection_time=timedelta(hours=12),
    )

    journeys = finder.find_journeys(
        origin="BUE",
        destination="LON",
        departure_date=datetime(2024, 9, 12).date(),
    )

    assert len(journeys) == 2  # Direct flight and one valid connection
    assert journeys[0].connections == 0  # Direct flight first
    assert journeys[1].connections == 1  # Then connection


def test_invalid_connection_time(complex_graph):
    """Should exclude paths with invalid connection times"""
    finder = JourneyFinder(complex_graph)

    # Get all paths including invalid ones
    paths = list(complex_graph.find_paths("BUE", "LON", 2))

    # Check that path with short connection is invalid
    invalid_path = [p for p in paths if len(p) == 2][-1]  # Last 2-segment path
    assert not finder._is_valid_path(invalid_path)


def test_max_flight_events_limit(complex_graph):
    """Should respect max_flight_events limit"""
    finder = JourneyFinder(
        flight_graph=complex_graph, max_flight_events=0  # Only direct flights
    )

    journeys = finder.find_journeys(
        origin="BUE",
        destination="LON",
        departure_date=datetime(2024, 9, 12).date(),
    )

    assert len(journeys) == 1
    assert journeys[0].connections == 0
