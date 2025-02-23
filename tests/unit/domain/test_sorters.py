import pytest
from datetime import datetime

from app.models.journey import Journey, PathFlight
from app.domain.journey.sorters import TimeAndConnectionsSorter


@pytest.fixture
def sorter():
    return TimeAndConnectionsSorter()


@pytest.fixture
def sample_path_flight():
    return PathFlight(
        flight_number="TEST",
        from_="A",
        to="B",
        departure_time=datetime(2024, 1, 1, 10, 0),
        arrival_time=datetime(2024, 1, 1, 12, 0),
    )


def test_empty_journeys(sorter):
    """Should handle empty journey list"""
    assert sorter.sort([]) == []


def test_sort_by_total_time(
    sorter: TimeAndConnectionsSorter, sample_path_flight: PathFlight
):
    """Should sort primarily by total journey time"""
    # Create two journeys with same connections but different duration
    path1 = [
        sample_path_flight,
        PathFlight(
            flight_number="TEST2",
            from_="B",
            to="C",
            departure_time=datetime(2024, 1, 1, 13, 0),
            arrival_time=datetime(2024, 1, 1, 14, 0),  # 4h total
        ),
    ]
    path2 = [
        sample_path_flight,
        PathFlight(
            flight_number="TEST3",
            from_="B",
            to="C",
            departure_time=datetime(2024, 1, 1, 13, 0),
            arrival_time=datetime(2024, 1, 1, 15, 0),  # 5h total
        ),
    ]

    journey1 = Journey(connections=1, path=path1)
    journey2 = Journey(connections=1, path=path2)

    sorted_journeys = sorter.sort([journey2, journey1])
    assert sorted_journeys == [journey1, journey2]


def test_sort_by_connections_when_same_time(
    sorter: TimeAndConnectionsSorter, sample_path_flight: PathFlight
):
    """Should use connections as secondary sort criteria"""
    # Create two journeys with same total time but different connections
    path1 = [sample_path_flight]  # 2h, 0 connections
    path2 = [
        PathFlight(
            flight_number="TEST2",
            from_="A",
            to="B",
            departure_time=datetime(2024, 1, 1, 10, 0),
            arrival_time=datetime(2024, 1, 1, 11, 0),
        ),
        PathFlight(
            flight_number="TEST3",
            from_="B",
            to="C",
            departure_time=datetime(2024, 1, 1, 11, 0),
            arrival_time=datetime(2024, 1, 1, 12, 0),
        ),
    ]  # 2h total, 1 connection

    journey1 = Journey(connections=0, path=path1)
    journey2 = Journey(connections=1, path=path2)

    sorted_journeys = sorter.sort([journey2, journey1])
    assert sorted_journeys == [journey1, journey2]
