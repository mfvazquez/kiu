from datetime import datetime, date, timedelta

from app.models.journey import Journey


class DefaultJourneyValidator:
    """Validates journey constraints"""

    def __init__(
        self,
        min_connection_time: timedelta,
        max_connection_time: timedelta,
        max_flight_time: timedelta,
    ):
        self.min_connection_time = min_connection_time
        self.max_connection_time = max_connection_time
        self.max_flight_time = max_flight_time

    def is_valid_connection(
        self, arrival_time: datetime, departure_time: datetime
    ) -> bool:
        """Check if connection time between flights is valid"""
        connection_time = departure_time - arrival_time
        return (
            self.min_connection_time
            <= connection_time
            <= self.max_connection_time
        )

    def is_valid_departure_date(
        self, flight_datetime: datetime, departure_date: date
    ) -> bool:
        """Check if flight departs on or after the departure date"""
        return flight_datetime.date() == departure_date

    def is_valid_total_time(self, journey: Journey) -> bool:
        """Check if total journey time is within limits"""
        paths = journey.path
        if not paths:
            return False

        total_time = paths[-1].arrival_time - paths[0].departure_time
        return total_time <= self.max_flight_time
