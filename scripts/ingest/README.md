# OSM Data Ingestion

## Overview

The Cork Mobility Lab ingests road network data from OpenStreetMap (OSM) and converts it to the simulation domain models.

## Files

- `osm_download.py` - Download Cork network from OpenStreetMap via osmnx
- `osm_parser.py` - Convert OSM GeoJSON to simulation.network models
- `run_pipeline.py` - Complete ingestion pipeline orchestration

## Usage

### Option 1: Run Complete Pipeline

```bash
python scripts/ingest/run_pipeline.py
```

This will:
1. Download Cork OSM data (cached)
2. Parse to domain models
3. Save metadata
4. Create Cork network

### Option 2: Manual Steps

```bash
# Download
python scripts/ingest/osm_download.py

# Parse
python scripts/ingest/osm_parser.py
```

## Data Sources

**OpenStreetMap** (https://www.openstreetmap.org)
- License: ODbL (Open Data Commons Open Database License)
- Attribution required
- Free to download and use

### Cork Coordinates
- **Center**: 51.8985°N, 8.4761°W
- **Bounding Box**: 51.95 to 51.82 (N-S), -8.35 to -8.60 (E-W)

## Road Types

The following OSM road types are supported:

| OSM Type | Simulation Type | Default Speed |
|----------|-----------------|---------------|
| motorway | MOTORWAY | 120 km/h |
| trunk | TRUNK | 100 km/h |
| primary | PRIMARY | 80 km/h |
| secondary | SECONDARY | 60 km/h |
| tertiary | TERTIARY | 50 km/h |
| residential | RESIDENTIAL | 30 km/h |
| unclassified | UNCLASSIFIED | 40 km/h |

## Output

Processed network is saved to `data/processed/`:

- `cork_network_metadata.json` - Network metadata and statistics
- `cork_edges.geojson` - Edge geometries (original OSM)
- `cork_nodes.geojson` - Node geometries (original OSM)

## Caching

OSM data is cached in `data/raw/osm_cache/` to avoid repeated downloads.

To clear cache:
```bash
rm -rf data/raw/osm_cache/
```

## Attribution

Data sourced from OpenStreetMap and contributors.

© OpenStreetMap contributors.
ODbL: https://opendatacommons.org/licenses/odbl/
