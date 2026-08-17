"""
Unit tests for simulation core.
"""

import pytest
from simulation.core import Simulation, SimulationConfig, SimulationState


class TestSimulationConfig:
    """Test SimulationConfig."""
    
    def test_create_config(self):
        """Test config creation."""
        config = SimulationConfig(
            name="Test Sim",
            start_time=0,
            end_time=3600,
            timestep=1.0
        )
        assert config.name == "Test Sim"
        assert config.start_time == 0
        assert config.end_time == 3600
    
    def test_validate_config_valid(self):
        """Test valid config."""
        config = SimulationConfig(
            name="Test",
            start_time=0,
            end_time=3600,
            timestep=1.0
        )
        config.validate()  # Should not raise
    
    def test_validate_config_invalid_time(self):
        """Test invalid time range."""
        config = SimulationConfig(
            name="Test",
            start_time=3600,
            end_time=0,
            timestep=1.0
        )
        with pytest.raises(ValueError):
            config.validate()
    
    def test_validate_config_invalid_timestep(self):
        """Test invalid timestep."""
        config = SimulationConfig(
            name="Test",
            start_time=0,
            end_time=3600,
            timestep=-1.0
        )
        with pytest.raises(ValueError):
            config.validate()


class TestSimulation:
    """Test Simulation."""
    
    def test_create_simulation(self):
        """Test simulation creation."""
        config = SimulationConfig(
            name="Test Sim",
            start_time=0,
            end_time=100,
            timestep=1.0
        )
        sim = Simulation(config)
        assert sim.config.name == "Test Sim"
        assert sim.state.current_step == 0
    
    def test_run_simulation(self):
        """Test running simulation."""
        config = SimulationConfig(
            name="Test Sim",
            start_time=0,
            end_time=10,
            timestep=1.0
        )
        sim = Simulation(config)
        result = sim.run()
        
        assert result["status"] == "completed"
        assert result["name"] == "Test Sim"
        assert result["steps"] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
