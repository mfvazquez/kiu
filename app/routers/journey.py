from typing import List
from fastapi import APIRouter, HTTPException, status, Depends, Query
from datetime import date

from app.domain.journey.journey_finder import JourneyFinder
from app.models.journey import Journey
from app.dependencies import get_journey_finder
from app.domain.flight_graph.exceptions import AirportNotFoundError


router = APIRouter(prefix="/journeys", tags=["journeys"])


@router.get("/search")
async def search_journeys(
    departure_date: date = Query(
        ..., description="Departure date (YYYY-MM-DD)"
    ),
    from_: str = Query(..., alias="from", description="Origin airport code"),
    to: str = Query(..., description="Destination airport code"),
    finder: JourneyFinder = Depends(get_journey_finder),
) -> List[Journey]:
    try:
        return finder.find_journeys(
            origin=from_, destination=to, departure_date=departure_date
        )
    except AirportNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
