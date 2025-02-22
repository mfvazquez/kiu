from typing import List, Protocol
from datetime import datetime
from pydantic import BaseModel


class FlightEvent(BaseModel):
    flight_number: str
    departure_city: str
    arrival_city: str
    departure_datetime: datetime
    arrival_datetime: datetime


class FlightEventsProvider(Protocol):
    """Protocol for flight events providers"""
    
    def get_flight_events(self) -> List[FlightEvent]:
        """
        Get all available flight events
        
        Returns:
            List[FlightEvent]: List of flight events
            
        Raises:
            FlightEventsError: If there's an error fetching events
        """
        ... 