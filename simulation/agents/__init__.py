"""
Vehicle agents with routing support.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
import uuid


class VehicleState(Enum):
    """Vehicle operational state."""
    WAITING = "waiting"
    DRIVING = "driving"
    QUEUED = "queued"
    STOPPED = "stopped"
    ARRIVED = "arrived"


@dataclass
class Vehicle:
    """
    Vehicle agent in the simulation.
    
    Attributes:
        id: Unique vehicle identifier
        origin_node_id: Origin node ID
        destination_node_id: Destination node ID
        vehicle_type: Type of vehicle (car, bus, etc.)
        departure_time: Departure time in seconds
        current_edge_id: Current edge ID (if driving)
        position_on_edge: Position along edge (0 to 1)
        speed_ms: Current speed in m/s
        state: Current vehicle state
        route: Ordered list of edge IDs (from routing engine)
        node_sequence: Ordered list of node IDs in planned route
        planned_route: Route object from routing engine
        arrival_time: Actual arrival time (set when arrived)
        current_node_idx: Current position in node sequence
    """
    id: str
    origin_node_id: str
    destination_node_id: str
    vehicle_type: str = "car"
    departure_time: float = 0.0
    current_edge_id: Optional[str] = None
    position_on_edge: float = 0.0
    speed_ms: float = 0.0
    state: VehicleState = VehicleState.WAITING
    route: List[str] = field(default_factory=list)  # Edge sequence
    node_sequence: List[str] = field(default_factory=list)  # Node sequence
    planned_route: Optional[object] = None  # Route object from Router
    arrival_time: Optional[float] = None
    current_node_idx: int = 0
    
    @classmethod
    def create(
        cls,
        origin_node_id: str,
        destination_node_id: str,
        departure_time: float = 0.0,
        vehicle_type: str = "car"
    ) -> "Vehicle":
        """Create a new vehicle."""
        return cls(
            id=str(uuid.uuid4()),
            origin_node_id=origin_node_id,
            destination_node_id=destination_node_id,
            vehicle_type=vehicle_type,
            departure_time=departure_time
        )
    
    def set_route(self, route) -> None:
        """
        Set planned route for vehicle.
        
        Args:
            route: Route object from Router.dijkstra() or Router.astar()
        """
        if route is None:
            self.state = VehicleState.STOPPED  # No route found
            return
        
        self.planned_route = route
        self.route = route.edge_sequence
        self.node_sequence = route.node_sequence
        self.current_node_idx = 0
    
    def has_route(self) -> bool:
        """Check if vehicle has a planned route."""
        return len(self.route) > 0
    
    def get_next_node(self) -> Optional[str]:
        """Get ID of next node in route."""
        if self.current_node_idx + 1 < len(self.node_sequence):
            return self.node_sequence[self.current_node_idx + 1]
        return None
    
    def get_next_edge(self) -> Optional[str]:
        """Get ID of next edge to traverse."""
        if self.current_node_idx < len(self.route):
            return self.route[self.current_node_idx]
        return None
    
    def advance_node(self) -> bool:
        """
        Move to next node in route.
        
        Returns:
            True if advanced, False if route complete
        """
        if self.current_node_idx + 1 < len(self.node_sequence):
            self.current_node_idx += 1
            return True
        return False
    
    def route_progress_percent(self) -> float:
        """Get route completion percentage (0-100)."""
        if not self.node_sequence or len(self.node_sequence) < 2:
            return 0.0
        return (self.current_node_idx / (len(self.node_sequence) - 1)) * 100
    
    def distance_remaining_m(self) -> float:
        """Get remaining distance in meters."""
        if self.planned_route is None:
            return 0.0
        return self.planned_route.distance_remaining_m(self.current_node_idx)
    
    def journey_time(self) -> Optional[float]:
        """Get journey time in seconds (None if not arrived)."""
        if self.arrival_time is None:
            return None
        return self.arrival_time - self.departure_time
