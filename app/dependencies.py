import os
from datetime import timedelta
from fastapi_cache.decorator import cache

from app.domain.flight_graph import FlightGraph
from app.domain.journey.journey_finder import JourneyFinder
from app.domain.journey.validators import DefaultJourneyValidator
from app.domain.journey.builders import DefaultJourneyPathBuilder
from app.domain.journey.sorters import TimeAndConnectionsSorter
from app.services.flight_events import (
    FlightEventsAPIService,
    FlightEventsConfigError,
)

from fastapi import Depends


def get_flight_events_service() -> FlightEventsAPIService:
    api_url = os.getenv("FLIGHT_EVENTS_URL")
    if not api_url:
        raise FlightEventsConfigError(
            "FLIGHT_EVENTS_URL environment variable is required"
        )
    return FlightEventsAPIService(api_url=api_url)


@cache(expire=int(os.getenv("CACHE_TTL_SECONDS", "600")))
async def get_flight_graph(
    service: FlightEventsAPIService = Depends(get_flight_events_service),
) -> FlightGraph:
    """Get flight graph with 10 minute cache"""
    graph = FlightGraph()
    events = await service.get_flight_events()
    for event in events:
        graph.add_flight(event)
    return graph


def get_journey_validator() -> DefaultJourneyValidator:
    return DefaultJourneyValidator(
        min_connection_time=timedelta(
            hours=float(os.getenv("MIN_WAIT_TIME_HOURS", "1"))
        ),
        max_connection_time=timedelta(
            hours=float(os.getenv("MAX_WAIT_TIME_HOURS", "4"))
        ),
        max_flight_time=timedelta(
            hours=float(os.getenv("MAX_FLIGHT_DURATION_HOURS", "24"))
        ),
    )


def get_journey_finder(
    graph: FlightGraph = Depends(get_flight_graph),
    validator: DefaultJourneyValidator = Depends(get_journey_validator),
) -> JourneyFinder:
    return JourneyFinder(
        flight_graph=graph,
        validator=validator,
        path_builder=DefaultJourneyPathBuilder(),
        sorter=TimeAndConnectionsSorter(),
        max_flight_events=int(os.getenv("MAX_FLIGHT_EVENTS", "2")),
    )
