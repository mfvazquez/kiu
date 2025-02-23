import pytest
from datetime import datetime, date, timedelta

from app.domain.journey.preprocessors import PathPreprocessor
from app.domain.journey.validators import DefaultJourneyValidator
from app.domain.flight_graph import FlightGraph
from app.services.flight_events import FlightEvent


@pytest.fixture
def validator():
    return DefaultJourneyValidator(
        min_connection_time=timedelta(hours=1),
        max_connection_time=timedelta(hours=4),
        max_flight_time=timedelta(hours=24),
    )


@pytest.fixture
def graph():
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
        # Valid connection path
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
            departure_datetime=datetime(
                2024, 9, 12, 23, 30
            ),  # 1.5h connection
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
        # Invalid departure date
        FlightEvent(
            flight_number="IB303",
            departure_city="BUE",
            arrival_city="MAD",
            departure_datetime=datetime(2024, 9, 11, 8, 0),  # Day before
            arrival_datetime=datetime(2024, 9, 11, 22, 0),
        ),
    ]
    for flight in flights:
        graph.add_flight(flight)
    return graph


@pytest.fixture
def preprocessor(graph, validator):
    return PathPreprocessor(graph, validator)


def test_empty_paths(preprocessor):
    """Should handle empty path list"""
    paths: list = []
    departure_date = date(2024, 9, 12)

    assert preprocessor.preprocess(paths, departure_date) == []


def test_invalid_empty_path(preprocessor):
    """Should filter out empty paths"""
    paths = [[]]  # List with one empty path
    departure_date = date(2024, 9, 12)

    assert preprocessor.preprocess(paths, departure_date) == []


def test_valid_direct_flight(preprocessor, graph):
    """Should accept valid direct flights"""
    paths = [[("BUE", "LON", "BA200_2024-09-12T09:00:00")]]
    departure_date = date(2024, 9, 12)

    valid_paths = preprocessor.preprocess(paths, departure_date)
    assert len(valid_paths) == 1
    assert valid_paths[0] == paths[0]


def test_valid_connection(preprocessor, graph):
    """Should accept valid connections"""
    paths = [
        [
            ("BUE", "MAD", "AA100_2024-09-12T08:00:00"),
            ("MAD", "LON", "IB301_2024-09-12T23:30:00"),
        ]
    ]
    departure_date = date(2024, 9, 12)

    valid_paths = preprocessor.preprocess(paths, departure_date)
    assert len(valid_paths) == 1
    assert valid_paths[0] == paths[0]


def test_invalid_connection_time(preprocessor, graph):
    """Should filter out paths with invalid connection times"""
    paths = [
        [
            ("BUE", "MAD", "AA100_2024-09-12T08:00:00"),
            (
                "MAD",
                "LON",
                "IB302_2024-09-12T22:30:00",
            ),  # Too short connection
        ]
    ]
    departure_date = date(2024, 9, 12)

    assert preprocessor.preprocess(paths, departure_date) == []


def test_invalid_departure_date(preprocessor, graph):
    """Should filter out paths starting before departure date"""
    paths = [[("BUE", "MAD", "IB303_2024-09-11T08:00:00")]]  # Day before
    departure_date = date(2024, 9, 12)

    assert preprocessor.preprocess(paths, departure_date) == []


def test_mixed_valid_invalid_paths(preprocessor, graph):
    """Should filter invalid paths while keeping valid ones"""
    paths = [
        # Valid direct flight
        [("BUE", "LON", "BA200_2024-09-12T09:00:00")],
        # Invalid connection
        [
            ("BUE", "MAD", "AA100_2024-09-12T08:00:00"),
            ("MAD", "LON", "IB302_2024-09-12T22:30:00"),
        ],
        # Valid connection
        [
            ("BUE", "MAD", "AA100_2024-09-12T08:00:00"),
            ("MAD", "LON", "IB301_2024-09-12T23:30:00"),
        ],
    ]
    departure_date = date(2024, 9, 12)

    valid_paths = preprocessor.preprocess(paths, departure_date)
    assert len(valid_paths) == 2
    assert valid_paths[0] == paths[0]  # Direct flight
    assert valid_paths[1] == paths[2]  # Valid connection
