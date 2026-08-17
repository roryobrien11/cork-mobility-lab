#!/usr/bin/env python3
"""
Cork Mobility Lab - OSM Data Ingestion Pipeline

Complete workflow for downloading and processing OpenStreetMap data for Cork.
"""

import logging
import json
import os
from pathlib import Path
from datetime import datetime

from scripts.ingest.osm_download import download_cork_network
from scripts.ingest.osm_parser import parse_cork_network

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_ingestion_pipeline(
    output_dir: str = "data/processed",
    cache_dir: str = "data/raw/osm_cache",
    network_name: str = "Cork Network",
    skip_download: bool = False
) -> dict:
    """
    Run complete OSM ingestion pipeline.

    Args:
        output_dir: Output directory for processed network
        cache_dir: OSM data cache directory
        network_name: Name for the network
        skip_download: Skip download if data already exists

    Returns:
        Dictionary with pipeline results
    """
    
    logger.info("=" * 60)
    logger.info("Cork Mobility Lab - OSM Ingestion Pipeline")
    logger.info("=" * 60)

    results = {
        "timestamp": datetime.now().isoformat(),
        "network_name": network_name,
        "status": "running",
        "steps": {}
    }

    os.makedirs(output_dir, exist_ok=True)

    try:
        # Step 1: Download OSM data
        logger.info("\n📥 STEP 1: Downloading OpenStreetMap data for Cork...")
        logger.info("-" * 60)

        edges_file = "data/raw/cork_edges.geojson"
        nodes_file = "data/raw/cork_nodes.geojson"

        if skip_download and os.path.exists(edges_file) and os.path.exists(nodes_file):
            logger.info("✅ Using cached OSM data")
            results["steps"]["download"] = {
                "status": "skipped",
                "reason": "data_already_exists"
            }
        else:
            edges_file = download_cork_network(
                output_dir="data/raw",
                cache_dir=cache_dir
            )
            nodes_file = "data/raw/cork_nodes.geojson"
            
            results["steps"]["download"] = {
                "status": "completed",
                "edges_file": edges_file,
                "nodes_file": nodes_file
            }

        # Step 2: Parse OSM data to domain models
        logger.info("\n🔄 STEP 2: Parsing OSM data to network models...")
        logger.info("-" * 60)

        network = parse_cork_network(nodes_file=nodes_file, edges_file=edges_file)

        results["steps"]["parse"] = {
            "status": "completed",
            "num_nodes": network.num_nodes(),
            "num_edges": network.num_edges(),
            "total_length_km": network.total_length_m() / 1000
        }

        # Step 3: Save network metadata
        logger.info("\n💾 STEP 3: Saving network metadata...")
        logger.info("-" * 60)

        metadata_file = os.path.join(output_dir, "cork_network_metadata.json")
        
        metadata = {
            "name": network_name,
            "source": "OpenStreetMap",
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "num_nodes": network.num_nodes(),
                "num_edges": network.num_edges(),
                "total_length_km": network.total_length_m() / 1000
            },
            "bounds": {
                "north": 51.95,
                "south": 51.82,
                "east": -8.35,
                "west": -8.60
            },
            "source_files": {
                "nodes": nodes_file,
                "edges": edges_file
            }
        }

        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"✅ Metadata saved to {metadata_file}")

        results["steps"]["metadata"] = {
            "status": "completed",
            "metadata_file": metadata_file
        }

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("✅ PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info(f"\n📊 Summary:")
        logger.info(f"  Network: {network_name}")
        logger.info(f"  Nodes: {network.num_nodes()}")
        logger.info(f"  Edges: {network.num_edges()}")
        logger.info(f"  Total length: {network.total_length_m() / 1000:.1f} km")
        logger.info(f"  Metadata: {metadata_file}")

        results["status"] = "completed"
        results["network"] = {
            "num_nodes": network.num_nodes(),
            "num_edges": network.num_edges(),
            "total_length_km": network.total_length_m() / 1000
        }

        return results

    except Exception as e:
        logger.error(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        
        results["status"] = "failed"
        results["error"] = str(e)
        
        return results


if __name__ == "__main__":
    results = run_ingestion_pipeline(skip_download=True)
    
    if results["status"] == "completed":
        print("\n✅ Ingestion pipeline completed successfully!")
        exit(0)
    else:
        print(f"\n❌ Pipeline failed!")
        exit(1)
