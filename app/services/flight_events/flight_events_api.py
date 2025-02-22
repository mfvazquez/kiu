import os
import requests
from typing import List, Optional

from .interface import FlightEvent
from .exceptions import FlightEventsAPIError, FlightEventsConfigError


class FlightEventsAPIService:
    """Service to fetch flight events from external API"""

    def __init__(self, api_url: Optional[str] = None):
        self.api_url = api_url or os.getenv("FLIGHT_EVENTS_URL")
        if not self.api_url:
            raise FlightEventsConfigError("API URL not provided")

    def get_flight_events(self) -> List[FlightEvent]:
        """
        Get flight events from the API

        Raises:
            FlightEventsAPIError: If there's an error with the API
        """
        try:
            response = requests.get(self.api_url, timeout=30)
            response.raise_for_status()

            raw_events = response.json()
            return [FlightEvent.model_validate(event) for event in raw_events]

        except requests.RequestException as e:
            raise FlightEventsAPIError(
                f"Error fetching flight events: {str(e)}"
            )
