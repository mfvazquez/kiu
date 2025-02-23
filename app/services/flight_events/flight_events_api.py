import os
import httpx
from typing import List, Optional
from pydantic import ValidationError

from .interface import FlightEvent
from .exceptions import FlightEventsAPIError, FlightEventsConfigError


class FlightEventsAPIService:
    """Service to fetch flight events from external API"""

    def __init__(self, api_url: Optional[str] = None):
        self.api_url = api_url or os.getenv("FLIGHT_EVENTS_URL")
        if not self.api_url:
            raise FlightEventsConfigError("API URL not provided")

    async def get_flight_events(self) -> List[FlightEvent]:
        """
        Get flight events from the API

        Raises:
            FlightEventsAPIError: If there's an error with the API
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.api_url, timeout=30.0)
                response.raise_for_status()

                raw_events = response.json()
                return [FlightEvent.model_validate(event) for event in raw_events]

        except httpx.HTTPError as e:
            raise FlightEventsAPIError(
                f"Error fetching flight events: {str(e)}"
            )
        except ValidationError as e:
            raise FlightEventsAPIError(
                f"Error validating flight events: {str(e)}"
            )
