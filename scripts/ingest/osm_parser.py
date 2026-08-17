#!/usr/bin/env python3
"""
Parse OpenStreetMap data into Cork Mobility Lab network models.

Converts OSM nodes/edges to simulation.network.Node/Edge domain models.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

import geopandas as gpd
from shapely.geometry import Point, LineString

from simulation.network import Network, Node, Edge, RoadType, JunctionType

logger = logging.getLogger(__name__)


def _read_geojson(path: str) -> gpd.GeoDataFrame:
    """
    Read a GeoJSON file into a GeoDataFrame without requiring fiona/pyogrio
    (and therefore without requiring a working GDAL install). We only ever
    read files this pipeline wrote itself via GeoDataFrame.to_json(), so a
    plain feature-collection parse is sufficient.
    """
    with open(path, "r", encoding="utf-8") as f:
        geojson = json.load(f)
    return gpd.GeoDataFrame.from_features(geojson["features"], crs="EPSG:4326")


class OSMParser:
    """Parse OSM GeoJSON into simulation domain models."""

    # Mapping of OSM road types to our RoadType enum
    ROAD_TYPE_MAPPING = {
        "motorway": RoadType.MOTORWAY,
        "trunk": RoadType.TRUNK,
        "primary": RoadType.PRIMARY,
        "secondary": RoadType.SECONDARY,
        "tertiary": RoadType.TERTIARY,
        "residential": RoadType.RESIDENTIAL,
        "unclassified": RoadType.UNCLASSIFIED,
    }

    # Default speeds by road type (km/h)
    DEFAULT_SPEEDS = {
        RoadType.MOTORWAY: 120,
        RoadType.TRUNK: 100,
        RoadType.PRIMARY: 80,
        RoadType.SECONDARY: 60,
        RoadType.TERTIARY: 50,
        RoadType.RESIDENTIAL: 30,
        RoadType.UNCLASSIFIED: 40,
    }

    def __init__(self):
        """Initialize parser."""
        self.nodes_by_osm_id: Dict[int, Node] = {}
        self.edges: List[Edge] = []

    def parse_network(
        self,
        nodes_file: str,
        edges_file: str
    ) -> Network:
        """
        Parse OSM GeoJSON files into network model.

        Args:
            nodes_file: Path to nodes GeoJSON
            edges_file: Path to edges GeoJSON

        Returns:
            Network domain model
        """
        logger.info(f"Parsing nodes from {nodes_file}")
        nodes_gdf = _read_geojson(nodes_file)
        self._parse_nodes(nodes_gdf)

        logger.info(f"Parsing edges from {edges_file}")
        edges_gdf = _read_geojson(edges_file)
        self._parse_edges(edges_gdf)

        # Create network
        network = Network.create("Cork OSM Network")
        
        for node in self.nodes_by_osm_id.values():
            network.add_node(node)

        for edge in self.edges:
            try:
                network.add_edge(edge)
            except ValueError as e:
                logger.warning(f"Skipping edge {edge.id}: {e}")

        logger.info(f"Created network: {network.num_nodes()} nodes, {network.num_edges()} edges")
        logger.info(f"Total length: {network.total_length_m() / 1000:.1f} km")

        return network

    def _parse_nodes(self, nodes_gdf: gpd.GeoDataFrame) -> None:
        """Parse nodes from GeoDataFrame."""
        for idx, row in nodes_gdf.iterrows():
            osm_id = row.get("osmid", idx)
            
            # Get coordinates from geometry
            if row.geometry.geom_type == "Point":
                lon, lat = row.geometry.x, row.geometry.y
            else:
                logger.warning(f"Non-point geometry for node {osm_id}, skipping")
                continue

            node = Node.create(lat=lat, lon=lon, junction_type=JunctionType.PRIORITY)
            self.nodes_by_osm_id[osm_id] = node
            logger.debug(f"Parsed node {osm_id}: ({lat:.4f}, {lon:.4f})")

    def _parse_edges(self, edges_gdf: gpd.GeoDataFrame) -> None:
        """Parse edges from GeoDataFrame."""
        for idx, row in edges_gdf.iterrows():
            # Get OSM node IDs
            u = row.get("u")  # Source node
            v = row.get("v")  # Target node

            if u not in self.nodes_by_osm_id or v not in self.nodes_by_osm_id:
                logger.debug(f"Skipping edge {u}->{v}: nodes not found")
                continue

            source_node = self.nodes_by_osm_id[u]
            target_node = self.nodes_by_osm_id[v]

            # Prefer osmnx's precomputed geodesic length (metres); it accounts
            # for the fact that a degree of longitude is shorter than a degree
            # of latitude at Cork's ~52N latitude, unlike a flat degrees*111000
            # approximation.
            length_m = row.get("length")
            if length_m is None or (isinstance(length_m, float) and length_m != length_m):
                if row.geometry.geom_type == "LineString":
                    length_m = row.geometry.length * 111000
                else:
                    logger.debug(f"Non-linestring geometry for edge {u}->{v}, skipping")
                    continue
            length_m = float(length_m)

            # Get road type
            highway = row.get("highway", "unclassified")
            if isinstance(highway, list):
                highway = highway[0]
            
            road_type = self.ROAD_TYPE_MAPPING.get(highway, RoadType.UNCLASSIFIED)

            # Get speed limit (or use default). OSM ways that were split by
            # osmnx simplification can carry maxspeed/lanes as a list of
            # per-segment values (e.g. ["50", "30"]) rather than a scalar;
            # take the first value in that case.
            speed_kmh = row.get("maxspeed")
            if isinstance(speed_kmh, list):
                speed_kmh = speed_kmh[0] if speed_kmh else None
            if speed_kmh is None or speed_kmh == "":
                speed_kmh = self.DEFAULT_SPEEDS.get(road_type, 40)
            else:
                try:
                    speed_kmh = float(speed_kmh) if isinstance(speed_kmh, str) else float(speed_kmh)
                except (ValueError, TypeError):
                    speed_kmh = self.DEFAULT_SPEEDS.get(road_type, 40)

            # Get lanes
            lanes = row.get("lanes", 1)
            if isinstance(lanes, list):
                lanes = lanes[0] if lanes else 1
            try:
                lanes = int(lanes) if lanes else 1
            except (ValueError, TypeError):
                lanes = 1

            # Create edge
            edge = Edge.create(
                source_id=source_node.id,
                target_id=target_node.id,
                length_m=length_m,
                speed_limit_kmh=speed_kmh
            )
            edge.road_type = road_type
            edge.lanes = lanes

            self.edges.append(edge)
            logger.debug(f"Parsed edge {u}->{v}: {length_m:.1f}m, {speed_kmh}km/h, {lanes} lanes")

        logger.info(f"Parsed {len(self.edges)} edges")


def parse_cork_network(
    nodes_file: str = "data/raw/cork_nodes.geojson",
    edges_file: str = "data/raw/cork_edges.geojson"
) -> Network:
    """
    Parse Cork OSM network files.

    Args:
        nodes_file: Path to nodes GeoJSON
        edges_file: Path to edges GeoJSON

    Returns:
        Network model
    """
    parser = OSMParser()
    return parser.parse_network(nodes_file, edges_file)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    logging.basicConfig(level=logging.INFO)

    try:
        network = parse_cork_network()
        print(f"\n✅ Network parsed successfully!")
        print(f"  Nodes: {network.num_nodes()}")
        print(f"  Edges: {network.num_edges()}")
        print(f"  Total length: {network.total_length_m() / 1000:.1f} km")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
