# Simulation Model Documentation

## Overview

Cork Mobility Lab uses a **discrete-time, agent-based simulation** to model traffic flow in Cork.

Each simulation step represents a fixed time interval (default 1 second). At each timestep:

1. Demand generates new vehicles
2. Vehicles update their positions
3. Road conditions (speeds, queues) are updated
4. Metrics are measured

## Simulation Engine

### Configuration

```python
@dataclass
class SimulationConfig:
    name: str                          # Scenario name
    start_time: int = 0                # Simulation start (seconds from midnight)
    end_time: int = 3600               # Simulation end
    timestep: float = 1.0              # Timestep duration (seconds)
    random_seed: int = 42              # RNG seed for reproducibility
    network_id: str                    # Which network to simulate
    scenario_id: str                   # Which scenario (interventions)
```

### Determinism

**Key principle**: Simulations are deterministic.

Given the same `config` and `random_seed`, running the simulation twice produces identical results.

This is achieved by:
- Seeding NumPy and Python's `random` module
- Using only deterministic algorithms (no floating-point nondeterminism)
- Storing all stochastic decisions (e.g., route choices)

### Time Representation

Time is represented as **seconds from midnight** (0–86400).

Example:
- 07:00 AM = 25200 seconds
- 17:30 PM = 63000 seconds

## Vehicle Agents

### State Machine

```
WAITING
  │
  ├──→ DRIVING (on road segment)
  │      │
  │      ├──→ QUEUED (slow moving, vehicles ahead)
  │      │
  │      └──→ STOPPED (at traffic signal)
  │
  └──→ ARRIVED (reached destination)
```

### Vehicle Model

```python
@dataclass
class Vehicle:
    id: str                              # Unique ID
    origin_node_id: str                  # Origin node
    destination_node_id: str             # Destination node
    vehicle_type: str = "car"            # car, bus, truck, etc.
    departure_time: float = 0.0          # Departure time (seconds)
    current_edge_id: Optional[str] = None
    position_on_edge: float = 0.0        # 0 = start, 1 = end
    speed_ms: float = 0.0                # Current speed (m/s)
    state: VehicleState = WAITING
    route: List[str] = []                # Planned route (edge IDs)
    arrival_time: Optional[float] = None
```

## Car-Following Model

### Intelligent Driver Model (IDM)

Cork Mobility Lab uses the **Intelligent Driver Model** for realistic vehicle dynamics.

The IDM is a physics-based model with the following parameters:

| Parameter | Symbol | Default | Unit | Meaning |
|-----------|--------|---------|------|---------|
| Desired velocity | $v_0$ | 40 | km/h | Free-flow speed |
| Max acceleration | $a$ | 1.5 | m/s² | Maximum acceleration |
| Comfort deceleration | $b$ | 2.0 | m/s² | Comfortable braking |
| Min time headway | $T$ | 1.6 | s | Time to next vehicle |
| Min gap | $s_0$ | 2 | m | Bumper-to-bumper distance |
| Acceleration exponent | $\delta$ | 4 | - | Shape parameter |

### Equations

At each timestep, acceleration is calculated as:

$$a = a \left[ 1 - \left(\frac{v}{v_0}\right)^\delta - \left(\frac{s^*}{s}\right)^2 \right]$$

Where:

$$s^* = s_0 + v \cdot T + \frac{v \cdot \Delta v}{2 \sqrt{a \cdot b}}$$

- $v$ = current speed
- $\Delta v$ = speed difference to leader
- $s$ = spacing to leader

### Behavior

- **Free flow** ($\Delta v = 0$, large $s$): Accelerates toward $v_0$
- **Approaching leader**: Decelerates smoothly
- **Stopped by leader**: Maintains safe gap

## Road Network

### Graph Structure

The network is a **directed graph**:

- **Nodes** = intersections, junctions
- **Edges** = road segments

### Edge Attributes

```python
@dataclass
class Edge:
    id: str
    source_id: str                      # Start node
    target_id: str                      # End node
    length_m: float                     # Length (metres)
    speed_limit_kmh: float              # Posted speed limit
    lanes: int                          # Number of lanes
    road_type: RoadType                 # motorway, trunk, primary, ...
    capacity_vehicles_per_hour: float   # Per lane, per hour
    free_flow_speed_ms: float           # = speed_limit_kmh / 3.6
    current_vehicle_count: int          # For simulation
    current_avg_speed_ms: float         # Congestion-dependent speed
```

### Speed Dynamics

Road speed is affected by congestion (simplified):

$$v_{actual} = v_{free} \cdot (1 - \text{congestion\_level}^2)$$

Where:

$$\text{congestion\_level} = \frac{\text{current vehicles}}{\text{capacity per timestep}}$$

This models the phenomena:
- Free flow at low density
- Gradual slowdown as traffic builds
- Severe congestion at high density

## Routing

### Shortest Path

Routing uses either:

1. **Dijkstra's algorithm** (baseline, exact)
2. **A*** (faster, heuristic-based)

Both find the **shortest travel time** path, accounting for:
- Distance
- Speed limits
- Current congestion (optional)

Route is computed at trip generation and followed deterministically.

### Future Extensions

- **Dynamic routing**: Recompute route if severe congestion ahead
- **Stochastic routing**: Different drivers take different routes
- **Multi-modal routing**: Support buses, walking, cycling

## Demand Generation

### Trip Model

A **trip** specifies:

```python
@dataclass
class Trip:
    origin_node: str
    destination_node: str
    departure_time: float  # seconds
    mode: str              # car, bus, walk, cycle, rail
    vehicle_type: str      # car, truck, etc. (if mode='car')
```

### Demand Generator

Demand is generated from **zones** (geographical areas representing origins/destinations).

Each zone has:
- Polygon (boundary)
- Population
- Employment
- Generation rate (trips per person per hour)
- Attraction rate (jobs per person)

At each timestep, demand generator:

1. Computes trips generated from each zone
2. Selects random origin/destination pair
3. Samples departure time
4. Creates Vehicle and assigns route

### Time-of-Day Profiles

Demand varies by time of day:

```python
demand_profile = {
    "06:00-07:00": 0.3,   # 30% of peak
    "07:00-08:00": 0.9,   # 90% of peak
    "08:00-09:00": 1.0,   # 100% (peak)
    "09:00-10:00": 0.8,
    ...
}
```

## Traffic Signals

### Signal Timing

A signal is defined by:

```python
@dataclass
class SignalPlan:
    cycle_length: int         # Total cycle (seconds)
    phases: List[Phase]       # List of phases
    offset: int               # Offset relative to others (seconds)

@dataclass
class Phase:
    green_duration: int       # How long green
    amber_duration: int       # How long amber
    allowed_movements: Set[str]  # Which turns are allowed
```

Example (two-phase signal):

```
Phase 1 (0-25s):  North-South green
Phase 2 (25-50s): East-West green
Cycle = 50s
```

### Vehicle Interaction

When a vehicle reaches a signalised junction:

1. Check signal state
2. If green for its movement: proceed
3. If red: queue and wait
4. When signal turns green: accelerate and cross

## Metrics

### Measured

The simulation calculates:

| Metric | Unit | Meaning |
|--------|------|---------|
| Average journey time | seconds | Mean travel time for completed trips |
| Median journey time | seconds | 50th percentile |
| 95th percentile journey time | seconds | Worst-case (percentile) |
| Total vehicle-hours | hours | Sum of (travel time × vehicles) |
| Total vehicle-kilometres | km | Sum of distances traveled |
| Average speed | km/h | Global average speed |
| Max queue length | vehicles | Peak queue on any edge |
| Total delay | seconds | Extra time beyond free-flow time |
| Network utilisation | % | % of capacity used |
| Average congestion | ratio | Average congestion index |
| Modal split | % | % of trips by mode |
| CO₂ emissions | kg | Total carbon output |

### Calculation

After each timestep:

```python
def update_metrics(vehicles, network):
    for vehicle in vehicles:
        if vehicle.state == ARRIVED:
            metrics.total_vehicles += 1
            metrics.vehicles_arrived += 1
            metrics.total_journey_time += vehicle.journey_time()
            metrics.total_distance += vehicle.distance_traveled
            metrics.total_vehicle_hours += vehicle.journey_time() / 3600

    metrics.average_journey_time = (
        metrics.total_journey_time / metrics.vehicles_arrived
        if metrics.vehicles_arrived > 0 else 0
    )
    
    metrics.total_vehicle_hours = sum(
        v.speed_ms * timestep / 3600
        for v in vehicles
        if v.state != ARRIVED
    )
```

## Emissions Model

### CO₂ Calculation

Simplified HBEFA-inspired model:

$$\text{CO}_2 = \text{distance} \times \text{emission\_factor}(v)$$

Where emission factor depends on speed:

$$\text{EF}(v) = a + b \cdot v + c \cdot v^2$$

| Vehicle Type | Typical EF | Speed Range |
|--------------|-----------|-------------|
| Car (petrol) | 200 g/km | Free flow |
| Car (petrol) | 250 g/km | Congested |
| Car (diesel) | 180 g/km | Free flow |
| Bus | 80 g/km/passenger | Free flow |

### Caveats

- This is a **simplified model** for illustration
- Real emissions depend on many factors (engine, driving behavior, etc.)
- Not calibrated to Cork data
- Used for scenario comparison only

## Scenarios & Interventions

### Scenario Definition

A scenario is a set of **interventions** applied to the baseline.

```python
@dataclass
class Scenario:
    name: str                           # e.g., "Patrick St closure"
    description: str
    base_network_id: str                # Network config
    base_demand_id: str                 # Demand profile
    interventions: List[Intervention]
```

### Intervention Types

| Type | Effect | Example |
|------|--------|---------|
| `CloseRoad` | Remove edge(s) | Close Patrick Street |
| `ReduceCapacity` | Lower capacity | Narrow lanes |
| `IncreaseCapacity` | Higher capacity | Add lanes |
| `ChangeSpeedLimit` | Modify $v_0$ | 50→40 km/h |
| `ModifySignal` | Change timing | Increase EW green |
| `AddBusLane` | Restrict lanes to buses | Bus-only lane |
| `IncreaseDemand` | Increase trips | +20% traffic |
| `ModalShift` | Change mode split | +10% bus, -10% car |

### Applying Interventions

Before simulation:

```python
def apply_scenario(network, scenario):
    for intervention in scenario.interventions:
        network = intervention.apply(network)
    return network
```

## Calibration

### Process

1. **Collect data**: Traffic counts at locations/times
2. **Run baseline**: Simulate with assumed parameters
3. **Compare**: Check model vs. observed counts
4. **Adjust**: Tune demand, routing, car-following params
5. **Validate**: Test on held-out data

### Metrics

Error metrics (observed vs. simulated):

| Metric | Formula | Target |
|--------|---------|--------|
| MAE | $\frac{1}{n}\sum\|y - \hat{y}\|$ | < 10% |
| RMSE | $\sqrt{\frac{1}{n}\sum(y - \hat{y})^2}$ | < 12% |
| MAPE | $\frac{1}{n}\sum\frac{\|y - \hat{y}\|}{y}$ | < 15% |

## Reproducibility Checklist

For every simulation run:

- [ ] Random seed recorded
- [ ] Configuration file saved
- [ ] Network version recorded (OSM download date)
- [ ] Demand parameters saved
- [ ] Start/end time specified
- [ ] Timestep documented
- [ ] Results file timestamped
- [ ] Software version recorded

---

**Disclaimer**: This simulation is a model of traffic. It is not perfect. Results should be interpreted with caution and validated against real data before informing decisions.
