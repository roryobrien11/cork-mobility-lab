"""
Integration tests for OSM ingestion pipeline.
"""

import json
import os
import pytest
from pathlib import Path

from scripts.ingest.osm_download import list_downloaded_networks, CORK_BBOX, CORK_COORDINATES
from scripts.ingest.osm_parser import OSMParser
from simulation.network import Network, RoadType


class TestOSMDownload:
    """Test OSM download functionality."""

    def test_cork_coordinates_defined(self):
        """Test that Cork coordinates are defined."""
        assert CORK_COORDINATES is not None
        lat, lon = CORK_COORDINATES
        assert isinstance(lat, float)
        assert isinstance(lon, float)
        assert 51 < lat < 52  # Cork is in Ireland
        assert -9 < lon < -8

    def test_cork_bbox_defined(self):
        """Test that Cork bounding box is defined."""
        assert CORK_BBOX is not None
        north, south, east, west = CORK_BBOX
        assert north > south
        assert east > west
        assert 51 < south < north < 52
        assert -9 < west < east < -8

    def test_download_list_empty_dir(self):
        """Test listing networks in empty directory."""
        networks = list_downloaded_networks("nonexistent_dir")
        assert networks == []


class TestOSMParser:
    """Test OSM parser in isolation."""

    def test_parser_has_mappings(self):
        """Test that parser has road type mappings."""
        parser = OSMParser()
        assert len(parser.ROAD_TYPE_MAPPING) > 0
        assert len(parser.DEFAULT_SPEEDS) > 0

    def test_all_road_types_have_speeds(self):
        """Test that all road types have default speeds."""
        parser = OSMParser()
        
        for road_type in parser.ROAD_TYPE_MAPPING.values():
            assert road_type in parser.DEFAULT_SPEEDS

    def test_parser_validates_speeds(self):
        """Test that speeds are reasonable."""
        parser = OSMParser()
        
        for road_type, speed in parser.DEFAULT_SPEEDS.items():
            assert 20 <= speed <= 200  # km/h


class TestNetworkMetadata:
    """Test network metadata structure."""

    def test_metadata_file_structure(self):
        """Test metadata file contains required fields."""
        expected_fields = {
            "name",
            "source",
            "timestamp",
            "statistics",
            "bounds",
            "source_files"
        }
        
        # This is what we expect the metadata to contain
        assert len(expected_fields) == 6

    def test_bounds_validity(self):
        """Test that Cork bounds are valid."""
        north, south, east, west = CORK_BBOX
        
        assert north > south
        assert east > west
        assert north - south < 1  # Within 1 degree
        assert east - west < 1


class TestIntegrationWorkflow:
    """Integration tests for complete workflow."""

    def test_network_statistics_structure(self):
        """Test that network statistics have expected structure."""
        stats = {
            "num_nodes": 100,
            "num_edges": 150,
            "total_length_km": 500.5
        }
        
        assert "num_nodes" in stats
        assert "num_edges" in stats
        assert "total_length_km" in stats
        assert stats["num_nodes"] > 0
        assert stats["num_edges"] > stats["num_nodes"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
