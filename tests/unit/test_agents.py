"""
Unit tests for vehicle agents.
"""

import pytest
from simulation.agents import Vehicle, VehicleState


class TestVehicle:
    """Test Vehicle agent."""
    
    def test_create_vehicle(self):
        """Test vehicle creation."""
        vehicle = Vehicle.create(
            origin_node_id="node_1",
            destination_node_id="node_2",
            departure_time=10.0
        )
        assert vehicle.origin_node_id == "node_1"
        assert vehicle.destination_node_id == "node_2"
        assert vehicle.departure_time == 10.0
        assert vehicle.state == VehicleState.WAITING
        assert vehicle.id is not None
    
    def test_vehicle_journey_time_not_arrived(self):
        """Test journey time for vehicle not arrived."""
        vehicle = Vehicle.create(
            origin_node_id="node_1",
            destination_node_id="node_2",
            departure_time=0.0
        )
        assert vehicle.journey_time() is None
    
    def test_vehicle_journey_time_arrived(self):
        """Test journey time for arrived vehicle."""
        vehicle = Vehicle.create(
            origin_node_id="node_1",
            destination_node_id="node_2",
            departure_time=0.0
        )
        vehicle.arrival_time = 100.0
        assert vehicle.journey_time() == 100.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
