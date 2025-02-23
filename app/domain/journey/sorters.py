from typing import List
from datetime import timedelta

from app.models.journey import Journey


class TimeAndConnectionsSorter:
    def sort(self, journeys: List[Journey]) -> List[Journey]:
        def get_total_time(journey: Journey) -> timedelta:
            return (
                journey.path[-1].arrival_time - journey.path[0].departure_time
            )

        return sorted(
            journeys, key=lambda j: (get_total_time(j), j.connections)
        )
