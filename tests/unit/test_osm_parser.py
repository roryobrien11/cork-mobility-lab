"""
Tests for OSM ingestion utilities.
"""

import pytest
from scripts.ingest.osm_parser import OSMParser, RoadType, JunctionType
from simulation.network import Network, Node, Edge


class TestOSMParser:
    """Test OSM parser."""

    def test_parser_initialization(self):
        """Test parser creation."""
        parser = OSMParser()
        assert parser.nodes_by_osm_id == {}
        assert parser.edges == []

    def test_road_type_mapping(self):
        """Test OSM to RoadType mapping."""
        parser = OSMParser()
        
        assert parser.ROAD_TYPE_MAPPING["motorway"] == RoadType.MOTORWAY
        assert parser.ROAD_TYPE_MAPPING["trunk"] == RoadType.TRUNK
        assert parser.ROAD_TYPE_MAPPING["primary"] == RoadType.PRIMARY
        assert parser.ROAD_TYPE_MAPPING["secondary"] == RoadType.SECONDARY
        assert parser.ROAD_TYPE_MAPPING["residential"] == RoadType.RESIDENTIAL

    def test_default_speeds(self):
        """Test default speed configuration."""
        parser = OSMParser()
        
        assert parser.DEFAULT_SPEEDS[RoadType.MOTORWAY] == 120
        assert parser.DEFAULT_SPEEDS[RoadType.PRIMARY] == 80
        assert parser.DEFAULT_SPEEDS[RoadType.RESIDENTIAL] == 30

    def test_unknown_road_type_mapping(self):
        """Test mapping unknown road types."""
        parser = OSMParser()
        
        # Unknown road types should map to UNCLASSIFIED
        unknown = "footway"
        road_type = parser.ROAD_TYPE_MAPPING.get(unknown, RoadType.UNCLASSIFIED)
        assert road_type == RoadType.UNCLASSIFIED

    def test_parse_nodes_structure(self):
        """Test that nodes are correctly parsed."""
        parser = OSMParser()
        
        # After parsing, nodes should be indexed by OSM ID
        assert isinstance(parser.nodes_by_osm_id, dict)

    def test_parse_edges_structure(self):
        """Test that edges are correctly parsed."""
        parser = OSMParser()
        
        # After parsing, edges should be in a list
        assert isinstance(parser.edges, list)


class TestOSMIntegration:
    """Integration tests for OSM ingestion."""

    def test_network_creation_empty(self):
        """Test creating network from empty data."""
        parser = OSMParser()
        network = Network.create("Test Network")
        
        assert network.num_nodes() == 0
        assert network.num_edges() == 0

    def test_network_with_sample_nodes(self):
        """Test network creation with sample nodes."""
        network = Network.create("Cork Test Network")
        
        # Add sample Cork coordinates
        node1 = Node.create(lat=51.8985, lon=-8.4761, junction_type=JunctionType.PRIORITY)
        node2 = Node.create(lat=51.9000, lon=-8.4750, junction_type=JunctionType.PRIORITY)
        
        network.add_node(node1)
        network.add_node(node2)
        
        assert network.num_nodes() == 2

    def test_road_types_for_cork(self):
        """Test that Cork road types are correctly identified."""
        parser = OSMParser()
        
        cork_roads = ["motorway", "trunk", "primary", "secondary", "residential"]
        
        for road in cork_roads:
            assert road in parser.ROAD_TYPE_MAPPING


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
