"""
Vehicle agents.
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
        route: Ordered list of edge IDs
        arrival_time: Actual arrival time (set when arrived)
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
    route: List[str] = field(default_factory=list)
    arrival_time: Optional[float] = None
    
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
    
    def journey_time(self) -> Optional[float]:
        """Get journey time in seconds (None if not arrived)."""
        if self.arrival_time is None:
            return None
        return self.arrival_time - self.departure_time
