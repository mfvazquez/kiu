from typing import Dict, Type, List, Optional
from .interface import FlightEventsProvider, FlightEvent
from .flight_events_api import FlightEventsAPIService
from .exceptions import FlightEventsConfigError


class APIFlightEventsProvider:
    """Implementation that uses the external API"""

    def __init__(self, api_url: Optional[str] = None):
        self.service = FlightEventsAPIService(api_url)

    async def get_flight_events(self) -> List[FlightEvent]:
        return await self.service.get_flight_events()


PROVIDERS: Dict[str, Type[FlightEventsProvider]] = {
    "api": APIFlightEventsProvider,
}


def get_default_provider(
    provider_type: str = "api", **kwargs
) -> FlightEventsProvider:
    """
    Factory function to get the configured provider

    Args:
        provider_type: Type of provider to create ("api" or "mock")
        **kwargs: Additional configuration for the provider

    Returns:
        FlightEventsProvider: Configured provider instance

    Raises:
        FlightEventsConfigError: If provider_type is unknown
    """
    provider_class = PROVIDERS.get(provider_type)
    if not provider_class:
        raise FlightEventsConfigError(
            f"Unknown provider type: {provider_type}"
        )
    return provider_class(**kwargs)
