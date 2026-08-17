"""
Core simulation engine.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import random

from simulation.agents import Vehicle, VehicleState, IDMParameters, DEFAULT_IDM_PARAMETERS, idm_acceleration
from simulation.network import Network
from simulation.routing import Router


@dataclass
class SimulationConfig:
    """Configuration for a simulation run."""

    name: str
    description: str = ""
    start_time: int = 0  # seconds from midnight
    end_time: int = 3600  # seconds from midnight
    timestep: float = 1.0  # seconds
    random_seed: int = 42
    network_id: str = ""
    scenario_id: str = ""

    def validate(self) -> None:
        """Validate configuration."""
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be greater than start_time")
        if self.timestep <= 0:
            raise ValueError("timestep must be positive")


@dataclass
class SimulationState:
    """State of a running simulation."""

    current_time: int = 0
    current_step: int = 0
    total_vehicles: int = 0
    vehicles_arrived: int = 0
    vehicles_active: int = 0
    metrics: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation."""
        return (
            f"SimulationState(time={self.current_time}s, "
            f"step={self.current_step}, active={self.vehicles_active})"
        )


class Simulation:
    """
    Main simulation engine.

    Orchestrates network, routing, vehicle agents (via the Intelligent
    Driver Model), and metrics.

    Junction and traffic-signal interaction is not yet implemented (see
    simulation.signals) — vehicles currently drive edge-by-edge in
    isolation from cross-traffic at junctions, with car-following only
    against a leader on the same edge. This is a deliberate, documented
    scope limit for this phase, not a bug.
    """

    def __init__(
        self,
        config: SimulationConfig,
        network: Optional[Network] = None,
        vehicles: Optional[List[Vehicle]] = None,
        idm_params: IDMParameters = DEFAULT_IDM_PARAMETERS,
    ):
        """
        Initialize simulation.

        Args:
            config: Simulation configuration.
            network: Road network to simulate over. If omitted, run()
                performs a no-op time advancement only (useful for testing
                SimulationConfig/SimulationState in isolation).
            vehicles: Vehicles to simulate, each with an origin/destination
                and departure_time already set. Routes are computed
                automatically via Dijkstra at initialization.
            idm_params: Car-following model parameters.
        """
        self.config = config
        self.state = SimulationState()
        self.config.validate()

        self.network = network
        self.idm_params = idm_params
        self.vehicles: Dict[str, Vehicle] = {v.id: v for v in (vehicles or [])}

        if self.network is not None and self.vehicles:
            router = Router(self.network)
            for vehicle in self.vehicles.values():
                route = router.dijkstra(vehicle.origin_node_id, vehicle.destination_node_id)
                vehicle.set_route(route)

        self.state.total_vehicles = len(self.vehicles)

    def run(self) -> Dict[str, Any]:
        """
        Run simulation from config.start_time to config.end_time.

        Returns:
            Dictionary with simulation results and summary metrics.
        """
        random.seed(self.config.random_seed)

        if self.network is None or not self.vehicles:
            return self._run_time_advancement_only()

        print(f"Running simulation: {self.config.name}")
        print(f"Duration: {self.config.start_time} to {self.config.end_time} seconds")
        print(f"Timestep: {self.config.timestep} seconds")
        print(f"Vehicles: {len(self.vehicles)}")

        num_steps = int((self.config.end_time - self.config.start_time) / self.config.timestep)

        for step in range(num_steps):
            self.state.current_step = step + 1
            self.state.current_time = self.config.start_time + (step + 1) * self.config.timestep
            self._step(self.config.timestep)

        self.state.vehicles_active = sum(
            1 for v in self.vehicles.values() if v.state != VehicleState.ARRIVED
        )

        print(f"Simulation complete: {self.state.current_step} steps")
        print(f"Arrived: {self.state.vehicles_arrived}/{self.state.total_vehicles}")

        return {
            "name": self.config.name,
            "steps": self.state.current_step,
            "final_time": self.state.current_time,
            "status": "completed",
            "total_vehicles": self.state.total_vehicles,
            "vehicles_arrived": self.state.vehicles_arrived,
            "vehicles_active": self.state.vehicles_active,
            "metrics": self._compute_metrics(),
        }

    def _run_time_advancement_only(self) -> Dict[str, Any]:
        """Placeholder path used when there is no network/vehicles to simulate."""
        print(f"Running simulation: {self.config.name}")
        print(f"Duration: {self.config.start_time} to {self.config.end_time} seconds")
        print(f"Timestep: {self.config.timestep} seconds")

        num_steps = int((self.config.end_time - self.config.start_time) / self.config.timestep)

        for step in range(num_steps):
            self.state.current_step = step + 1
            self.state.current_time = self.config.start_time + (step + 1) * self.config.timestep

            if step % 100 == 0:
                print(f"  Step {step}/{num_steps}")

        print(f"Simulation complete: {self.state.current_step} steps")

        return {
            "name": self.config.name,
            "steps": self.state.current_step,
            "final_time": self.state.current_time,
            "status": "completed",
        }

    def _step(self, dt: float) -> None:
        """Advance all vehicles by one timestep using IDM car-following."""
        self._process_departures()

        edge_occupants: Dict[str, List[Vehicle]] = {}
        for vehicle in self.vehicles.values():
            if vehicle.state in (VehicleState.DRIVING, VehicleState.QUEUED) and vehicle.current_edge_id:
                edge_occupants.setdefault(vehicle.current_edge_id, []).append(vehicle)

        # Phase 1: compute accelerations from a consistent snapshot of
        # positions, so update order within an edge doesn't bias results.
        accelerations: Dict[str, float] = {}
        for edge_id, occupants in edge_occupants.items():
            edge = self.network.edges[edge_id]
            desired_speed_ms = edge.free_flow_speed_ms
            # Leader = vehicle furthest along the edge.
            occupants.sort(key=lambda v: v.position_on_edge, reverse=True)

            for i, vehicle in enumerate(occupants):
                if i == 0:
                    accelerations[vehicle.id] = idm_acceleration(
                        speed_ms=vehicle.speed_ms,
                        desired_speed_ms=desired_speed_ms,
                        params=self.idm_params,
                    )
                else:
                    leader = occupants[i - 1]
                    gap_m = (
                        (leader.position_on_edge - vehicle.position_on_edge) * edge.length_m
                        - self.idm_params.vehicle_length_m
                    )
                    accelerations[vehicle.id] = idm_acceleration(
                        speed_ms=vehicle.speed_ms,
                        desired_speed_ms=desired_speed_ms,
                        gap_m=gap_m,
                        leader_speed_ms=leader.speed_ms,
                        params=self.idm_params,
                    )

        # Phase 2: apply the updates.
        for vehicle in list(self.vehicles.values()):
            if vehicle.state not in (VehicleState.DRIVING, VehicleState.QUEUED) or not vehicle.current_edge_id:
                continue
            self._advance_vehicle(vehicle, accelerations[vehicle.id], dt)

    def _process_departures(self) -> None:
        """Move WAITING vehicles whose departure time has arrived onto their route."""
        for vehicle in self.vehicles.values():
            if vehicle.state != VehicleState.WAITING:
                continue
            if vehicle.departure_time > self.state.current_time:
                continue
            if not vehicle.has_route():
                # No route was found for this OD pair; it will never depart.
                vehicle.state = VehicleState.STOPPED
                continue

            first_edge = vehicle.get_next_edge()
            vehicle.current_edge_id = first_edge
            vehicle.position_on_edge = 0.0
            vehicle.speed_ms = 0.0
            vehicle.state = VehicleState.DRIVING

    def _advance_vehicle(self, vehicle: Vehicle, acceleration_ms2: float, dt: float) -> None:
        """Integrate one vehicle's speed/position for one timestep, handling edge transitions."""
        new_speed_ms = max(0.0, vehicle.speed_ms + acceleration_ms2 * dt)
        # Trapezoidal integration of distance from old and new speed.
        distance_m = max(0.0, (vehicle.speed_ms + new_speed_ms) / 2.0 * dt)

        edge = self.network.edges[vehicle.current_edge_id]
        vehicle.distance_traveled_m += distance_m
        vehicle.position_on_edge += distance_m / edge.length_m
        vehicle.speed_ms = new_speed_ms

        # Congested/stopped classification, per the state machine in
        # docs/simulation.md. Junction-level QUEUED/STOPPED handling (e.g.
        # red signals) is not modelled yet; this reflects car-following
        # congestion only.
        vehicle.state = VehicleState.QUEUED if new_speed_ms < 0.5 else VehicleState.DRIVING

        if vehicle.position_on_edge >= 1.0:
            overflow_m = (vehicle.position_on_edge - 1.0) * edge.length_m
            vehicle.advance_node()
            next_edge_id = vehicle.get_next_edge()

            if next_edge_id is None:
                # Reached the final node in the route.
                vehicle.state = VehicleState.ARRIVED
                vehicle.arrival_time = self.state.current_time
                vehicle.current_edge_id = None
                vehicle.position_on_edge = 1.0
                self.state.vehicles_arrived += 1
            else:
                next_edge = self.network.edges[next_edge_id]
                vehicle.current_edge_id = next_edge_id
                vehicle.position_on_edge = min(0.99, overflow_m / next_edge.length_m)

    def _compute_metrics(self) -> Dict[str, Any]:
        """Compute summary metrics over vehicles that have arrived."""
        arrived = [v for v in self.vehicles.values() if v.state == VehicleState.ARRIVED]

        if not arrived:
            return {
                "average_journey_time_s": 0.0,
                "median_journey_time_s": 0.0,
                "total_vehicle_hours": 0.0,
                "total_distance_km": 0.0,
                "average_speed_kmh": 0.0,
            }

        journey_times = sorted(v.journey_time() for v in arrived)
        total_distance_m = sum(v.distance_traveled_m for v in arrived)
        total_time_s = sum(journey_times)
        n = len(journey_times)
        mid = n // 2
        median = journey_times[mid] if n % 2 == 1 else (journey_times[mid - 1] + journey_times[mid]) / 2.0

        return {
            "average_journey_time_s": total_time_s / n,
            "median_journey_time_s": median,
            "total_vehicle_hours": total_time_s / 3600.0,
            "total_distance_km": total_distance_m / 1000.0,
            "average_speed_kmh": (total_distance_m / total_time_s) * 3.6 if total_time_s > 0 else 0.0,
        }
