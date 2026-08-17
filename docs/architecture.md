# Cork Mobility Lab Architecture

## System Overview

Cork Mobility Lab is a monorepo containing:

1. **Web Application** (`apps/web/`): React/TypeScript frontend with MapLibre visualization
2. **REST API** (`apps/api/`): FastAPI backend serving network, simulation, and results data
3. **Simulation Engine** (`simulation/`): Python-based agent-based traffic model
4. **Data Pipeline** (`scripts/`): OSM ingestion, preprocessing, experiment management

## Separation of Concerns

### Simulation Engine (Independent)

The simulation engine is **completely independent** of the web application. It can be:

- Run from the command line
- Imported into Jupyter notebooks
- Called from external tools
- Containerized separately

This ensures:

- The simulation is not bound to web concerns
- Testing is simpler and faster
- Reusability in other projects
- Scalability (simulation could be distributed)

### Web API

The FastAPI backend:

- Provides REST endpoints for UI consumption
- Manages database state (networks, scenarios, results)
- Runs simulations via the simulation engine
- Returns results to frontend

### Domain Models

All domain models (Network, Vehicle, Edge, etc.) are:

- Defined in `simulation/`
- Independent of database models
- Strongly typed with Pydantic
- Tested in isolation

Database models in `apps/api/` may differ for persistence/query efficiency.

## Deployment Architecture

```
┌────────────────────────────┐
│  User Browser              │
│  (React + MapLibre)        │
└──────────────┬─────────────┘
               │
               │ HTTPS
               ▼
┌────────────────────────────┐
│  Nginx Reverse Proxy       │
│  (Routes to API, serves UI)│
└──────────────┬─────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌──────────────┐  ┌────────────────┐
│   FastAPI    │  │  Static Files  │
│   App        │  │  (React Build) │
└──────┬───────┘  └────────────────┘
       │
       ▼
┌────────────────────────────┐
│  PostgreSQL + PostGIS      │
│  (Network, Scenarios, Logs)│
└────────────────────────────┘
       │
       └─────────────────────────┐
                                 │
                    (On Demand)  ▼
                        ┌────────────────┐
                        │ Simulation     │
                        │ Engine         │
                        │ (Python)       │
                        └────────────────┘
```

## Key Design Principles

### 1. Type Safety

**Python**:
- Pydantic models for all data structures
- Type hints on all functions
- mypy for static checking

**TypeScript**:
- Strict mode enabled
- React component props typed
- API responses typed via Pydantic OpenAPI schema

### 2. Determinism

Simulations are reproducible:

```python
# Same seed + configuration = same result
sim = Simulation(config, seed=42)
result1 = sim.run()

sim2 = Simulation(config, seed=42)
result2 = sim.run()

assert result1 == result2  # Always true
```

### 3. Configuration Over Hardcoding

All parameters are configurable:

```yaml
# experiments/configs/baseline.yaml
network:
  source: osm_cork_2024
  filter: highway in [motorway, trunk, primary, secondary, tertiary]

demand:
  generator: synthetic_zones
  peak_hour_demand: 8000_vehicles_per_hour
  
simulation:
  duration: 3600  # seconds
  timestep: 1.0
  random_seed: 42

output:
  metrics_file: results/baseline_metrics.json
  vehicle_trajectories: false
```

### 4. Testability

```python
# Units are tested in isolation
def test_network_routing():
    network = sample_network()
    route = find_shortest_path(network, "A", "C")
    assert len(route) == 2

# Integration tests verify API + DB
def test_api_get_network():
    response = client.get("/api/network")
    assert response.status_code == 200
    network = NetworkSchema(**response.json())
    assert network.num_edges > 0
```

### 5. Modularity

```python
# Easy to swap components
simulation = Simulation(
    network=real_cork_network,
    demand=synthetic_demand_from_zones,
    routing=AStarRouter(),  # or DijkstraRouter()
    car_following=IDMModel(),  # or other model
    metrics=StandardMetrics()
)
```

## Database Schema (Outline)

```sql
-- Networks
CREATE TABLE networks (
    id UUID PRIMARY KEY,
    name TEXT,
    source TEXT,
    created_at TIMESTAMP,
    num_nodes INT,
    num_edges INT
);

-- Network nodes
CREATE TABLE network_nodes (
    id UUID PRIMARY KEY,
    network_id UUID REFERENCES networks,
    osmid BIGINT,
    lat FLOAT8,
    lon FLOAT8,
    junction_type TEXT,
    geom GEOMETRY(POINT, 4326)
);

-- Network edges
CREATE TABLE network_edges (
    id UUID PRIMARY KEY,
    network_id UUID REFERENCES networks,
    osmid BIGINT,
    source_id UUID REFERENCES network_nodes,
    target_id UUID REFERENCES network_nodes,
    length_m FLOAT8,
    speed_limit_kmh FLOAT8,
    lanes INT,
    road_type TEXT,
    geom GEOMETRY(LINESTRING, 4326)
);

-- Simulations
CREATE TABLE simulations (
    id UUID PRIMARY KEY,
    network_id UUID REFERENCES networks,
    scenario_id UUID,
    config JSONB,
    status TEXT,
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Simulation results
CREATE TABLE simulation_results (
    id UUID PRIMARY KEY,
    simulation_id UUID REFERENCES simulations,
    avg_journey_time FLOAT8,
    total_vehicle_hours FLOAT8,
    congestion_index FLOAT8,
    metrics JSONB
);
```

## API Endpoints (Planned)

```
GET     /api/network                    Get current network
GET     /api/network/nodes              List nodes
GET     /api/network/edges              List edges
GET     /api/network/stats              Network statistics

POST    /api/scenarios                  Create scenario
GET     /api/scenarios                  List scenarios
GET     /api/scenarios/{id}             Get scenario
DELETE  /api/scenarios/{id}             Delete scenario

POST    /api/simulations                Run simulation
GET     /api/simulations                List simulations
GET     /api/simulations/{id}           Get simulation status
GET     /api/simulations/{id}/metrics   Get results
GET     /api/simulations/{id}/log       Get progress log

GET     /api/experiments                List experiments
GET     /api/experiments/{id}           Get experiment results
POST    /api/experiments/compare        Compare scenarios
```

## Simulation Loop (Pseudocode)

```python
def run_simulation(config: SimulationConfig):
    network = load_network(config.network_id)
    demand = generate_demand(config.demand_config)
    vehicles = []
    time = config.start_time
    
    while time <= config.end_time:
        # Generate trips for this timestep
        new_vehicles = demand.trips_at(time)
        for trip in new_vehicles:
            vehicle = Vehicle(
                origin=trip.origin,
                destination=trip.destination,
                departure_time=time,
                route=find_route(network, trip)
            )
            vehicles.append(vehicle)
        
        # Update vehicle positions
        for vehicle in vehicles:
            if vehicle.state != VehicleState.ARRIVED:
                vehicle.step(
                    network,
                    config.timestep,
                    other_vehicles=vehicles
                )
        
        # Update edge speeds based on congestion
        update_edge_speeds(network, vehicles)
        
        # Measure metrics
        update_metrics(metrics, vehicles, network)
        
        # Remove arrived vehicles
        vehicles = [v for v in vehicles if v.state != VehicleState.ARRIVED]
        
        time += config.timestep
    
    return metrics
```

## Performance Considerations

1. **Spatial Indexing**: Use PostGIS spatial indexes on edges/nodes
2. **Routing Cache**: Cache common routes to avoid repeated computation
3. **Vectorization**: Use NumPy for batch vehicle updates
4. **Database Queries**: Use connection pooling, prepared statements
5. **API Caching**: Cache network topology (rarely changes)
6. **Frontend**: Use clustering for thousands of objects on map

## Testing Strategy

```
Unit Tests (40%)
├── Domain models (network, agents, routing)
├── Metrics calculations
├── Configuration validation
└── Car-following physics

Integration Tests (40%)
├── API endpoints
├── Database operations
├── Scenario execution
└── Results storage

Simulation Tests (15%)
├── Determinism (same seed = same result)
├── Conservation (no vehicles lost)
├── Physics plausibility
└── Known scenarios

E2E Tests (5%)
├── Full workflow (create scenario → run → view results)
└── UI interactions
```

## Extensibility Points

### Adding a New Transport Mode

1. Create `simulation/modes/transit_mode.py`
2. Define TransitMode domain model
3. Update routing to support mode
4. Update mode choice model
5. Add tests
6. Update API schema
7. Update UI

### Adding a New Scenario Intervention

1. Define intervention in `simulation/scenarios/`
2. Implement network mutation logic
3. Add tests
4. Update API endpoint
5. Update UI scenario editor

### Replacing the Car-Following Model

1. Create new model class inheriting from `CarFollowingModel`
2. Implement `acceleration(vehicle, lead_vehicle, timestep)` method
3. Add tests with known scenarios
4. Update configuration to select model
5. Update documentation

## Monitoring & Logging

Structured logging throughout:

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Starting simulation", extra={
    "simulation_id": sim_id,
    "network_nodes": network.num_nodes(),
    "timestep": config.timestep
})

logger.warning("Vehicle removed (invalid state)", extra={
    "vehicle_id": v.id,
    "state": v.state
})
```

Metrics exported to:
- stdout (development)
- PostgreSQL (production)
- Files (archival)

## Security Considerations

- API authentication (future: JWT tokens)
- Rate limiting on simulation runs
- Input validation on all endpoints
- No hardcoded credentials (use .env)
- Database queries use parameterized statements (SQLAlchemy)
- CORS configured appropriately

## Future Evolution

The architecture supports:

- **Distributed Simulation**: Simulation could scale to multiple workers
- **Real-time Traffic Data**: Integration with live traffic feeds
- **ML-based Mode Choice**: Replace heuristic with trained model
- **Rust/C++ Simulation Core**: Drop-in replacement if performance critical
- **Mobile App**: Consume same API from mobile client

---

For detailed subsystem documentation, see:
- [docs/simulation.md](simulation.md) - Simulation model details
- [docs/traffic_model.md](traffic_model.md) - Car-following and physics
- [docs/routing.md](routing.md) - Routing algorithms
- [docs/demand_model.md](demand_model.md) - Trip generation
