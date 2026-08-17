"""
Create sample Cork network for testing without OSM download.
"""

import json
from pathlib import Path

from simulation.network import Network, Node, Edge, RoadType, JunctionType


def create_sample_cork_network() -> Network:
    """
    Create a sample Cork network for testing.
    
    This is a simplified mock of Cork's actual road network
    suitable for testing without downloading real OSM data.
    
    Returns:
        Network domain model
    """
    
    network = Network.create("Sample Cork Network")
    
    # Create key junctions (real Cork locations with approximate coords)
    # Cork city center and surrounding areas
    
    junctions = {
        "city_center": Node.create(lat=51.8985, lon=-8.4761, junction_type=JunctionType.SIGNALS),
        "patrick_st": Node.create(lat=51.8995, lon=-8.4755, junction_type=JunctionType.SIGNALS),
        "grand_parade": Node.create(lat=51.8975, lon=-8.4745, junction_type=JunctionType.SIGNALS),
        "oliver_plunkett": Node.create(lat=51.8970, lon=-8.4780, junction_type=JunctionType.SIGNALS),
        "south_main": Node.create(lat=51.8960, lon=-8.4790, junction_type=JunctionType.PRIORITY),
        "quay": Node.create(lat=51.8975, lon=-8.4805, junction_type=JunctionType.PRIORITY),
        "college_rd": Node.create(lat=51.8920, lon=-8.4870, junction_type=JunctionType.PRIORITY),
        "western_rd": Node.create(lat=51.8900, lon=-8.4950, junction_type=JunctionType.PRIORITY),
        "mardyke": Node.create(lat=51.8930, lon=-8.4920, junction_type=JunctionType.PRIORITY),
        "n8_north": Node.create(lat=51.9100, lon=-8.4800, junction_type=JunctionType.PRIORITY),
        "n8_south": Node.create(lat=51.8800, lon=-8.4800, junction_type=JunctionType.PRIORITY),
    }
    
    # Add all junctions to network
    for junction in junctions.values():
        network.add_node(junction)
    
    # Create roads (edges) connecting junctions
    roads = [
        # City center connections
        ("city_center", "patrick_st", 150, 50, RoadType.SECONDARY),
        ("patrick_st", "grand_parade", 200, 50, RoadType.SECONDARY),
        ("grand_parade", "oliver_plunkett", 300, 50, RoadType.SECONDARY),
        ("oliver_plunkett", "city_center", 250, 50, RoadType.SECONDARY),
        
        # South Main Street (major route)
        ("city_center", "south_main", 500, 60, RoadType.SECONDARY),
        ("south_main", "quay", 400, 60, RoadType.SECONDARY),
        
        # College Road
        ("grand_parade", "college_rd", 1500, 50, RoadType.TERTIARY),
        ("college_rd", "mardyke", 800, 50, RoadType.TERTIARY),
        
        # Western Road
        ("mardyke", "western_rd", 1000, 50, RoadType.TERTIARY),
        
        # N8 connections
        ("city_center", "n8_north", 3000, 100, RoadType.PRIMARY),
        ("city_center", "n8_south", 3500, 100, RoadType.PRIMARY),
        
        # Return routes (simplified two-way as separate edges)
        ("patrick_st", "city_center", 150, 50, RoadType.SECONDARY),
        ("grand_parade", "patrick_st", 200, 50, RoadType.SECONDARY),
        ("oliver_plunkett", "grand_parade", 300, 50, RoadType.SECONDARY),
        ("city_center", "oliver_plunkett", 250, 50, RoadType.SECONDARY),
    ]
    
    for source, target, length, speed, road_type in roads:
        if source in junctions and target in junctions:
            edge = Edge.create(
                source_id=junctions[source].id,
                target_id=junctions[target].id,
                length_m=length,
                speed_limit_kmh=speed
            )
            edge.road_type = road_type
            edge.lanes = 2 if road_type == RoadType.SECONDARY else 1
            network.add_edge(edge)
    
    return network


def save_sample_network_geojson(
    network: Network,
    output_dir: str = "data/sample"
) -> tuple:
    """
    Save sample network as GeoJSON for inspection.
    
    Args:
        network: Network to save
        output_dir: Output directory
        
    Returns:
        (nodes_file, edges_file)
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Save nodes
    nodes_data = {
        "type": "FeatureCollection",
        "features": []
    }
    
    for node in network.nodes.values():
        nodes_data["features"].append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [node.lon, node.lat]
            },
            "properties": {
                "id": node.id,
                "junction_type": node.junction_type.value
            }
        })
    
    nodes_file = os.path.join(output_dir, "sample_nodes.geojson")
    with open(nodes_file, "w") as f:
        json.dump(nodes_data, f, indent=2)
    
    # Save edges
    edges_data = {
        "type": "FeatureCollection",
        "features": []
    }
    
    for edge in network.edges.values():
        source_node = network.nodes[edge.source_id]
        target_node = network.nodes[edge.target_id]
        
        edges_data["features"].append({
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [source_node.lon, source_node.lat],
                    [target_node.lon, target_node.lat]
                ]
            },
            "properties": {
                "id": edge.id,
                "length_m": edge.length_m,
                "speed_kmh": edge.speed_limit_kmh,
                "lanes": edge.lanes,
                "road_type": edge.road_type.value
            }
        })
    
    edges_file = os.path.join(output_dir, "sample_edges.geojson")
    with open(edges_file, "w") as f:
        json.dump(edges_data, f, indent=2)
    
    return nodes_file, edges_file


if __name__ == "__main__":
    # Create and save sample network
    print("Creating sample Cork network...")
    network = create_sample_cork_network()
    
    print(f"✅ Sample network created:")
    print(f"  Nodes: {network.num_nodes()}")
    print(f"  Edges: {network.num_edges()}")
    print(f"  Total length: {network.total_length_m() / 1000:.1f} km")
    
    print("\nSaving as GeoJSON...")
    nodes_file, edges_file = save_sample_network_geojson(network)
    
    print(f"✅ Saved:")
    print(f"  {nodes_file}")
    print(f"  {edges_file}")
