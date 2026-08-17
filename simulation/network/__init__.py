"""
Road network domain models.

Defines the structure of the transport network as a directed graph.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum
import uuid


class RoadType(Enum):
    """Road classification."""
    MOTORWAY = "motorway"
    TRUNK = "trunk"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    RESIDENTIAL = "residential"
    UNCLASSIFIED = "unclassified"


class JunctionType(Enum):
    """Type of junction."""
    PRIORITY = "priority"
    SIGNALS = "signals"
    ROUNDABOUT = "roundabout"
    GIVE_WAY = "give_way"
    STOP = "stop"


@dataclass
class Node:
    """
    Network node representing intersection or junction.
    
    Attributes:
        id: Unique identifier
        lat: Latitude (WGS84)
        lon: Longitude (WGS84)
        junction_type: Type of junction
        incoming_edges: List of incoming edge IDs
        outgoing_edges: List of outgoing edge IDs
    """
    id: str
    lat: float
    lon: float
    junction_type: JunctionType = JunctionType.PRIORITY
    incoming_edges: List[str] = field(default_factory=list)
    outgoing_edges: List[str] = field(default_factory=list)
    
    @classmethod
    def create(cls, lat: float, lon: float, junction_type: JunctionType = JunctionType.PRIORITY) -> "Node":
        """Create a new node with generated ID."""
        return cls(
            id=str(uuid.uuid4()),
            lat=lat,
            lon=lon,
            junction_type=junction_type
        )


@dataclass
class Edge:
    """
    Network edge representing a road segment.
    
    Attributes:
        id: Unique identifier
        source_id: Source node ID
        target_id: Target node ID
        length_m: Length in metres
        speed_limit_kmh: Speed limit in km/h
        lanes: Number of lanes
        road_type: Classification
        capacity_vehicles_per_hour: Maximum flow per hour
        allowed_modes: Set of allowed transport modes
        free_flow_speed_ms: Free flow speed in m/s
        current_vehicle_count: Current number of vehicles (for simulation)
        current_avg_speed_ms: Current average speed (for simulation)
    """
    id: str
    source_id: str
    target_id: str
    length_m: float
    speed_limit_kmh: float
    lanes: int = 1
    road_type: RoadType = RoadType.RESIDENTIAL
    capacity_vehicles_per_hour: float = 1800  # per lane
    allowed_modes: Set[str] = field(default_factory=lambda: {"car"})
    free_flow_speed_ms: float = 13.9  # ~50 km/h
    current_vehicle_count: int = 0
    current_avg_speed_ms: float = 0.0
    
    @classmethod
    def create(cls, source_id: str, target_id: str, length_m: float, speed_limit_kmh: float) -> "Edge":
        """Create a new edge with generated ID."""
        free_flow = speed_limit_kmh / 3.6  # km/h to m/s
        return cls(
            id=str(uuid.uuid4()),
            source_id=source_id,
            target_id=target_id,
            length_m=length_m,
            speed_limit_kmh=speed_limit_kmh,
            free_flow_speed_ms=free_flow
        )
    
    def travel_time_s(self, speed_ms: Optional[float] = None) -> float:
        """
        Calculate travel time in seconds.
        
        Args:
            speed_ms: Speed in m/s. If None, uses free flow speed.
        
        Returns:
            Travel time in seconds
        """
        if speed_ms is None:
            speed_ms = self.free_flow_speed_ms
        if speed_ms <= 0:
            return float('inf')
        return self.length_m / speed_ms
    
    def congestion_level(self) -> float:
        """
        Calculate congestion level (0 to 1).
        
        Returns:
            Congestion ratio
        """
        max_vehicles = (self.capacity_vehicles_per_hour * self.lanes) / 3600  # per second
        if max_vehicles == 0:
            return 0.0
        return min(1.0, self.current_vehicle_count / max_vehicles)


@dataclass
class Network:
    """
    Transport network as a directed graph.
    
    Attributes:
        id: Network identifier
        nodes: Dictionary of node ID -> Node
        edges: Dictionary of edge ID -> Edge
        name: Network name
        description: Network description
    """
    id: str
    nodes: Dict[str, Node] = field(default_factory=dict)
    edges: Dict[str, Edge] = field(default_factory=dict)
    name: str = "Unnamed Network"
    description: str = ""
    
    @classmethod
    def create(cls, name: str = "Network") -> "Network":
        """Create a new empty network."""
        return cls(id=str(uuid.uuid4()), name=name)
    
    def add_node(self, node: Node) -> None:
        """Add node to network."""
        self.nodes[node.id] = node
    
    def add_edge(self, edge: Edge) -> None:
        """Add edge to network."""
        if edge.source_id not in self.nodes:
            raise ValueError(f"Source node {edge.source_id} not in network")
        if edge.target_id not in self.nodes:
            raise ValueError(f"Target node {edge.target_id} not in network")
        
        self.edges[edge.id] = edge
        self.nodes[edge.source_id].outgoing_edges.append(edge.id)
        self.nodes[edge.target_id].incoming_edges.append(edge.id)
    
    def get_outgoing_edges(self, node_id: str) -> List[Edge]:
        """Get all outgoing edges from a node."""
        node = self.nodes.get(node_id)
        if not node:
            return []
        return [self.edges[eid] for eid in node.outgoing_edges if eid in self.edges]
    
    def get_incoming_edges(self, node_id: str) -> List[Edge]:
        """Get all incoming edges to a node."""
        node = self.nodes.get(node_id)
        if not node:
            return []
        return [self.edges[eid] for eid in node.incoming_edges if eid in self.edges]
    
    def num_nodes(self) -> int:
        """Number of nodes."""
        return len(self.nodes)
    
    def num_edges(self) -> int:
        """Number of edges."""
        return len(self.edges)
    
    def total_length_m(self) -> float:
        """Total network length in metres."""
        return sum(edge.length_m for edge in self.edges.values())
