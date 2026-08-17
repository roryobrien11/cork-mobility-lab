"""
Simulation metrics and key performance indicators.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class Metrics:
    """Traffic simulation metrics."""
    
    total_vehicles: int = 0
    vehicles_arrived: int = 0
    vehicles_active: int = 0
    
    total_journey_time_s: float = 0.0
    total_distance_m: float = 0.0
    total_vehicle_hours: float = 0.0
    
    average_journey_time_s: float = 0.0
    median_journey_time_s: float = 0.0
    average_speed_ms: float = 0.0
    
    # Congestion metrics
    max_queue_length: int = 0
    total_delay_s: float = 0.0
    
    # Network metrics
    network_utilisation: float = 0.0  # 0 to 1
    average_congestion: float = 0.0  # 0 to 1
    
    # Emissions (placeholder)
    total_co2_kg: float = 0.0
    
    custom_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_vehicles": self.total_vehicles,
            "vehicles_arrived": self.vehicles_arrived,
            "vehicles_active": self.vehicles_active,
            "average_journey_time_s": self.average_journey_time_s,
            "median_journey_time_s": self.median_journey_time_s,
            "average_speed_ms": self.average_speed_ms,
            "total_vehicle_hours": self.total_vehicle_hours,
            "total_distance_m": self.total_distance_m,
            "network_utilisation": self.network_utilisation,
            "average_congestion": self.average_congestion,
            "total_co2_kg": self.total_co2_kg,
            **self.custom_metrics
        }
