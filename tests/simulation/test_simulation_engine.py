"""
Integration tests for the Simulation engine: network + routing + IDM
car-following driving actual vehicle movement over time.
"""

import pytest

from simulation.core import Simulation, SimulationConfig
from simulation.network import Network, Node, Edge, JunctionType
from simulation.agents import Vehicle, VehicleState


@pytest.fixture
def line_network():
    """Two-edge line network A -> B -> C, 1000m per edge at 50 km/h."""
    network = Network.create("Line Network")
    a = Node.create(lat=51.80, lon=-8.50, junction_type=JunctionType.PRIORITY)
    b = Node.create(lat=51.81, lon=-8.50, junction_type=JunctionType.PRIORITY)
    c = Node.create(lat=51.82, lon=-8.50, junction_type=JunctionType.PRIORITY)
    for node in (a, b, c):
        network.add_node(node)
    network.add_edge(Edge.create(source_id=a.id, target_id=b.id, length_m=1000, speed_limit_kmh=50))
    network.add_edge(Edge.create(source_id=b.id, target_id=c.id, length_m=1000, speed_limit_kmh=50))
    return network, a, b, c


class TestSingleVehicle:
    def test_vehicle_arrives_at_destination(self, line_network):
        network, a, b, c = line_network
        vehicle = Vehicle.create(origin_node_id=a.id, destination_node_id=c.id, departure_time=0)
        config = SimulationConfig(name="single vehicle", start_time=0, end_time=300, timestep=1.0)

        sim = Simulation(config, network=network, vehicles=[vehicle])
        result = sim.run()

        assert vehicle.state == VehicleState.ARRIVED
        assert vehicle.arrival_time is not None
        assert vehicle.arrival_time > vehicle.departure_time
        assert result["vehicles_arrived"] == 1
        assert result["vehicles_active"] == 0

    def test_distance_traveled_matches_route_length(self, line_network):
        network, a, b, c = line_network
        vehicle = Vehicle.create(origin_node_id=a.id, destination_node_id=c.id, departure_time=0)
        config = SimulationConfig(name="distance check", start_time=0, end_time=300, timestep=1.0)

        Simulation(config, network=network, vehicles=[vehicle]).run()

        # Route is exactly two 1000m edges.
        assert vehicle.distance_traveled_m == pytest.approx(2000.0, rel=0.01)

    def test_never_exceeds_edge_free_flow_speed_by_much(self, line_network):
        """IDM should not let a vehicle blow past the desired speed uncontrolled."""
        network, a, b, c = line_network
        vehicle = Vehicle.create(origin_node_id=a.id, destination_node_id=c.id, departure_time=0)
        config = SimulationConfig(name="speed check", start_time=0, end_time=300, timestep=1.0)

        sim = Simulation(config, network=network, vehicles=[vehicle])

        max_speed_seen = 0.0
        # Run manually step by step to observe intermediate speed.
        sim.state.current_time = 0
        for _ in range(300):
            sim.state.current_step += 1
            sim.state.current_time += 1
            sim._step(1.0)
            max_speed_seen = max(max_speed_seen, vehicle.speed_ms)

        free_flow_ms = 50 / 3.6
        assert max_speed_seen <= free_flow_ms + 1e-6

    def test_departure_time_respected(self, line_network):
        """A vehicle should not start moving before its departure_time."""
        network, a, b, c = line_network
        vehicle = Vehicle.create(origin_node_id=a.id, destination_node_id=c.id, departure_time=100)
        config = SimulationConfig(name="late departure", start_time=0, end_time=50, timestep=1.0)

        Simulation(config, network=network, vehicles=[vehicle]).run()

        assert vehicle.state == VehicleState.WAITING
        assert vehicle.distance_traveled_m == 0.0

    def test_unreachable_destination_stops_vehicle(self, line_network):
        """A vehicle with no route (e.g. destination not in the network) never departs."""
        network, a, b, c = line_network
        vehicle = Vehicle.create(origin_node_id=a.id, destination_node_id="not-a-real-node", departure_time=0)
        config = SimulationConfig(name="no route", start_time=0, end_time=50, timestep=1.0)

        Simulation(config, network=network, vehicles=[vehicle]).run()

        assert vehicle.state == VehicleState.STOPPED
        assert vehicle.arrival_time is None


class TestCarFollowing:
    def test_follower_never_overtakes_leader(self, line_network):
        """Two vehicles on the same route, close together, must preserve their order."""
        network, a, b, c = line_network
        leader = Vehicle.create(origin_node_id=a.id, destination_node_id=c.id, departure_time=0)
        follower = Vehicle.create(origin_node_id=a.id, destination_node_id=c.id, departure_time=2)
        config = SimulationConfig(name="car following", start_time=0, end_time=300, timestep=1.0)

        sim = Simulation(config, network=network, vehicles=[leader, follower])
        for _ in range(300):
            sim.state.current_step += 1
            sim.state.current_time += 1
            sim._step(1.0)

            same_edge = (
                leader.current_edge_id is not None
                and leader.current_edge_id == follower.current_edge_id
            )
            if same_edge:
                assert follower.position_on_edge <= leader.position_on_edge

        assert leader.state == VehicleState.ARRIVED
        assert follower.state == VehicleState.ARRIVED
        assert follower.arrival_time >= leader.arrival_time

    def test_follower_arrival_not_faster_than_leader(self, line_network):
        """A trailing vehicle constrained by a leader can't complete the trip faster."""
        network, a, b, c = line_network
        leader = Vehicle.create(origin_node_id=a.id, destination_node_id=c.id, departure_time=0)
        follower = Vehicle.create(origin_node_id=a.id, destination_node_id=c.id, departure_time=0)
        config = SimulationConfig(name="same departure", start_time=0, end_time=300, timestep=1.0)

        Simulation(config, network=network, vehicles=[leader, follower]).run()

        assert leader.journey_time() <= follower.journey_time() + 1e-6


class TestConservationAndDeterminism:
    def test_vehicle_count_conserved(self, line_network):
        """At completion, every vehicle is accounted for as arrived, active, or stopped."""
        network, a, b, c = line_network
        vehicles = [
            Vehicle.create(origin_node_id=a.id, destination_node_id=c.id, departure_time=t)
            for t in (0, 5, 10, 200)
        ]
        config = SimulationConfig(name="conservation", start_time=0, end_time=300, timestep=1.0)

        result = Simulation(config, network=network, vehicles=vehicles).run()

        accounted_for = result["vehicles_arrived"] + result["vehicles_active"]
        assert accounted_for == len(vehicles)

    def test_deterministic_with_same_seed(self, line_network):
        """Running the same scenario twice must yield identical results."""
        network, a, b, c = line_network

        def make_vehicles():
            return [
                Vehicle.create(origin_node_id=a.id, destination_node_id=c.id, departure_time=t)
                for t in (0, 3, 7)
            ]

        config1 = SimulationConfig(name="det1", start_time=0, end_time=300, timestep=1.0, random_seed=7)
        config2 = SimulationConfig(name="det2", start_time=0, end_time=300, timestep=1.0, random_seed=7)

        result1 = Simulation(config1, network=network, vehicles=make_vehicles()).run()
        result2 = Simulation(config2, network=network, vehicles=make_vehicles()).run()

        assert result1["metrics"] == result2["metrics"]
        assert result1["vehicles_arrived"] == result2["vehicles_arrived"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
