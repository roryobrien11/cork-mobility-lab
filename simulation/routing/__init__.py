"""
Cork Mobility Lab - Vehicle Routing Module

Pathfinding algorithms for vehicle navigation:
- Dijkstra: Shortest path by travel time
- A*: Heuristic-guided shortest path
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from heapq import heappush, heappop
import math


class RoutingError(Exception):
    """Routing algorithm error."""
    pass


@dataclass
class Route:
    """
    Planned route for a vehicle.
    
    Attributes:
        route_id: Unique route identifier
        origin_id: Starting node ID
        destination_id: Target node ID
        node_sequence: Ordered list of node IDs from origin to destination
        edge_sequence: Ordered list of edge IDs to traverse
        total_distance_m: Total route distance in meters
        total_travel_time_s: Estimated travel time in seconds
    """
    route_id: str
    origin_id: str
    destination_id: str
    node_sequence: List[str]
    edge_sequence: List[str]
    total_distance_m: float
    total_travel_time_s: float
    
    def is_complete(self) -> bool:
        """Check if route has been fully traversed."""
        return len(self.node_sequence) <= 1
    
    def next_node(self) -> Optional[str]:
        """Get next node in route (or None if complete)."""
        if len(self.node_sequence) > 1:
            return self.node_sequence[1]
        return None
    
    def distance_remaining_m(self, current_node_idx: int = 0) -> float:
        """Get remaining distance from current position."""
        if current_node_idx >= len(self.node_sequence) - 1:
            return 0.0
        
        # This is simplified - in reality would sum edges from current position
        return self.total_distance_m * (1 - current_node_idx / len(self.node_sequence))


class Router:
    """
    Vehicle routing engine using various pathfinding algorithms.
    
    Supports:
    - Dijkstra's algorithm (shortest time)
    - A* algorithm (heuristic-guided)
    """
    
    def __init__(self, network):
        """
        Initialize router.
        
        Args:
            network: Network domain model with nodes and edges
        """
        self.network = network
        self._route_counter = 0

        # A* costs (g_score) are accumulated in seconds via edge.travel_time_s(),
        # so the heuristic must also estimate remaining cost in seconds, not
        # metres, or the search loses its correctness guarantee entirely. We
        # convert straight-line distance to a lower-bound travel time by
        # dividing by the fastest free-flow speed present in the network:
        # since no edge can be traversed faster than that, this heuristic
        # never overestimates the true remaining cost (admissible).
        speeds = [edge.free_flow_speed_ms for edge in network.edges.values()]
        self._max_speed_ms = max(speeds) if speeds else 33.3  # ~120 km/h fallback
    
    def dijkstra(
        self,
        origin_id: str,
        destination_id: str,
        weight_key: str = "travel_time"
    ) -> Optional[Route]:
        """
        Find shortest path using Dijkstra's algorithm.
        
        Args:
            origin_id: Starting node ID
            destination_id: Target node ID
            weight_key: Edge weight to optimize ("travel_time" or "distance")
            
        Returns:
            Route object or None if no path found
        """
        
        # Validate nodes exist
        if origin_id not in self.network.nodes or destination_id not in self.network.nodes:
            return None
        
        if origin_id == destination_id:
            return None
        
        # Initialize distances and previous nodes
        distances: Dict[str, float] = {node_id: float('inf') for node_id in self.network.nodes}
        distances[origin_id] = 0.0
        
        previous: Dict[str, Optional[str]] = {node_id: None for node_id in self.network.nodes}
        visited = set()
        
        # Priority queue: (distance, node_id)
        pq: List[Tuple[float, str]] = [(0.0, origin_id)]
        
        while pq:
            current_distance, current_node_id = heappop(pq)
            
            if current_node_id in visited:
                continue
            
            visited.add(current_node_id)
            
            # Found destination
            if current_node_id == destination_id:
                return self._reconstruct_route(
                    previous=previous,
                    destination_id=destination_id,
                    origin_id=origin_id
                )
            
            # Explore neighbors
            current_node = self.network.nodes[current_node_id]
            for edge_id in current_node.outgoing_edges:
                edge = self.network.edges[edge_id]
                neighbor_id = edge.target_id
                
                if neighbor_id in visited:
                    continue
                
                # Calculate edge weight
                if weight_key == "travel_time":
                    edge_weight = edge.travel_time_s()
                else:  # distance
                    edge_weight = edge.length_m
                
                new_distance = distances[current_node_id] + edge_weight
                
                if new_distance < distances[neighbor_id]:
                    distances[neighbor_id] = new_distance
                    previous[neighbor_id] = current_node_id
                    heappush(pq, (new_distance, neighbor_id))
        
        # No path found
        return None
    
    def astar(
        self,
        origin_id: str,
        destination_id: str,
        heuristic: str = "haversine"
    ) -> Optional[Route]:
        """
        Find shortest path using A* algorithm.
        
        Args:
            origin_id: Starting node ID
            destination_id: Target node ID
            heuristic: Heuristic function ("haversine" or "manhattan")
            
        Returns:
            Route object or None if no path found
        """
        
        # Validate nodes exist
        if origin_id not in self.network.nodes or destination_id not in self.network.nodes:
            return None
        
        if origin_id == destination_id:
            return None
        
        destination_node = self.network.nodes[destination_id]
        
        # Initialize costs
        g_score: Dict[str, float] = {node_id: float('inf') for node_id in self.network.nodes}
        g_score[origin_id] = 0.0
        
        f_score: Dict[str, float] = {node_id: float('inf') for node_id in self.network.nodes}
        f_score[origin_id] = self._heuristic(
            self.network.nodes[origin_id],
            destination_node,
            heuristic
        )
        
        previous: Dict[str, Optional[str]] = {node_id: None for node_id in self.network.nodes}
        open_set = set([origin_id])
        
        # Priority queue: (f_score, node_id)
        pq: List[Tuple[float, str]] = [(f_score[origin_id], origin_id)]
        
        while pq:
            _, current_node_id = heappop(pq)
            
            if current_node_id not in open_set:
                continue
            
            if current_node_id == destination_id:
                return self._reconstruct_route(
                    previous=previous,
                    destination_id=destination_id,
                    origin_id=origin_id
                )
            
            open_set.remove(current_node_id)
            current_node = self.network.nodes[current_node_id]
            
            # Explore neighbors
            for edge_id in current_node.outgoing_edges:
                edge = self.network.edges[edge_id]
                neighbor_id = edge.target_id
                tentative_g = g_score[current_node_id] + edge.travel_time_s()
                
                if tentative_g < g_score[neighbor_id]:
                    previous[neighbor_id] = current_node_id
                    g_score[neighbor_id] = tentative_g
                    
                    neighbor_node = self.network.nodes[neighbor_id]
                    h_score = self._heuristic(neighbor_node, destination_node, heuristic)
                    f_score[neighbor_id] = g_score[neighbor_id] + h_score
                    
                    if neighbor_id not in open_set:
                        open_set.add(neighbor_id)
                        heappush(pq, (f_score[neighbor_id], neighbor_id))
        
        # No path found
        return None
    
    def _reconstruct_route(
        self,
        previous: Dict[str, Optional[str]],
        destination_id: str,
        origin_id: str
    ) -> Optional[Route]:
        """Reconstruct route from Dijkstra/A* parent pointers."""
        
        node_sequence = []
        current = destination_id
        
        while current is not None:
            node_sequence.insert(0, current)
            current = previous[current]
        
        if node_sequence[0] != origin_id:
            return None  # Path doesn't start at origin
        
        # Calculate route statistics
        edge_sequence = []
        total_distance = 0.0
        total_time = 0.0
        
        for i in range(len(node_sequence) - 1):
            current_node = self.network.nodes[node_sequence[i]]
            next_node_id = node_sequence[i + 1]
            
            # Find edge between current and next
            for edge_id in current_node.outgoing_edges:
                edge = self.network.edges[edge_id]
                if edge.target_id == next_node_id:
                    edge_sequence.append(edge.id)
                    total_distance += edge.length_m
                    total_time += edge.travel_time_s()
                    break
        
        route_id = f"route_{self._route_counter}"
        self._route_counter += 1
        
        return Route(
            route_id=route_id,
            origin_id=origin_id,
            destination_id=destination_id,
            node_sequence=node_sequence,
            edge_sequence=edge_sequence,
            total_distance_m=total_distance,
            total_travel_time_s=total_time
        )
    
    def _heuristic(self, current_node, destination_node, heuristic_type: str) -> float:
        """
        Estimate remaining travel time (seconds) to the destination.

        g_score is accumulated in seconds, so the straight-line distance
        estimate is converted to seconds via the network's fastest free-flow
        speed, keeping the heuristic admissible (never overestimates).
        """

        if heuristic_type == "haversine":
            distance_m = self._haversine_distance(current_node, destination_node)
        elif heuristic_type == "manhattan":
            distance_m = self._manhattan_distance(current_node, destination_node)
        else:
            return 0.0

        return distance_m / self._max_speed_ms
    
    @staticmethod
    def _haversine_distance(node1, node2) -> float:
        """Calculate great-circle distance using Haversine formula (meters)."""
        
        R = 6371000  # Earth radius in meters
        lat1, lon1 = math.radians(node1.lat), math.radians(node1.lon)
        lat2, lon2 = math.radians(node2.lat), math.radians(node2.lon)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    @staticmethod
    def _manhattan_distance(node1, node2) -> float:
        """Calculate Manhattan distance approximation."""
        
        # Rough conversion: 1 degree ≈ 111 km
        lat_dist = abs(node2.lat - node1.lat) * 111000
        lon_dist = abs(node2.lon - node1.lon) * 111000
        
        return lat_dist + lon_dist
