#!/usr/bin/env python3
"""
Download OpenStreetMap data for Cork, Ireland.

Uses osmnx to fetch road network data from OSM.
"""

import logging
import os
from pathlib import Path
from typing import Optional

import osmnx as ox
import geopandas as gpd

logger = logging.getLogger(__name__)

# Cork city center coordinates (WGS84)
CORK_COORDINATES = (51.8985, -8.4761)

# Cork bounding box (approx)
# North, South, East, West
CORK_BBOX = (51.95, 51.82, -8.35, -8.60)


def download_cork_network(
    output_dir: str = "data/raw",
    cache_dir: str = "data/raw/osm_cache",
    tags: Optional[dict] = None,
    network_type: str = "drive"
) -> str:
    """
    Download OSM road network for Cork.

    Args:
        output_dir: Directory to save downloaded data
        cache_dir: Directory to cache OSM data
        tags: OSM tags to filter (default: all roads)
        network_type: Type of network (drive, walk, bike, all)

    Returns:
        Path to saved network file
    """
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(cache_dir, exist_ok=True)

    logger.info(f"Downloading OSM road network for Cork...")
    logger.info(f"Using cache directory: {cache_dir}")

    # Configure osmnx
    ox.settings.use_cache = True
    ox.settings.cache_folder = cache_dir
    ox.settings.log_console = False

    try:
        # Download network from OSM using bounding box
        logger.info("Fetching network from OpenStreetMap (this may take a moment)...")
        
        # Use bounding box for more reliable results
        north, south, east, west = CORK_BBOX
        graph = ox.graph_from_bbox(
            north=north,
            south=south,
            east=east,
            west=west,
            network_type=network_type,
            simplify=True,
            retain_all=False,
            truncate_by_edge=True,
            custom_filter=None
        )

        logger.info(f"Network downloaded: {len(graph.nodes)} nodes, {len(graph.edges)} edges")

        # Save as GeoJSON for inspection
        output_file = os.path.join(output_dir, "cork_network.geojson")
        nodes_file = os.path.join(output_dir, "cork_nodes.geojson")
        edges_file = os.path.join(output_dir, "cork_edges.geojson")

        # Save nodes and edges
        nodes_gdf, edges_gdf = ox.graph_to_gdfs(graph)
        
        nodes_gdf.to_file(nodes_file, driver="GeoJSON")
        edges_gdf.to_file(edges_file, driver="GeoJSON")

        logger.info(f"✅ Network saved to {edges_file}")
        logger.info(f"✅ Nodes saved to {nodes_file}")

        return edges_file

    except Exception as e:
        logger.error(f"Error downloading OSM data: {e}")
        raise


def list_downloaded_networks(data_dir: str = "data/raw") -> list:
    """List downloaded network files."""
    path = Path(data_dir)
    if not path.exists():
        return []
    return [str(f) for f in path.glob("cork_*.geojson")]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    try:
        output_file = download_cork_network()
        print(f"\n✅ Cork network downloaded to: {output_file}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)
