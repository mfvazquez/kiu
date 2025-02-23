from datetime import date
from typing import List

from app.models.journey import Journey
from .protocols import (
    JourneyPathBuilder,
    JourneySorter,
    JourneyValidator,
)
from ..flight_graph import FlightGraph
from .preprocessors import PathPreprocessor


class JourneyFinder:
    """
    Finds possible journeys between cities using a flight graph.
    Uses the flight graph to search for valid paths considering
    connections and time constraints.
    """

    def __init__(
        self,
        flight_graph: FlightGraph,
        validator: JourneyValidator,
        path_builder: JourneyPathBuilder,
        sorter: JourneySorter,
        max_flight_events: int = 2,
    ):
        """
        Initialize with a flight graph to search on

        Args:
            flight_graph: Graph containing all flights
            validator: Validator for journey constraints
            path_builder: Builder for journey paths
            sorter: Sorter for journeys
            max_flight_events: Maximum number of flight events allowed
        """
        self.flight_graph = flight_graph
        self.validator = validator
        self.path_builder = path_builder
        self.sorter = sorter
        self.max_flight_events = max_flight_events
        self.preprocessor = PathPreprocessor(flight_graph, validator)

    def find_journeys(
        self, origin: str, destination: str, departure_date: date
    ) -> List[Journey]:
        """
        Find all possible journeys between origin and destination
        for a given departure date.
        Returns journeys ordered by number of connections (ascending).
        """
        all_paths = self.flight_graph.find_paths(
            origin, destination, self.max_flight_events
        )
        paths = self.preprocessor.preprocess(all_paths, departure_date)

        journeys = []
        for path in paths:
            flight_path = self.path_builder.build_path(path, self.flight_graph)
            journey = Journey(connections=len(path) - 1, path=flight_path)
            if not self.validator.is_valid_total_time(journey):
                continue

            journeys.append(journey)

        return self.sorter.sort(journeys)
