import pytest
from datetime import datetime, date, timedelta

from app.domain.journey.validators import DefaultJourneyValidator
from app.models.journey import Journey, PathFlight


@pytest.fixture
def validator():
    return DefaultJourneyValidator(
        min_connection_time=timedelta(hours=1),
        max_connection_time=timedelta(hours=4),
        max_flight_time=timedelta(hours=24),
    )


def test_valid_connection_time(validator):
    """Should validate connection times correctly"""
    arrival = datetime(2024, 9, 12, 10, 0)

    # Too short connection (30 min)
    departure1 = arrival + timedelta(minutes=30)
    assert not validator.is_valid_connection(arrival, departure1)

    # Valid connection (2 hours)
    departure2 = arrival + timedelta(hours=2)
    assert validator.is_valid_connection(arrival, departure2)

    # Too long connection (5 hours)
    departure3 = arrival + timedelta(hours=5)
    assert not validator.is_valid_connection(arrival, departure3)


def test_valid_departure_date(validator):
    """Should validate departure dates correctly"""
    departure_date = date(2024, 9, 12)

    # Same day
    flight_time1 = datetime(2024, 9, 12, 10, 0)
    assert validator.is_valid_departure_date(flight_time1, departure_date)

    # Future day
    flight_time2 = datetime(2024, 9, 13, 10, 0)
    assert validator.is_valid_departure_date(flight_time2, departure_date)

    # Past day
    flight_time3 = datetime(2024, 9, 11, 10, 0)
    assert not validator.is_valid_departure_date(flight_time3, departure_date)


def test_valid_total_time(validator):
    """Should validate total journey time correctly"""
    # Valid journey (20 hours)
    path1 = [
        PathFlight(
            flight_number="TEST1",
            from_="A",
            to="B",
            departure_time=datetime(2024, 9, 12, 10, 0),
            arrival_time=datetime(2024, 9, 12, 15, 0),
        ),
        PathFlight(
            flight_number="TEST2",
            from_="B",
            to="C",
            departure_time=datetime(2024, 9, 12, 16, 0),
            arrival_time=datetime(2024, 9, 13, 6, 0),
        ),
    ]
    journey1 = Journey(connections=1, path=path1)
    assert validator.is_valid_total_time(journey1)

    # Invalid journey (30 hours)
    path2 = [
        PathFlight(
            flight_number="TEST3",
            from_="A",
            to="B",
            departure_time=datetime(2024, 9, 12, 10, 0),
            arrival_time=datetime(2024, 9, 12, 20, 0),
        ),
        PathFlight(
            flight_number="TEST4",
            from_="B",
            to="C",
            departure_time=datetime(2024, 9, 13, 0, 0),
            arrival_time=datetime(2024, 9, 13, 16, 0),
        ),
    ]
    journey2 = Journey(connections=1, path=path2)
    assert not validator.is_valid_total_time(journey2)


def test_empty_journey_time(validator):
    """Should handle empty journey paths"""
    journey = Journey(connections=0, path=[])
    assert not validator.is_valid_total_time(journey)


def test_single_flight_journey(validator):
    """Should validate single flight journeys"""
    path = [
        PathFlight(
            flight_number="TEST1",
            from_="A",
            to="B",
            departure_time=datetime(2024, 9, 12, 10, 0),
            arrival_time=datetime(2024, 9, 12, 15, 0),
        )
    ]
    journey = Journey(connections=0, path=path)
    assert validator.is_valid_total_time(journey)


def test_invalid_connection_negative_time(validator):
    """Should invalidate connections where departure is before arrival"""
    arrival = datetime(2024, 9, 12, 10, 0)

    # Departure before arrival (negative connection time)
    departure = arrival - timedelta(hours=1)
    assert not validator.is_valid_connection(arrival, departure)

    # Edge case: departure equals arrival
    assert not validator.is_valid_connection(arrival, arrival)
