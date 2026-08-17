"""
Core simulation engine.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
from datetime import datetime


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
    
    Orchestrates network, agents, demand, and metrics.
    """
    
    def __init__(self, config: SimulationConfig):
        """Initialize simulation."""
        self.config = config
        self.state = SimulationState()
        self.config.validate()
    
    def run(self) -> Dict[str, Any]:
        """
        Run simulation.
        
        Returns:
            Dictionary with simulation results
        """
        print(f"Running simulation: {self.config.name}")
        print(f"Duration: {self.config.start_time} to {self.config.end_time} seconds")
        print(f"Timestep: {self.config.timestep} seconds")
        
        # Placeholder simulation loop
        num_steps = int((self.config.end_time - self.config.start_time) / self.config.timestep)
        
        for step in range(num_steps):
            self.state.current_step = step
            self.state.current_time = self.config.start_time + step * self.config.timestep
            
            # Placeholder: simulate one timestep
            if step % 100 == 0:
                print(f"  Step {step}/{num_steps}")
        
        print(f"Simulation complete: {self.state.current_step} steps")
        
        return {
            "name": self.config.name,
            "steps": self.state.current_step,
            "final_time": self.state.current_time,
            "status": "completed"
        }
