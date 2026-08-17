"""
Unit tests for routing module.
"""

import pytest
import math

from simulation.routing import Route, Router, RoutingError
from simulation.network import Network, Node, Edge, RoadType, JunctionType


@pytest.fixture
def simple_network():
    """Create simple linear test network: 1 -> 2 -> 3 -> 4."""
    network = Network.create("Test Network")
    
    # Create 4 nodes in a line
    nodes = [
        Node.create(lat=51.0 + i * 0.001, lon=-8.0 + i * 0.001, junction_type=JunctionType.PRIORITY)
        for i in range(4)
    ]
    
    for node in nodes:
        network.add_node(node)
    
    # Create edges: 1->2->3->4
    for i in range(3):
        edge = Edge.create(
            source_id=nodes[i].id,
            target_id=nodes[i + 1].id,
            length_m=500,
            speed_limit_kmh=50
        )
        network.add_edge(edge)
    
    return network, nodes


@pytest.fixture
def grid_network():
    """Create 3x3 grid network for testing multiple paths."""
    network = Network.create("Grid Network")
    
    nodes = {}
    # Create 3x3 grid
    for i in range(3):
        for j in range(3):
            node_id = f"node_{i}_{j}"
            node = Node.create(
                lat=51.0 + i * 0.001,
                lon=-8.0 + j * 0.001,
                junction_type=JunctionType.PRIORITY
            )
            nodes[node_id] = node
            network.add_node(node)
    
    # Connect nodes: right and down
    for i in range(3):
        for j in range(3):
            current_node = nodes[f"node_{i}_{j}"]
            
            # Connect right
            if j < 2:
                target_node = nodes[f"node_{i}_{j + 1}"]
                edge = Edge.create(
                    source_id=current_node.id,
                    target_id=target_node.id,
                    length_m=500,
                    speed_limit_kmh=50
                )
                network.add_edge(edge)
            
            # Connect down
            if i < 2:
                target_node = nodes[f"node_{i + 1}_{j}"]
                edge = Edge.create(
                    source_id=current_node.id,
                    target_id=target_node.id,
                    length_m=500,
                    speed_limit_kmh=50
                )
                network.add_edge(edge)
    
    return network, nodes


class TestRoute:
    """Test Route dataclass."""
    
    def test_create_route(self):
        """Test creating a route."""
        route = Route(
            route_id="r1",
            origin_id="n1",
            destination_id="n3",
            node_sequence=["n1", "n2", "n3"],
            edge_sequence=["e1", "e2"],
            total_distance_m=1000,
            total_travel_time_s=60
        )
        
        assert route.route_id == "r1"
        assert route.origin_id == "n1"
        assert route.destination_id == "n3"
    
    def test_route_next_node(self):
        """Test getting next node in route."""
        route = Route(
            route_id="r1",
            origin_id="n1",
            destination_id="n3",
            node_sequence=["n1", "n2", "n3"],
            edge_sequence=["e1", "e2"],
            total_distance_m=1000,
            total_travel_time_s=60
        )
        
        assert route.next_node() == "n2"
    
    def test_route_is_complete(self):
        """Test checking if route is complete."""
        complete_route = Route(
            route_id="r1",
            origin_id="n1",
            destination_id="n1",
            node_sequence=["n1"],
            edge_sequence=[],
            total_distance_m=0,
            total_travel_time_s=0
        )
        
        assert complete_route.is_complete()
    
    def test_route_distance_remaining(self):
        """Test calculating remaining distance."""
        route = Route(
            route_id="r1",
            origin_id="n1",
            destination_id="n4",
            node_sequence=["n1", "n2", "n3", "n4"],
            edge_sequence=["e1", "e2", "e3"],
            total_distance_m=1500,
            total_travel_time_s=90
        )
        
        # At start
        remaining = route.distance_remaining_m(current_node_idx=0)
        assert remaining > 0
        
        # At end
        remaining = route.distance_remaining_m(current_node_idx=3)
        assert remaining == 0


class TestRouter:
    """Test Router class."""
    
    def test_router_initialization(self, simple_network):
        """Test router initialization."""
        network, _ = simple_network
        router = Router(network)
        
        assert router.network == network
        assert router._route_counter == 0
    
    def test_dijkstra_simple_path(self, simple_network):
        """Test Dijkstra on simple linear network."""
        network, nodes = simple_network
        router = Router(network)
        
        route = router.dijkstra(nodes[0].id, nodes[3].id)
        
        assert route is not None
        assert route.origin_id == nodes[0].id
        assert route.destination_id == nodes[3].id
        assert len(route.node_sequence) == 4
        assert route.total_distance_m > 0
        assert route.total_travel_time_s > 0
    
    def test_dijkstra_no_path(self, simple_network):
        """Test Dijkstra when no path exists."""
        network, nodes = simple_network
        router = Router(network)
        
        # Reverse direction (no edges going back)
        route = router.dijkstra(nodes[3].id, nodes[0].id)
        
        assert route is None
    
    def test_dijkstra_same_origin_destination(self, simple_network):
        """Test Dijkstra with same origin and destination."""
        network, nodes = simple_network
        router = Router(network)
        
        route = router.dijkstra(nodes[0].id, nodes[0].id)
        
        assert route is None
    
    def test_dijkstra_invalid_node(self, simple_network):
        """Test Dijkstra with invalid nodes."""
        network, nodes = simple_network
        router = Router(network)
        
        route = router.dijkstra("invalid_node", nodes[1].id)
        
        assert route is None
    
    def test_dijkstra_grid_shortest_path(self, grid_network):
        """Test Dijkstra finds shortest path in grid."""
        network, nodes = grid_network
        router = Router(network)
        
        # Get nodes
        start = nodes["node_0_0"]
        end = nodes["node_2_2"]
        
        route = router.dijkstra(start.id, end.id)
        
        assert route is not None
        # Shortest path in grid should have 5 nodes (0,0 -> 0,1 -> 0,2 -> 1,2 -> 2,2)
        # or similar path with 5 nodes
        assert len(route.node_sequence) == 5
    
    def test_astar_simple_path(self, simple_network):
        """Test A* on simple linear network."""
        network, nodes = simple_network
        router = Router(network)
        
        route = router.astar(nodes[0].id, nodes[3].id, heuristic="haversine")
        
        assert route is not None
        assert route.origin_id == nodes[0].id
        assert route.destination_id == nodes[3].id
    
    def test_astar_with_manhattan_heuristic(self, grid_network):
        """Test A* with Manhattan heuristic."""
        network, nodes = grid_network
        router = Router(network)
        
        start = nodes["node_0_0"]
        end = nodes["node_2_2"]
        
        route = router.astar(start.id, end.id, heuristic="manhattan")
        
        assert route is not None
        assert len(route.node_sequence) > 1
    
    def test_dijkstra_vs_astar_same_path(self, grid_network):
        """Test that Dijkstra and A* find same optimal path."""
        network, nodes = grid_network
        router = Router(network)
        
        start = nodes["node_0_0"]
        end = nodes["node_2_2"]
        
        dijkstra_route = router.dijkstra(start.id, end.id)
        astar_route = router.astar(start.id, end.id)
        
        assert dijkstra_route is not None
        assert astar_route is not None
        # Both should find paths of same length
        assert len(dijkstra_route.node_sequence) == len(astar_route.node_sequence)
        assert abs(dijkstra_route.total_distance_m - astar_route.total_distance_m) < 0.01
    
    def test_astar_matches_dijkstra_with_heterogeneous_speeds(self):
        """
        A* must return the same optimal travel time as Dijkstra even when
        edges have very different speeds and nodes are spread far apart.

        Regression test: the A* heuristic used to return straight-line
        distance in metres while g_score accumulates travel time in
        seconds. Over short, uniform-speed test networks the resulting
        magnitude mismatch was too small to break tie-breaking, but with
        widely spaced nodes (as in the real Cork network) the inadmissible
        heuristic caused A* to close the destination early and return a
        slower route than Dijkstra's optimum.
        """
        network = Network.create("Heterogeneous Speed Network")

        a = Node.create(lat=51.80, lon=-8.60, junction_type=JunctionType.PRIORITY)
        b = Node.create(lat=51.90, lon=-8.50, junction_type=JunctionType.PRIORITY)
        # X sits close to A but geographically far from B (large heuristic to B).
        x = Node.create(lat=51.80, lon=-8.61, junction_type=JunctionType.PRIORITY)
        # Y sits geographically close to B (small heuristic to B), tempting a
        # distance-driven search to prefer it even though it's the slow route.
        y = Node.create(lat=51.895, lon=-8.505, junction_type=JunctionType.PRIORITY)

        for node in (a, b, x, y):
            network.add_node(node)

        # Path via X: fast (motorway-speed) end to end -> lowest travel time.
        network.add_edge(Edge.create(source_id=a.id, target_id=x.id, length_m=500, speed_limit_kmh=120))
        network.add_edge(Edge.create(source_id=x.id, target_id=b.id, length_m=20000, speed_limit_kmh=120))

        # Path via Y: geographically tempting (Y is near B) but slow throughout.
        network.add_edge(Edge.create(source_id=a.id, target_id=y.id, length_m=20000, speed_limit_kmh=20))
        network.add_edge(Edge.create(source_id=y.id, target_id=b.id, length_m=500, speed_limit_kmh=20))

        router = Router(network)

        dijkstra_route = router.dijkstra(a.id, b.id, weight_key="travel_time")
        astar_route = router.astar(a.id, b.id, heuristic="haversine")

        assert dijkstra_route is not None
        assert astar_route is not None
        # The fast route via X should win on travel time, not the
        # geographically-tempting-but-slow route via Y.
        assert dijkstra_route.node_sequence == [a.id, x.id, b.id]
        assert astar_route.node_sequence == dijkstra_route.node_sequence
        assert abs(astar_route.total_travel_time_s - dijkstra_route.total_travel_time_s) < 1e-6

    def test_haversine_distance_calculation(self):
        """Test Haversine distance calculation."""
        router = Router(Network.create("Test"))
        
        n1 = Node.create(lat=51.0, lon=-8.0)
        n2 = Node.create(lat=51.0, lon=-8.0)  # Same location
        
        distance = router._haversine_distance(n1, n2)
        assert distance < 1  # Should be nearly zero
    
    def test_haversine_distance_nonzero(self):
        """Test Haversine distance for different locations."""
        router = Router(Network.create("Test"))
        
        n1 = Node.create(lat=51.0, lon=-8.0)
        n2 = Node.create(lat=51.01, lon=-8.01)  # Different location
        
        distance = router._haversine_distance(n1, n2)
        assert distance > 1000  # Should be at least 1 km


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
