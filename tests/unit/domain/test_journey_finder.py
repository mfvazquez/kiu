import pytest
from datetime import datetime, timedelta

from app.domain.journey.journey_finder import JourneyFinder
from app.domain.flight_graph import FlightGraph
from app.services.flight_events import FlightEvent
from app.domain.journey.validators import DefaultJourneyValidator
from app.domain.journey.builders import DefaultJourneyPathBuilder
from app.domain.journey.sorters import TimeAndConnectionsSorter


@pytest.fixture
def journey_finder(flight_graph_with_flights: FlightGraph):
    validator = DefaultJourneyValidator(
        min_connection_time=timedelta(hours=1),
        max_connection_time=timedelta(hours=4),
        max_flight_time=timedelta(hours=24),
    )
    path_builder = DefaultJourneyPathBuilder()
    sorter = TimeAndConnectionsSorter()

    return JourneyFinder(
        flight_graph=flight_graph_with_flights,
        validator=validator,
        path_builder=path_builder,
        sorter=sorter,
        max_flight_events=2,
    )


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
            departure_datetime=datetime(2024, 9, 12, 23, 0),
            arrival_datetime=datetime(2024, 9, 13, 2, 0),
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
        # Invalid connection (departure before arrival)
        FlightEvent(
            flight_number="IB303",
            departure_city="MAD",
            arrival_city="LON",
            departure_datetime=datetime(
                2024, 9, 12, 22, 30
            ),  # Only 30min connection
            arrival_datetime=datetime(2024, 9, 12, 4, 0),
        ),
        # Invalid flight ( total time too long )
        FlightEvent(
            flight_number="BA201",
            departure_city="BUE",
            arrival_city="LON",
            departure_datetime=datetime(2024, 9, 12, 9, 0),
            arrival_datetime=datetime(2024, 9, 13, 9, 1),
        ),
    ]

    for flight in flights:
        graph.add_flight(flight)
    return graph


@pytest.fixture
def complex_journey_finder(complex_graph: FlightGraph):
    validator = DefaultJourneyValidator(
        min_connection_time=timedelta(hours=1),
        max_connection_time=timedelta(hours=4),
        max_flight_time=timedelta(hours=24),
    )
    path_builder = DefaultJourneyPathBuilder()
    sorter = TimeAndConnectionsSorter()

    return JourneyFinder(
        flight_graph=complex_graph,
        validator=validator,
        path_builder=path_builder,
        sorter=sorter,
        max_flight_events=2,
    )


def test_find_journeys_direct_and_connection(
    complex_journey_finder: JourneyFinder,
):
    """Should find both direct flights and valid connections"""

    journeys = complex_journey_finder.find_journeys(
        origin="BUE",
        destination="LON",
        departure_date=datetime(2024, 9, 12).date(),
    )

    assert len(journeys) == 2  # Direct flight and one valid connection
    assert journeys[0].connections == 0  # Direct flight first
    assert journeys[1].connections == 1  # Then connection


def test_max_flight_events_limit(complex_journey_finder: JourneyFinder):
    """Should respect max_flight_events limit"""
    complex_journey_finder.max_flight_events = 1

    journeys = complex_journey_finder.find_journeys(
        origin="BUE",
        destination="LON",
        departure_date=datetime(2024, 9, 12).date(),
    )

    assert len(journeys) == 1
    assert journeys[0].connections == 0


def test_flight_search_before_departure_date_returns_empty_list(
    complex_journey_finder: JourneyFinder,
):
    """Should return empty list if departure date is in the past"""
    complex_journey_finder.max_flight_events = 1

    journeys = complex_journey_finder.find_journeys(
        origin="BUE",
        destination="LON",
        departure_date=datetime(1990, 5, 8).date(),
    )

    assert len(journeys) == 0
