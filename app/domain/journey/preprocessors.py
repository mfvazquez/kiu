from typing import List, Tuple
from datetime import date

from app.domain.flight_graph import FlightGraph
from app.domain.journey.protocols import JourneyValidator


class PathPreprocessor:
    def __init__(
        self, 
        graph: FlightGraph,
        validator: JourneyValidator
    ):
        self.graph = graph
        self.validator = validator

    def preprocess(
        self, 
        paths: List[List[Tuple[str, str, str]]], 
        departure_date: date
    ) -> List[List[Tuple[str, str, str]]]:
        """Filter and transform paths before building journeys"""
        valid_paths = []
        for path in paths:
            if self._is_valid_path(path, departure_date):
                valid_paths.append(path)
        return valid_paths

    def _is_valid_path(self, path: List[Tuple[str, str, str]], departure_date: date) -> bool:
        """Quick validation of paths before building journeys"""
        if not path:
            return False

        # Validate first flight departure date
        current = self.graph.get_flight_details(path[0])
        if not self.validator.is_valid_departure_date(
            current.departure_datetime, departure_date
        ):
            return False

        # Validate connections
        for i in range(len(path) - 1):
            current = self.graph.get_flight_details(path[i])
            next_flight = self.graph.get_flight_details(path[i + 1])
            if not self.validator.is_valid_connection(
                current.arrival_datetime, next_flight.departure_datetime
            ):
                return False

        return True 