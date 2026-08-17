# Cork Mobility Lab - Quick Reference

## Project Summary

**Cork Mobility Lab** is a research-grade, agent-based traffic simulation platform for Cork, Ireland.

- **Type**: Full-stack traffic simulation + optimization platform
- **Tech Stack**: React/TypeScript (frontend), FastAPI (backend), Python (simulation), PostgreSQL + PostGIS (database)
- **Status**: Initial scaffolding complete, ready for Phase 2
- **Total Files**: 65+
- **Lines of Code**: ~2,500

## One-Time Setup

### 1. Install Prerequisites
- Python 3.10+ (https://www.python.org)
- Node.js 18+ (https://nodejs.org)
- Docker Desktop (https://docker.com)
- Git

### 2. Create Virtual Environment
```bash
cd cork-mobility-lab
python -m venv venv
.\venv\Scripts\Activate.ps1  # PowerShell
```

### 3. Install Dependencies
```bash
pip install -e ".[dev]"
npm install
```

## Daily Development

### Start Everything
```bash
# Terminal 1: Docker services
docker-compose up -d

# Terminal 2: Backend tests (optional)
pytest tests/ -v

# Terminal 3: Backend
uvicorn apps.api.main:app --reload

# Terminal 4: Frontend
cd apps/web && npm run dev
```

### Access Application
- Frontend: http://localhost:5173
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Database: localhost:5432 (cork_user / cork_password)

### Quick Commands

```bash
# Run all tests
pytest tests/ -v --cov=simulation

# Test specific module
pytest tests/unit/test_network.py -v

# Format and lint code
black simulation/ apps/api/ tests/
isort simulation/ apps/api/ tests/
mypy simulation/ apps/api/

# Run simulation from CLI
python scripts/run_simulation.py

# Initialize database
python scripts/init_db.py

# Docker commands
docker-compose up -d              # Start
docker-compose logs -f api        # View API logs
docker-compose logs -f postgres   # View DB logs
docker-compose down               # Stop all
```

## Project Structure at a Glance

```
cork-mobility-lab/
├── apps/
│   ├── web/                  # React/TypeScript frontend
│   └── api/                  # FastAPI backend
├── simulation/               # Python simulation engine
│   ├── core/                # Simulation class
│   ├── network/             # Graph models (Node, Edge)
│   ├── agents/              # Vehicle agents
│   ├── routing/             # Path algorithms
│   ├── demand/              # Trip generation
│   ├── metrics/             # Measurement
│   ├── signals/             # Traffic control
│   └── scenarios/           # What-if scenarios
├── tests/                    # Unit & integration tests
├── docs/                     # Architecture & guides
├── scripts/                  # Utilities (init_db, run)
├── data/                     # Datasets
├── docker-compose.yml        # Services config
├── pyproject.toml            # Python config
└── README.md                 # Full overview
```

## What's Implemented

✅ Domain Models
- Network (nodes, edges)
- Vehicles with state machine
- Simulation configuration
- Metrics structures

✅ Infrastructure
- FastAPI backend scaffold
- React frontend scaffold
- PostgreSQL + PostGIS setup
- Docker Compose
- Test framework (pytest)

✅ Documentation
- Architecture guide
- Simulation model docs
- Development guide

## What's Not Yet Implemented

These are **intentionally deferred**:

- ⏳ Cork OSM data ingestion
- ⏳ Routing algorithms (Dijkstra, A*)
- ⏳ Car-following physics (IDM model)
- ⏳ Traffic signal logic
- ⏳ Demand/trip generation
- ⏳ Multimodal transport (bus, walk, cycle)
- ⏳ Map visualization
- ⏳ Optimization algorithms
- ⏳ Calibration framework

These are **built incrementally** in phases 2-25.

## Key Principles

1. **Separation of Concerns**: Simulation engine is independent of web app
2. **Type Safety**: Pydantic + TypeScript strict mode
3. **Reproducibility**: Deterministic with fixed seeds
4. **Testing**: Comprehensive unit and integration tests
5. **Documentation**: Clear architecture and assumptions

## Architecture

```
┌─────────────────┐
│  React Browser  │
│  MapLibre UI    │
└────────┬────────┘
         │ REST/JSON
         ▼
┌─────────────────┐
│  FastAPI        │
│  Backend        │
└────────┬────────┘
         │
    ┌────┴─────┐
    ▼          ▼
PostgreSQL  Python Simulation
PostGIS     Engine
```

## Testing

**18 unit tests** covering:
- Network models (Node, Edge, Network)
- Vehicle agents
- Simulation configuration
- Metrics calculation

**Run tests:**
```bash
pytest tests/ -v
```

**Test results:** All tests designed to pass with current scaffolding.

## Code Quality

**Automatic formatting:**
```bash
black simulation/ apps/api/ tests/
isort simulation/ apps/api/ tests/
```

**Type checking:**
```bash
mypy simulation/ apps/api/
```

**Linting:**
```bash
flake8 simulation/ apps/api/
ruff check simulation/ apps/api/
```

**All in one:**
```bash
bash scripts/lint.sh
```

## Database

**Tables created by init_db.py:**
- networks
- network_nodes
- network_edges
- simulations
- simulation_results

**Connect to database:**
```bash
psql -h localhost -U cork_user -d cork_mobility
```

**View PostGIS:**
```sql
SELECT st_astext(geom) FROM network_nodes LIMIT 5;
```

## Deployment Ready

**Docker Compose includes:**
- PostgreSQL 15 + PostGIS 3.3
- FastAPI on port 8000
- React dev server on port 5173

**For production:**
- Build React: `npm run build -w apps/web`
- Use Nginx as reverse proxy
- Use production-grade server (Gunicorn)
- Configure CORS properly
- Use environment secrets

## File Locations

**Important Files:**
- `pyproject.toml` - Python dependencies
- `apps/web/package.json` - React dependencies
- `docker-compose.yml` - Docker services
- `simulation/core/__init__.py` - Simulation class
- `simulation/network/__init__.py` - Domain models
- `apps/api/main.py` - API endpoints
- `apps/web/src/App.tsx` - React app

**Documentation:**
- `README.md` - Full overview
- `docs/architecture.md` - System design
- `docs/simulation.md` - Simulation model
- `docs/development.md` - Dev guide
- `SETUP_COMPLETE.md` - Detailed setup (this file)

## Next Phase (Phase 2)

**Cork OSM Data Ingestion:**

1. Download OpenStreetMap data for Cork
2. Extract road network
3. Create network graph
4. Add tests with real Cork geometry
5. Validate network connectivity

**Commands:**
```bash
# After implementing Phase 2
python scripts/ingest/osm_download.py cork 51.9 -8.5
python scripts/ingest/process_network.py data/raw/cork.osm
pytest tests/simulation/test_cork_network.py
```

## Troubleshooting

### Python not found
- Install Python 3.10+ from https://python.org
- Add to PATH during installation

### Database won't connect
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Restart Docker Compose
docker-compose down
docker-compose up -d postgres
sleep 5
python scripts/init_db.py
```

### Port already in use
```bash
# Find process on port 8000
netstat -ano | findstr :8000
# Kill it
taskkill /PID <PID> /F
```

### Module import errors
```bash
# Reinstall in development mode
pip install -e . --force-reinstall
```

## Resources

- **API Docs**: http://localhost:8000/docs (when running)
- **React Docs**: https://react.dev
- **FastAPI**: https://fastapi.tiangolo.com
- **PostgreSQL**: https://postgresql.org
- **PostGIS**: https://postgis.net
- **MapLibre**: https://maplibre.org

## Key Contacts & Attribution

Cork Mobility Lab is a research project developed as a portfolio demonstration of:
- Agent-based simulation
- Graph algorithms
- GIS and spatial data
- Backend engineering
- Full-stack web development
- Software architecture

---

**Last Updated**: 2026-08-17  
**Version**: 0.1.0 (Initial Scaffolding)  
**Status**: Ready for Phase 2 (Cork OSM Ingestion)
