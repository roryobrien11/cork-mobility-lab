"""
Tests using sample Cork network fixtures.
"""

import pytest

from data.sample.create_fixtures import create_sample_cork_network, save_sample_network_geojson


class TestSampleNetwork:
    """Test sample Cork network generation."""

    def test_create_sample_network(self):
        """Test creating sample network."""
        network = create_sample_cork_network()
        
        assert network is not None
        assert network.num_nodes() > 0
        assert network.num_edges() > 0

    def test_sample_network_has_city_center(self):
        """Test that sample network includes key Cork locations."""
        network = create_sample_cork_network()
        
        # Should have at least some junctions
        assert network.num_nodes() >= 10
        
        # Check approximate Cork coordinates
        for node in network.nodes.values():
            assert 51.8 < node.lat < 51.95
            assert -8.6 < node.lon < -8.35

    def test_sample_network_connectivity(self):
        """Test that sample network is connected."""
        network = create_sample_cork_network()
        
        # Most nodes should have outgoing edges
        nodes_with_outgoing = sum(
            1 for node in network.nodes.values()
            if len(node.outgoing_edges) > 0
        )
        
        assert nodes_with_outgoing > len(network.nodes) * 0.5

    def test_sample_network_realism(self):
        """Test that sample network has realistic properties."""
        network = create_sample_cork_network()
        
        # Get some statistics
        speeds = [e.speed_limit_kmh for e in network.edges.values()]
        lengths = [e.length_m for e in network.edges.values()]
        
        # Speeds should be reasonable
        assert min(speeds) >= 30  # km/h
        assert max(speeds) <= 100  # km/h
        
        # Lengths should be reasonable urban/suburban distances
        assert min(lengths) >= 100  # meters
        assert max(lengths) <= 5000  # meters

    def test_save_geojson_format(self):
        """Test that GeoJSON is saved in correct format."""
        network = create_sample_cork_network()
        nodes_file, edges_file = save_sample_network_geojson(
            network,
            output_dir="data/sample"
        )
        
        import os
        assert os.path.exists(nodes_file)
        assert os.path.exists(edges_file)
        
        # Load and validate GeoJSON structure
        import json
        with open(nodes_file) as f:
            nodes_data = json.load(f)
            assert nodes_data["type"] == "FeatureCollection"
            assert len(nodes_data["features"]) == network.num_nodes()
        
        with open(edges_file) as f:
            edges_data = json.load(f)
            assert edges_data["type"] == "FeatureCollection"
            assert len(edges_data["features"]) == network.num_edges()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
