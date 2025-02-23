class FlightEventsError(Exception):
    """Base exception for flight events errors"""

    pass


class FlightEventsAPIError(FlightEventsError):
    """Raised when there's an error communicating with the API"""

    pass


class FlightEventsConfigError(FlightEventsError):
    """Raised when there's a configuration error"""

    pass
