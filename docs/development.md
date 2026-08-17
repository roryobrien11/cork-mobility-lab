# Development Setup & Contributing

## Local Development

### Prerequisites

- Python 3.10 or later
- Node.js 18 or later
- Git
- Docker (optional, for database)

### Initial Setup

1. **Clone repository and enter directory:**
   ```bash
   git clone <repo-url>
   cd cork-mobility-lab
   ```

2. **Create Python virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install Node dependencies:**
   ```bash
   npm install
   ```

5. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

### Running Services

#### Option A: Docker Compose (recommended)

```bash
docker-compose up -d
```

This starts:
- PostgreSQL with PostGIS on localhost:5432
- FastAPI backend on localhost:8000
- React frontend on localhost:5173

#### Option B: Manual

1. **PostgreSQL** (install locally or via Docker):
   ```bash
   docker run -d \
     -e POSTGRES_USER=cork_user \
     -e POSTGRES_PASSWORD=cork_password \
     -e POSTGRES_DB=cork_mobility \
     -p 5432:5432 \
     postgis/postgis:15-3.3
   ```

2. **Backend** (in project root):
   ```bash
   uvicorn apps.api.main:app --reload
   ```

3. **Frontend** (in apps/web/):
   ```bash
   npm run dev
   ```

### Accessing Services

- **Frontend**: http://localhost:5173
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger)
- **Database**: localhost:5432 (psql client)

## Code Style & Quality

### Python

**Format with Black:**
```bash
black simulation/ apps/api/ tests/
```

**Sort imports:**
```bash
isort simulation/ apps/api/ tests/
```

**Lint:**
```bash
flake8 simulation/ apps/api/ tests/
ruff check simulation/ apps/api/ tests/
```

**Type check:**
```bash
mypy simulation/ apps/api/
```

**All in one:**
```bash
bash scripts/lint.sh
```

### TypeScript/React

**Format:**
```bash
npm run lint -w apps/web
```

**Type check:**
```bash
npm run type-check -w apps/web
```

## Testing

### Run All Tests

```bash
# Python tests
pytest tests/ -v --cov=simulation --cov=apps.api

# Frontend tests
npm test -w apps/web

# Type checking
mypy simulation/ apps/api/
```

### Test Organization

```
tests/
├── unit/                    # Fast, isolated tests
│   ├── test_network.py      # Network model tests
│   ├── test_agents.py       # Vehicle agent tests
│   ├── test_simulation.py   # Simulation engine tests
│   └── test_metrics.py      # Metrics calculation tests
│
├── integration/             # API + database tests
│   ├── test_api_network.py
│   ├── test_api_simulation.py
│   └── test_database.py
│
└── simulation/              # Detailed simulation behavior
    ├── test_car_following.py
    ├── test_routing.py
    └── test_determinism.py
```

### Writing Tests

Example unit test:

```python
# tests/unit/test_network.py

import pytest
from simulation.network import Network, Node, Edge

def test_network_creation():
    """Test creating a network."""
    network = Network.create("Test Network")
    assert network.name == "Test Network"
    assert network.num_nodes() == 0
    assert network.num_edges() == 0

def test_add_edge_validates_nodes(sample_network):
    """Test adding edge with missing node."""
    node_x = Node.create(lat=52.0, lon=-8.5)
    node_y = Node.create(lat=52.1, lon=-8.5)
    
    # node_y is not in network
    network.add_node(node_x)
    
    edge = Edge.create(node_x.id, node_y.id, 1000, 50)
    
    with pytest.raises(ValueError):
        network.add_edge(edge)
```

Example API integration test:

```python
# tests/integration/test_api.py

from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_network():
    response = client.get("/api/network")
    assert response.status_code == 200
```

## Git Workflow

### Commit Messages

Follow conventional commits:

```
feat(network): add node type validation
fix(routing): handle unreachable destination
docs(simulation): update car-following equations
test(agents): add vehicle state transition tests
```

### Branch Naming

```
feature/road-network-models
feature/routing-algorithm
feature/map-visualization
fix/edge-case-handling
docs/calibration-guide
```

### Pull Request Process

1. Create feature branch
2. Make changes
3. Write/update tests
4. Run linting and tests locally
5. Push to GitHub
6. Create PR with description
7. Address review comments
8. Merge when approved

## Project Layout

### Source Code

```
simulation/              # Core simulation (Python)
├── __init__.py
├── core/               # Main simulation engine
│   ├── __init__.py    # Simulation, SimulationConfig
│   └── ...
├── network/           # Road network
│   ├── __init__.py    # Network, Node, Edge models
│   └── ...
├── agents/            # Vehicle agents
├── routing/           # Routing algorithms
├── demand/            # Trip generation
├── signals/           # Traffic signals
├── metrics/           # KPI calculation
└── scenarios/         # Scenario management

apps/api/              # Backend (Python FastAPI)
├── main.py           # Entry point
├── models/           # Database models
├── schemas/          # Pydantic schemas
├── routes/           # API endpoints
└── database/         # Database config

apps/web/              # Frontend (React/TypeScript)
├── src/
│   ├── components/   # React components
│   ├── pages/        # Pages
│   ├── services/     # API calls
│   ├── App.tsx
│   └── main.tsx
├── vite.config.ts
└── tsconfig.json
```

### Configuration Files

```
pyproject.toml         # Python project config
package.json           # Node root workspace
docker-compose.yml     # Docker services
.env.example          # Environment template
.gitignore            # Git ignore rules
```

### Tests

```
tests/
├── conftest.py        # Pytest fixtures
├── unit/              # Fast unit tests
├── integration/       # API + DB tests
└── simulation/        # Simulation tests
```

### Documentation

```
docs/
├── architecture.md    # System design
├── simulation.md      # Simulation model
├── traffic_model.md   # Physics models
├── routing.md         # Routing algorithms
├── demand_model.md    # Demand generation
├── calibration.md     # Calibration process
├── data_sources.md    # Data sources & licensing
└── development.md     # This file
```

## Adding a New Feature

### Example: Add Bus Mode Support

1. **Create domain model:**
   ```python
   # simulation/modes/bus.py
   @dataclass
   class BusRoute:
       id: str
       stops: List[str]
       schedule: Dict[float, BusVehicle]
   ```

2. **Add tests:**
   ```python
   # tests/unit/test_bus_mode.py
   def test_bus_route_creation():
       route = BusRoute.create(...)
       assert len(route.stops) > 0
   ```

3. **Implement logic:**
   - Update routing to support buses
   - Update mode choice model
   - Add bus vehicle class

4. **Update API:**
   - Add `/api/transit/routes` endpoint
   - Update simulation results schema

5. **Update UI:**
   - Add bus layer to map
   - Show bus delay metrics

6. **Update docs:**
   - Document bus model in `docs/`

7. **Add tests:**
   - Run `pytest tests/ -v`
   - Check coverage: `pytest tests/ --cov=simulation`

## Debugging

### Python Debugging

Use VS Code with Python extension:

1. Create `.vscode/launch.json`:
   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Python: Run Simulation",
         "type": "python",
         "request": "launch",
         "program": "${workspaceFolder}/scripts/run_simulation.py",
         "console": "integratedTerminal",
         "justMyCode": true
       }
     ]
   }
   ```

2. Set breakpoint and press F5

### API Debugging

1. FastAPI auto-docs: http://localhost:8000/docs
2. Check logs: `docker-compose logs api`
3. Database query tool: `psql -U cork_user -d cork_mobility -h localhost`

### Frontend Debugging

1. Open DevTools (F12 in browser)
2. React DevTools extension (Chrome/Firefox)
3. Network tab to see API calls

## Performance Profiling

### Python Simulation

```bash
# Profile with cProfile
python -m cProfile -o simulation.prof scripts/run_simulation.py

# Visualize
python -m pstats simulation.prof
# Then: sort cumulative
#       stats 20  # Top 20 functions
```

### Database Queries

Enable query logging in PostgreSQL:

```sql
ALTER DATABASE cork_mobility SET log_statement = 'all';
ALTER DATABASE cork_mobility SET log_duration = 'on';
```

Then check logs:
```bash
docker-compose logs postgres
```

## Troubleshooting

### Database Connection Error

```
psycopg2.OperationalError: could not connect to server
```

**Solution:**
- Ensure PostgreSQL is running: `docker ps | grep postgres`
- Check DATABASE_URL in .env
- Try connecting manually: `psql postgresql://cork_user:cork_password@localhost:5432/cork_mobility`

### Port Already in Use

```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process on port 8000
lsof -i :8000
# Kill it
kill -9 <PID>
```

### Python Import Errors

```
ModuleNotFoundError: No module named 'simulation'
```

**Solution:**
- Ensure you're in the project root
- Reinstall: `pip install -e .`

### Frontend Dependencies Issues

```bash
npm install --force
```

## Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **PostgreSQL/PostGIS**: https://postgis.net/
- **MapLibre**: https://maplibre.org/
- **pytest**: https://docs.pytest.org/

---

**Questions?** Open an issue on GitHub or contact the team.
