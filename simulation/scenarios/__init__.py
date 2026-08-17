"""
Scenario management.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Scenario:
    """
    Simulation scenario.
    
    A scenario defines interventions applied to the baseline network/demand.
    """
    
    name: str
    description: str = ""
    base_network_id: str = ""
    base_demand_id: str = ""
    interventions: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_intervention(self, intervention: Dict[str, Any]) -> None:
        """Add intervention to scenario."""
        self.interventions.append(intervention)
