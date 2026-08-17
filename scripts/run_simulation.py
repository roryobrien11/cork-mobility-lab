"""
Cork Mobility Lab CLI utilities.
"""

import sys
from simulation.core import Simulation, SimulationConfig

def run_test_simulation():
    """Run a test simulation."""
    print("🚗 Cork Mobility Lab - Test Simulation")
    print("=" * 50)
    
    config = SimulationConfig(
        name="Baseline Test",
        description="Quick test of simulation engine",
        start_time=0,
        end_time=60,
        timestep=1.0,
        random_seed=42
    )
    
    sim = Simulation(config)
    result = sim.run()
    
    print()
    print("📊 Results:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    print()
    print("✅ Test simulation complete!")

if __name__ == "__main__":
    run_test_simulation()
