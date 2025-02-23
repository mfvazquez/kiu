class FlightGraphError(Exception):
    """Base exception for flight graph errors"""
    pass


class EdgeNotFoundError(FlightGraphError):
    """Raised when trying to access a non-existent edge in the graph"""
    def __init__(self, edge: tuple):
        self.edge = edge
        super().__init__(f"Edge {edge} does not exist in the graph") 