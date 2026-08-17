"""
Unit tests for network domain models.
"""

import pytest
from simulation.network import Network, Node, Edge, JunctionType, RoadType


class TestNode:
    """Test Node model."""
    
    def test_create_node(self):
        """Test node creation."""
        node = Node.create(lat=51.90, lon=-8.47)
        assert node.lat == 51.90
        assert node.lon == -8.47
        assert node.junction_type == JunctionType.PRIORITY
        assert node.id is not None
    
    def test_node_with_junction_type(self):
        """Test node with specific junction type."""
        node = Node.create(lat=51.90, lon=-8.47, junction_type=JunctionType.SIGNALS)
        assert node.junction_type == JunctionType.SIGNALS


class TestEdge:
    """Test Edge model."""
    
    def test_create_edge(self):
        """Test edge creation."""
        node_a = Node.create(lat=51.90, lon=-8.47)
        node_b = Node.create(lat=51.91, lon=-8.47)
        
        edge = Edge.create(node_a.id, node_b.id, length_m=1000, speed_limit_kmh=50)
        assert edge.length_m == 1000
        assert edge.speed_limit_kmh == 50
        assert edge.source_id == node_a.id
        assert edge.target_id == node_b.id
    
    def test_travel_time_free_flow(self):
        """Test travel time calculation at free flow."""
        node_a = Node.create(lat=51.90, lon=-8.47)
        node_b = Node.create(lat=51.91, lon=-8.47)
        
        edge = Edge.create(node_a.id, node_b.id, length_m=1000, speed_limit_kmh=36)
        # 36 km/h = 10 m/s
        # Travel time = 1000m / 10 m/s = 100s
        assert edge.travel_time_s() == 100.0
    
    def test_travel_time_custom_speed(self):
        """Test travel time with custom speed."""
        node_a = Node.create(lat=51.90, lon=-8.47)
        node_b = Node.create(lat=51.91, lon=-8.47)
        
        edge = Edge.create(node_a.id, node_b.id, length_m=1000, speed_limit_kmh=50)
        # At 5 m/s: 1000 / 5 = 200s
        assert edge.travel_time_s(speed_ms=5.0) == 200.0
    
    def test_congestion_level(self):
        """Test congestion calculation."""
        node_a = Node.create(lat=51.90, lon=-8.47)
        node_b = Node.create(lat=51.91, lon=-8.47)
        
        edge = Edge.create(node_a.id, node_b.id, length_m=1000, speed_limit_kmh=50)
        assert edge.congestion_level() == 0.0
        
        # Set some vehicles
        edge.current_vehicle_count = 10
        congestion = edge.congestion_level()
        assert 0 < congestion <= 1.0


class TestNetwork:
    """Test Network model."""
    
    def test_create_network(self):
        """Test network creation."""
        network = Network.create("Test Network")
        assert network.name == "Test Network"
        assert network.num_nodes() == 0
        assert network.num_edges() == 0
    
    def test_add_nodes(self):
        """Test adding nodes."""
        network = Network.create()
        node = Node.create(lat=51.90, lon=-8.47)
        
        network.add_node(node)
        assert network.num_nodes() == 1
        assert node.id in network.nodes
    
    def test_add_edge(self):
        """Test adding edge."""
        network = Network.create()
        node_a = Node.create(lat=51.90, lon=-8.47)
        node_b = Node.create(lat=51.91, lon=-8.47)
        
        network.add_node(node_a)
        network.add_node(node_b)
        
        edge = Edge.create(node_a.id, node_b.id, length_m=1000, speed_limit_kmh=50)
        network.add_edge(edge)
        
        assert network.num_edges() == 1
        assert edge.id in network.edges
    
    def test_add_edge_missing_node(self):
        """Test adding edge with missing node."""
        network = Network.create()
        node_a = Node.create(lat=51.90, lon=-8.47)
        node_b = Node.create(lat=51.91, lon=-8.47)
        
        network.add_node(node_a)
        
        edge = Edge.create(node_a.id, node_b.id, length_m=1000, speed_limit_kmh=50)
        
        with pytest.raises(ValueError):
            network.add_edge(edge)
    
    def test_outgoing_edges(self):
        """Test getting outgoing edges."""
        network = Network.create()
        node_a = Node.create(lat=51.90, lon=-8.47)
        node_b = Node.create(lat=51.91, lon=-8.47)
        node_c = Node.create(lat=51.92, lon=-8.47)
        
        network.add_node(node_a)
        network.add_node(node_b)
        network.add_node(node_c)
        
        edge_ab = Edge.create(node_a.id, node_b.id, length_m=1000, speed_limit_kmh=50)
        edge_ac = Edge.create(node_a.id, node_c.id, length_m=1000, speed_limit_kmh=50)
        
        network.add_edge(edge_ab)
        network.add_edge(edge_ac)
        
        outgoing = network.get_outgoing_edges(node_a.id)
        assert len(outgoing) == 2
    
    def test_network_stats(self, sample_network):
        """Test network statistics."""
        assert sample_network.num_nodes() == 4
        assert sample_network.num_edges() == 4
        assert sample_network.total_length_m() == 4000.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
