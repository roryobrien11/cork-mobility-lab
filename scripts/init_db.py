#!/usr/bin/env python3
"""
Initialize Cork Mobility Lab database.

Creates tables, spatial indexes, and sample data.
"""

import os
import sys
from sqlalchemy import create_engine, text

def main():
    """Initialize database."""
    db_url = os.getenv("DATABASE_URL", "postgresql://cork_user:cork_password@localhost:5432/cork_mobility")
    
    print("🗄️  Cork Mobility Lab Database Initialization")
    print("=" * 50)
    print(f"Database: {db_url}")
    print()
    
    try:
        # Create engine
        engine = create_engine(db_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL:")
            print(f"   {version}")
        
        print()
        print("📝 Creating tables...")
        
        # Create tables
        with engine.begin() as conn:
            # Enable PostGIS
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            
            # Network tables
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS networks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    source TEXT,
                    num_nodes INTEGER DEFAULT 0,
                    num_edges INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS network_nodes (
                    id TEXT PRIMARY KEY,
                    network_id TEXT NOT NULL REFERENCES networks(id),
                    lat FLOAT8 NOT NULL,
                    lon FLOAT8 NOT NULL,
                    junction_type TEXT,
                    geom GEOMETRY(POINT, 4326),
                    FOREIGN KEY (network_id) REFERENCES networks(id)
                );
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS network_edges (
                    id TEXT PRIMARY KEY,
                    network_id TEXT NOT NULL,
                    source_id TEXT NOT NULL REFERENCES network_nodes(id),
                    target_id TEXT NOT NULL REFERENCES network_nodes(id),
                    length_m FLOAT8 NOT NULL,
                    speed_limit_kmh FLOAT8 NOT NULL,
                    lanes INTEGER DEFAULT 1,
                    road_type TEXT,
                    geom GEOMETRY(LINESTRING, 4326),
                    FOREIGN KEY (network_id) REFERENCES networks(id)
                );
            """))
            
            # Simulations
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS simulations (
                    id TEXT PRIMARY KEY,
                    network_id TEXT NOT NULL REFERENCES networks(id),
                    scenario_id TEXT,
                    config JSONB,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (network_id) REFERENCES networks(id)
                );
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS simulation_results (
                    id TEXT PRIMARY KEY,
                    simulation_id TEXT NOT NULL REFERENCES simulations(id),
                    avg_journey_time_s FLOAT8,
                    total_vehicle_hours FLOAT8,
                    congestion_index FLOAT8,
                    metrics JSONB,
                    FOREIGN KEY (simulation_id) REFERENCES simulations(id)
                );
            """))
            
            # Spatial indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_nodes_geom ON network_nodes USING GIST(geom);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_edges_geom ON network_edges USING GIST(geom);"))
            
            # Other indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_nodes_network ON network_nodes(network_id);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_edges_network ON network_edges(network_id);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_simulations_network ON simulations(network_id);"))
            
        print("✅ Tables created successfully")
        
        print()
        print("🎉 Database initialization complete!")
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
