# Cork Mobility Lab

## Overview

Cork Mobility Lab is a **research-grade, agent-based traffic simulation and optimisation platform** for Cork, Ireland.

This is **not a toy animation**. It is a technically rigorous platform designed to:

- **Ingest real Cork geographic and transport data** from OpenStreetMap, traffic counts, and transport datasets
- **Simulate vehicles and multimodal transport** with physics-based car-following models
- **Measure congestion, mobility, and emissions outcomes** with rigorous metrics
- **Run scenario analysis** (road closures, bus priority, demand shifts, signal optimisation)
- **Optimise interventions** using derivative-free algorithms

The platform demonstrates:

- Graph theory and algorithms (Dijkstra, A*, routing)
- Agent-based simulation with discrete timesteps
- Numerical modelling (car-following, queueing)
- GIS (PostGIS, spatial indexing, coordinate systems)
- Backend engineering (FastAPI, PostgreSQL)
- Data engineering (data ingestion, preprocessing, reproducible pipelines)
- Optimisation algorithms
- Scientific computing (NumPy, SciPy)
- Testing and validation
- Software architecture (domain-driven design, separation of concerns)
- Performance engineering

## Technology Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development
- **MapLibre GL** for interactive mapping
- **Tailwind CSS** for styling

### Backend
- **FastAPI** with async support
- **PostgreSQL 15** with PostGIS for spatial data
- **SQLAlchemy** for ORM
- **Pydantic** for data validation

### Simulation & Computation
- **Python 3.10+**
- **NumPy** and **SciPy** for numerical computing
- **NetworkX** for graph algorithms
- **GeoPandas** and **Shapely** for spatial operations
- **Pandas** for data manipulation

### Testing & Quality
- **pytest** with asyncio support
- **Vitest** for frontend tests
- **Playwright** for end-to-end tests
- **mypy** for type checking
- **Black**, **isort**, **ruff** for code quality

### Infrastructure
- **Docker** and **Docker Compose**
- **GitHub Actions** for CI/CD

## Project Structure

```
cork-mobility-lab/
├── apps/
│   ├── web/                      # React frontend
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   ├── services/
│   │   │   └── App.tsx
│   │   ├── vite.config.ts
│   │   ├── tsconfig.json
│   │   └── package.json
│   │
│   └── api/                      # FastAPI backend
│       ├── main.py
│       ├── models/
│       ├── schemas/
│       ├── routes/
│       └── database/
│
├── simulation/                   # Simulation engine (Python)
│   ├── core/                    # Main simulation loop
│   ├── network/                 # Road network models
│   ├── agents/                  # Vehicle agents
│   ├── routing/                 # Routing algorithms
│   ├── demand/                  # Trip generation
│   ├── signals/                 # Traffic signals
│   ├── metrics/                 # KPIs and measurement
│   └── scenarios/               # Scenario management
│
├── data/
│   ├── raw/                     # Downloaded OSM, traffic counts
│   ├── processed/               # Cleaned networks, demand matrices
│   └── sample/                  # Example datasets
│
├── scripts/
│   ├── ingest/                  # OSM download, network extraction
│   ├── preprocessing/           # Data cleaning, zone creation
│   └── experiments/             # Experiment runners
│
├── experiments/
│   ├── configs/                 # Scenario YAML configurations
│   └── results/                 # Output metrics, logs
│
├── tests/
│   ├── unit/                    # Domain model tests
│   ├── integration/             # API + database tests
│   └── simulation/              # Simulation behaviour tests
│
├── docs/
│   ├── architecture.md
│   ├── simulation.md
│   ├── traffic_model.md
│   ├── routing.md
│   ├── demand_model.md
│   ├── calibration.md
│   ├── data_sources.md
│   └── development.md
│
├── docker-compose.yml
├── pyproject.toml
├── package.json
├── .env.example
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker and Docker Compose
- Git

### Installation

1. **Clone and setup environment:**
   ```bash
   git clone <repo>
   cd cork-mobility-lab
   cp .env.example .env
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Install Node dependencies:**
   ```bash
   npm install
   ```

4. **Start services with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

   This starts:
   - PostgreSQL 15 with PostGIS on port 5432
   - FastAPI backend on port 8000
   - React frontend on port 5173

5. **Initialize database:**
   ```bash
   python scripts/init_db.py
   ```

6. **Run tests:**
   ```bash
   pytest tests/ -v
   npm test -w apps/web
   ```

7. **Access the application:**
   - Frontend: http://localhost:5173
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Architecture

### Conceptual Flow

```
┌─────────────────────────┐
│  React / MapLibre UI    │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│     FastAPI REST API    │
└────────────┬────────────┘
             │
    ┌────────┼────────┐
    │        │        │
    ▼        ▼        ▼
PostgreSQL   │    Simulation
PostGIS      │    Engine
             │
         Network
         Routing
         Agents
         Demand
         Metrics
```

### Key Principles

1. **Separation of Concerns**: Simulation logic is independent of the web application
2. **Determinism**: Same configuration + seed = same results
3. **Type Safety**: Strong typing throughout (Python + TypeScript)
4. **Testability**: Comprehensive unit and integration tests
5. **Reproducibility**: All experiments store configuration and random seeds
6. **Extensibility**: Modular design allows adding new components (e.g., new transport modes)
7. **Science-first**: Clear distinction between real data, synthetic data, and model assumptions

## Simulation Phases

The project is built incrementally:

### Phase 1: Road Network
- [x] Domain models for nodes and edges
- [x] Network graph structure
- [x] Basic tests
- [x] Cork OSM data ingestion (see [docs/data_sources.md](docs/data_sources.md))

### Phase 2: Routing (CURRENT)
- [x] Dijkstra's algorithm
- [x] A* with heuristics
- [x] Tests with known paths

### Phase 3: Vehicle Agents
- [x] Vehicle model with state machine
- [ ] Discrete-time simulation loop

### Phase 4: Car-Following Model
- [ ] Intelligent Driver Model (IDM)
- [ ] Physics validation

### Phase 5: Traffic Signals & Junctions
- [ ] Signal phase control
- [ ] Queue dynamics

### Phase 6: Demand Generation
- [ ] Trip generation from zones
- [ ] Origin-destination matrices

### Phase 7: Simulation Engine
- [ ] Main event loop
- [ ] Time advancement
- [ ] Vehicle lifecycle

### Phase 8: Metrics & Measurement
- [ ] Travel time, congestion, emissions
- [ ] Output to database

### Phase 9: Web API
- [ ] REST endpoints
- [ ] Network, simulation, scenario endpoints

### Phase 10: Map UI
- [ ] Interactive map with congestion visualization
- [ ] Real-time metrics display

### Phase 11: Scenario System
- [ ] Scenario definitions
- [ ] Interventions (road closures, signal changes, etc.)

### Phase 12: Multimodal Transport
- [ ] Bus routes and schedules
- [ ] Mode choice model
- [ ] Walk/cycle network

### Phase 13: Experiment Framework
- [ ] Scenario runner
- [ ] Results storage
- [ ] Comparison analysis

### Phase 14: Calibration & Validation
- [ ] Data comparison tools
- [ ] Calibration workflow

### Phase 15: Optimisation
- [ ] Signal optimisation
- [ ] Demand intervention search

## Development Standards

### Code Quality

- **Type hints** throughout Python code
- **Docstrings** for all public classes and functions
- **Unit tests** for domain logic (target: >80% coverage)
- **Integration tests** for API and database interactions
- **Black** for code formatting
- **isort** for import sorting
- **mypy** for type checking

### Documentation

- Every subsystem has a markdown file explaining the model
- Mathematical models are documented with equations and assumptions
- External data sources are clearly cited
- Configuration options are documented
- Limitations and future work are explicit

### Reproducibility

- All experiments use fixed random seeds
- Configuration is stored with results
- Data sources and versions are recorded
- Simulation is deterministic

## Testing

Run all tests:

```bash
# Python tests
pytest tests/ -v --cov=simulation

# Frontend tests
npm test -w apps/web

# Type checking
mypy simulation/ apps/api/
tsc --noEmit -p apps/web/
```

## Data Sources

Cork Mobility Lab ingests data from:

- **OpenStreetMap**: Road network (open licence)
- **Cork City Council**: Traffic counts (subject to data sharing agreement)
- **TII**: National traffic data (via standard channels)
- **NTA**: Public transport data (where available)
- **CSO**: Demographic data (public)

See [docs/data_sources.md](docs/data_sources.md) for detailed sources and licensing.

## Scientific Integrity

This platform clearly distinguishes:

- **REAL DATA**: Observed traffic counts, OSM network
- **SYNTHETIC DATA**: Generated demand, test scenarios
- **MODEL ASSUMPTIONS**: Car-following parameters, modal choice coefficients
- **SIMULATION OUTPUT**: Computed metrics from running the model

Claims about Cork's traffic are only made with proper calibration and validation.

Results are described as:

- "simulation estimate"
- "modelled scenario"
- "subject to model calibration"
- "illustrative intervention analysis"

## Performance Targets

- **Vehicles simulated per second**: > 10,000 (Python, single-threaded)
- **Simulation of 1 hour traffic**: < 5 seconds (on modern CPU)
- **API response time**: < 200ms (p95)
- **Frontend interaction**: 60 FPS (map interactions)

Profiling is performed before optimisation. Current focus is correctness, not speed.

## Contributing

See [docs/development.md](docs/development.md) for:

- Development setup
- Code style guide
- Commit conventions
- PR process
- Adding new features

## Limitations & Disclaimer

- **NOT a real-time traffic prediction tool**: Requires calibration and is subject to model error
- **Simplified physics**: Car-following is realistic but not vehicle-dynamics accurate
- **Synthetic demand**: Trip patterns are modelled; observed demand may differ
- **Local scope**: Model is for Cork; generalisation to other regions requires validation

## Future Work

- Calibration against real Cork traffic counts
- Transit assignment for buses and walking
- Real-time traffic data integration
- Signal optimisation algorithms
- Network resilience analysis
- Environmental impact assessment

## License

MIT (or as appropriate for your institution)

## Contact & Attribution

Cork Mobility Lab is a research project. For questions or collaboration, contact [your details].

---

**Status**: Real Cork road network ingested from OpenStreetMap (10,400 nodes,
22,801 edges, 2,511 km — see [docs/data_sources.md](docs/data_sources.md)).
Dijkstra and A* routing implemented and verified against the real network.
Vehicle agents have a state machine and route assignment. Next: the
discrete-time simulation loop and car-following model (Phase 4/5).
