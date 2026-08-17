# Data Sources

This document tracks every external dataset ingested by Cork Mobility Lab: its
source, licence, acquisition method, and how it was processed. Per the
project's scientific-integrity principle, nothing in this file should be
taken as a claim that the simulation has been calibrated against it — see
[calibration.md](calibration.md) (not yet written) for validation status.

## Road network — OpenStreetMap

| | |
|---|---|
| **Source** | [OpenStreetMap](https://www.openstreetmap.org) via the [Overpass API](https://overpass-api.de/), fetched with the [`osmnx`](https://osmnx.readthedocs.io/) Python library |
| **Licence** | [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/) |
| **Attribution** | © OpenStreetMap contributors |
| **Coverage** | Cork city and immediate environs, bounding box 51.82–51.95°N, 8.35–8.60°W (`CORK_BBOX` in [scripts/ingest/osm_download.py](../scripts/ingest/osm_download.py)) |
| **Network type** | `drive` (car-accessible roads only; walk/bike/rail networks are not yet ingested) |
| **Date acquired (this dataset)** | 2026-08-17 |

### How to reproduce

```bash
python -m scripts.ingest.run_pipeline
```

This downloads the network from Overpass (cached under `data/raw/osm_cache/`
so repeat runs don't re-download), converts it to the `simulation.network`
domain model, and writes `data/processed/cork_network_metadata.json`.
`data/raw/` and `data/processed/` are gitignored — they are regenerated from
this pipeline, not committed, since OSM data changes over time and the ODbL
share-alike/attribution terms are simpler to satisfy by re-fetching than by
redistributing a snapshot in this repository.

### Result of the 2026-08-17 run

| Metric | Value |
|---|---|
| Nodes | 10,400 |
| Edges (directed road segments) | 22,801 |
| Total network length | 2,511 km |

These are **raw counts from the current bounding box**, not a claim about
Cork's "true" road network size — OSM completeness varies by area, and the
bbox includes a wide surrounding area, not just the city centre.

### Known processing limitations

- **Edge length**: preferred source is osmnx's own geodesic `length` column
  (metres, computed from the projected geometry). Where that column is
  absent, [`osm_parser.py`](../scripts/ingest/osm_parser.py) falls back to a
  flat `degrees × 111,000` approximation, which understates east–west
  distances at Cork's latitude (~52°N) by roughly 30% — this fallback path
  is not expected to trigger for osmnx-sourced data but exists for
  robustness against other GeoJSON sources.
- **Speed limits**: OSM's `maxspeed` tag is frequently missing. Where
  absent (or unparseable, e.g. `"national"` or a unit string osmnx doesn't
  normalise), the parser substitutes a default by road class (see the table
  in [scripts/ingest/README.md](../scripts/ingest/README.md)). These
  defaults are **modelling assumptions**, not observed speed limits.
- **Turning restrictions, lane-level topology, and traffic-signal timing**
  are not currently extracted from OSM tags — junctions are created as
  generic priority junctions regardless of their real-world control type.

## Synthetic / sample data

`data/sample/` contains a small, hand-generated fixture network
(`sample_nodes.geojson`, `sample_edges.geojson`, built by
[create_fixtures.py](../data/sample/create_fixtures.py)) used for fast unit
tests. It is **not derived from real Cork geography** and must never be
treated as representative of actual Cork traffic conditions — it exists so
tests don't depend on network access to the Overpass API.

## Planned / not yet integrated

The following sources are referenced in the project plan but have no
ingestion code yet. Do not assume any of these are wired into the
simulation:

- Cork City Council traffic counts
- Transport Infrastructure Ireland (TII) national traffic-count data
- National Transport Authority (NTA) public transport / GTFS data
- CSO demographic data (population/employment, for demand-zone generation)

When any of these is added, this file must be updated with the same fields
as the OSM entry above: source, licence, download method, date acquired,
and processing description.
