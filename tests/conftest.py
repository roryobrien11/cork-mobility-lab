"""
Test configuration and fixtures.
"""

import pytest
from simulation.network import Network, Node, Edge, JunctionType


@pytest.fixture
def sample_network() -> Network:
    """Create a simple test network."""
    network = Network.create("Test Network")
    
    # Create 4 nodes in a square
    node_a = Node.create(lat=51.90, lon=-8.47, junction_type=JunctionType.PRIORITY)
    node_b = Node.create(lat=51.91, lon=-8.47, junction_type=JunctionType.PRIORITY)
    node_c = Node.create(lat=51.91, lon=-8.46, junction_type=JunctionType.PRIORITY)
    node_d = Node.create(lat=51.90, lon=-8.46, junction_type=JunctionType.PRIORITY)
    
    network.add_node(node_a)
    network.add_node(node_b)
    network.add_node(node_c)
    network.add_node(node_d)
    
    # Create edges
    edge_ab = Edge.create(node_a.id, node_b.id, length_m=1000, speed_limit_kmh=50)
    edge_bc = Edge.create(node_b.id, node_c.id, length_m=1000, speed_limit_kmh=50)
    edge_cd = Edge.create(node_c.id, node_d.id, length_m=1000, speed_limit_kmh=50)
    edge_da = Edge.create(node_d.id, node_a.id, length_m=1000, speed_limit_kmh=50)
    
    network.add_edge(edge_ab)
    network.add_edge(edge_bc)
    network.add_edge(edge_cd)
    network.add_edge(edge_da)
    
    return network
