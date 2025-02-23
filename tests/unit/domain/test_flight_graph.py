import pytest
from datetime import datetime
from typing import List
from app.domain.flight_graph import FlightGraph
from app.services.flight_events import FlightEvent
from app.domain.flight_graph.exceptions import (
    EdgeNotFoundError,
    AirportNotFoundError,
)


def test_add_flight(
    flight_graph: FlightGraph, sample_flights: List[FlightEvent]
):
    """Should add flights to graph correctly"""
    flight = sample_flights[0]
    flight_graph.add_flight(flight)

    assert flight_graph.graph.has_node(flight.departure_city)
    assert flight_graph.graph.has_node(flight.arrival_city)
    assert flight_graph.graph.has_edge(
        flight.departure_city, flight.arrival_city
    )


def test_multiple_flights_same_route(flight_graph_with_flights: FlightGraph):
    """Should handle multiple flights between same cities"""
    edges = list(flight_graph_with_flights.graph.edges())
    assert len(edges) == 7
    assert edges[0] == ("BUE", "LON")
    assert edges[1] == ("BUE", "MAD")
    assert edges[2] == ("BUE", "MAD")
    assert edges[3] == ("MAD", "LON")
    assert edges[4] == ("MAD", "BER")
    assert edges[5] == ("BER", "LON")
    assert edges[6] == ("NY", "TYO")


def test_edge_key_uniqueness(flight_graph_with_flights: FlightGraph):
    """Should create unique keys for flights with correct format"""
    edges = list(flight_graph_with_flights.graph.edges(keys=True, data=True))

    # Check key format: {flight_number}_{departure_datetime_iso}
    for edge in edges:
        key = edge[2]

        flight = edge[3]["flight_event"]  # edge[3] is the data dict
        expected_key = (
            f"{flight.flight_number}_{flight.departure_datetime.isoformat()}"
        )
        assert key == expected_key


def test_get_flight_details(flight_graph_with_flights: FlightGraph):
    """Should get flight details correctly"""
    edges = list(flight_graph_with_flights.graph.edges(keys=True))

    flight = flight_graph_with_flights.get_flight_details(edges[0])
    assert flight.flight_number == "BA123"
    assert flight.departure_city == "BUE"
    assert flight.arrival_city == "LON"
    assert flight.departure_datetime == datetime(2024, 9, 12, 8, 0)
    assert flight.arrival_datetime == datetime(2024, 9, 12, 20, 0)

    flight = flight_graph_with_flights.get_flight_details(edges[1])
    assert flight.flight_number == "AA100"
    assert flight.departure_city == "BUE"
    assert flight.arrival_city == "MAD"
    assert flight.departure_datetime == datetime(2024, 9, 12, 8, 0)
    assert flight.arrival_datetime == datetime(2024, 9, 12, 22, 0)

    flight = flight_graph_with_flights.get_flight_details(edges[2])
    assert flight.flight_number == "AA100"
    assert flight.departure_city == "BUE"
    assert flight.arrival_city == "MAD"
    assert flight.departure_datetime == datetime(2024, 9, 13, 8, 0)
    assert flight.arrival_datetime == datetime(2024, 9, 13, 22, 0)

    flight = flight_graph_with_flights.get_flight_details(edges[3])
    assert flight.flight_number == "AA101"
    assert flight.departure_city == "MAD"
    assert flight.arrival_city == "LON"
    assert flight.departure_datetime == datetime(2024, 9, 13, 10, 0)
    assert flight.arrival_datetime == datetime(2024, 9, 13, 12, 0)

    flight = flight_graph_with_flights.get_flight_details(edges[4])
    assert flight.flight_number == "IB200"
    assert flight.departure_city == "MAD"
    assert flight.arrival_city == "BER"
    assert flight.departure_datetime == datetime(2024, 9, 13, 11, 0)
    assert flight.arrival_datetime == datetime(2024, 9, 13, 13, 30)

    flight = flight_graph_with_flights.get_flight_details(edges[5])
    assert flight.flight_number == "LH300"
    assert flight.departure_city == "BER"
    assert flight.arrival_city == "LON"
    assert flight.departure_datetime == datetime(2024, 9, 13, 15, 0)
    assert flight.arrival_datetime == datetime(2024, 9, 13, 16, 30)


def test_get_flight_details_of_nonexistent_edge(
    flight_graph_with_flights: FlightGraph,
):
    """Should raise an error if edge does not exist"""
    with pytest.raises(EdgeNotFoundError) as exc_info:
        flight_graph_with_flights.get_flight_details(
            ("BUE", "BER", "BA123_2024-09-12T08:00:00")
        )

    assert str(exc_info.value) == (
        "Edge ('BUE', 'BER', 'BA123_2024-09-12T08:00:00')"
        " does not exist in the graph"
    )


def test_find_direct_flights(flight_graph_with_flights: FlightGraph):
    """Should find valid paths between cities"""
    paths = flight_graph_with_flights.find_paths(
        origin="BUE", destination="LON", max_flights=1
    )

    # Should find only the BUE->MAD->LON path
    assert len(paths) == 1
    assert paths[0] == [("BUE", "LON", "BA123_2024-09-12T08:00:00")]


def test_find_paths_with_connections(flight_graph_with_flights: FlightGraph):
    """Should find valid paths between cities with connections"""
    paths = flight_graph_with_flights.find_paths(
        origin="BUE", destination="LON", max_flights=2
    )

    # Should find BUE->LON and BUE->MAD->LON paths
    assert len(paths) == 3
    assert len(paths[0]) == 1  # Two segments (BUE->LON)
    assert len(paths[1]) == 2  # Two segments (BUE->MAD->LON)
    assert len(paths[2]) == 2  # Two segments (BUE->MAD->LON)

    assert paths[0] == [("BUE", "LON", "BA123_2024-09-12T08:00:00")]
    assert paths[1] == [
        ("BUE", "MAD", "AA100_2024-09-12T08:00:00"),
        ("MAD", "LON", "AA101_2024-09-13T10:00:00"),
    ]
    assert paths[2] == [
        ("BUE", "MAD", "AA100_2024-09-13T08:00:00"),
        ("MAD", "LON", "AA101_2024-09-13T10:00:00"),
    ]


def test_find_paths_nonexistent_origin(flight_graph_with_flights: FlightGraph):
    """Should raise AirportNotFoundError when origin doesn't exist"""
    with pytest.raises(AirportNotFoundError) as exc_info:
        flight_graph_with_flights.find_paths(
            origin="XXX",  # Non-existent airport
            destination="LON",
            max_flights=2,
        )
    assert "Origin city 'XXX' not found" in str(exc_info.value)


def test_find_paths_nonexistent_destination(
    flight_graph_with_flights: FlightGraph,
):
    """Should raise AirportNotFoundError when destination doesn't exist"""
    with pytest.raises(AirportNotFoundError) as exc_info:
        flight_graph_with_flights.find_paths(
            origin="BUE",
            destination="XXX",  # Non-existent airport
            max_flights=2,
        )
    assert "Destination city 'XXX' not found" in str(exc_info.value)


def test_find_paths_both_airports_nonexistent(
    flight_graph_with_flights: FlightGraph,
):
    """Should raise AirportNotFoundError when both airports don't exist"""
    with pytest.raises(AirportNotFoundError) as exc_info:
        flight_graph_with_flights.find_paths(
            origin="YYY", destination="XXX", max_flights=2
        )
    assert "Origin city 'YYY' not found" in str(exc_info.value)


def test_find_paths_no_route_between_existing_airports(
    flight_graph_with_flights: FlightGraph,
):
    """Should return empty list when no route exists between valid airports"""
    paths = flight_graph_with_flights.find_paths(
        origin="BUE",
        destination="NY",
        max_flights=2,
    )
    assert len(paths) == 0
