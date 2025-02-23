import httpx
from typing import List
from pydantic import ValidationError

from .types import FlightEvent
from .exceptions import FlightEventsAPIError


class FlightEventsAPIService:
    """Service to fetch flight events from external API"""

    def __init__(self, api_url: str, timeout: float = 30.0):
        self.api_url = api_url
        self.timeout = timeout

    async def get_flight_events(self) -> List[FlightEvent]:
        """
        Get flight events from the API

        Raises:
            FlightEventsAPIError: If there's an error with the API
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.api_url, timeout=self.timeout)
                response.raise_for_status()

                raw_events = response.json()
                return [
                    FlightEvent.model_validate(event) for event in raw_events
                ]

        except httpx.HTTPError as e:
            raise FlightEventsAPIError(
                f"Error fetching flight events: {str(e)}"
            )
        except ValidationError as e:
            raise FlightEventsAPIError(
                f"Error validating flight events: {str(e)}"
            )
