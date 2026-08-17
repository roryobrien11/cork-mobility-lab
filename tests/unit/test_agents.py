"""
Unit tests for vehicle agents with routing.
"""

import pytest
from simulation.agents import Vehicle, VehicleState
from simulation.routing import Route


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
    
    def test_vehicle_without_route(self):
        """Test vehicle without route."""
        vehicle = Vehicle.create(
            origin_node_id="node_1",
            destination_node_id="node_2"
        )
        
        assert not vehicle.has_route()
        assert vehicle.get_next_node() is None
        assert vehicle.get_next_edge() is None
        assert vehicle.route_progress_percent() == 0.0
    
    def test_vehicle_set_route(self):
        """Test setting route for vehicle."""
        vehicle = Vehicle.create(
            origin_node_id="node_1",
            destination_node_id="node_3"
        )
        
        # Create mock route
        route = Route(
            route_id="r1",
            origin_id="node_1",
            destination_id="node_3",
            node_sequence=["node_1", "node_2", "node_3"],
            edge_sequence=["edge_1", "edge_2"],
            total_distance_m=1000.0,
            total_travel_time_s=60.0
        )
        
        vehicle.set_route(route)
        
        assert vehicle.has_route()
        assert vehicle.planned_route == route
        assert vehicle.route == ["edge_1", "edge_2"]
        assert vehicle.node_sequence == ["node_1", "node_2", "node_3"]
    
    def test_vehicle_get_next_node(self):
        """Test getting next node in route."""
        vehicle = Vehicle.create(
            origin_node_id="node_1",
            destination_node_id="node_3"
        )
        
        route = Route(
            route_id="r1",
            origin_id="node_1",
            destination_id="node_3",
            node_sequence=["node_1", "node_2", "node_3"],
            edge_sequence=["edge_1", "edge_2"],
            total_distance_m=1000.0,
            total_travel_time_s=60.0
        )
        
        vehicle.set_route(route)
        
        assert vehicle.get_next_node() == "node_2"
    
    def test_vehicle_get_next_edge(self):
        """Test getting next edge in route."""
        vehicle = Vehicle.create(
            origin_node_id="node_1",
            destination_node_id="node_3"
        )
        
        route = Route(
            route_id="r1",
            origin_id="node_1",
            destination_id="node_3",
            node_sequence=["node_1", "node_2", "node_3"],
            edge_sequence=["edge_1", "edge_2"],
            total_distance_m=1000.0,
            total_travel_time_s=60.0
        )
        
        vehicle.set_route(route)
        
        assert vehicle.get_next_edge() == "edge_1"
    
    def test_vehicle_advance_node(self):
        """Test advancing along route."""
        vehicle = Vehicle.create(
            origin_node_id="node_1",
            destination_node_id="node_3"
        )
        
        route = Route(
            route_id="r1",
            origin_id="node_1",
            destination_id="node_3",
            node_sequence=["node_1", "node_2", "node_3"],
            edge_sequence=["edge_1", "edge_2"],
            total_distance_m=1000.0,
            total_travel_time_s=60.0
        )
        
        vehicle.set_route(route)
        
        # Advance through route
        assert vehicle.current_node_idx == 0
        assert vehicle.advance_node()
        assert vehicle.current_node_idx == 1
        assert vehicle.advance_node()
        assert vehicle.current_node_idx == 2
        assert not vehicle.advance_node()  # Can't advance past end
    
    def test_vehicle_route_progress(self):
        """Test route progress calculation."""
        vehicle = Vehicle.create(
            origin_node_id="node_1",
            destination_node_id="node_3"
        )
        
        route = Route(
            route_id="r1",
            origin_id="node_1",
            destination_id="node_3",
            node_sequence=["node_1", "node_2", "node_3"],
            edge_sequence=["edge_1", "edge_2"],
            total_distance_m=1000.0,
            total_travel_time_s=60.0
        )
        
        vehicle.set_route(route)
        
        assert vehicle.route_progress_percent() == 0.0
        vehicle.advance_node()
        assert vehicle.route_progress_percent() == 50.0
        vehicle.advance_node()
        assert vehicle.route_progress_percent() == 100.0
    
    def test_vehicle_set_route_none(self):
        """Test setting None route stops vehicle."""
        vehicle = Vehicle.create(
            origin_node_id="node_1",
            destination_node_id="node_3"
        )
        
        vehicle.set_route(None)
        
        assert vehicle.state == VehicleState.STOPPED
        assert not vehicle.has_route()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
