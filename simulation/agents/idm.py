"""
Intelligent Driver Model (IDM) car-following model.

Pure, deterministic acceleration function used by the simulation engine to
update vehicle speed each timestep. See docs/simulation.md for the full
mathematical description and parameter table.
"""

from dataclasses import dataclass
from typing import Optional
import math


@dataclass(frozen=True)
class IDMParameters:
    """
    IDM tuning parameters. Defaults are typical illustrative values for
    urban car traffic, not values calibrated against observed Cork data.
    """

    max_acceleration_ms2: float = 1.5  # a
    comfortable_deceleration_ms2: float = 2.0  # b
    minimum_gap_m: float = 2.0  # s0
    time_headway_s: float = 1.6  # T
    acceleration_exponent: float = 4.0  # delta
    vehicle_length_m: float = 4.5


DEFAULT_IDM_PARAMETERS = IDMParameters()


def idm_acceleration(
    speed_ms: float,
    desired_speed_ms: float,
    gap_m: Optional[float] = None,
    leader_speed_ms: Optional[float] = None,
    params: IDMParameters = DEFAULT_IDM_PARAMETERS,
) -> float:
    """
    Compute IDM acceleration (m/s^2) for a vehicle.

    a = a_max * [1 - (v / v0)^delta - (s* / s)^2]

    where s* = s0 + v*T + (v * delta_v) / (2 * sqrt(a_max * b))

    Args:
        speed_ms: Current vehicle speed (m/s).
        desired_speed_ms: Free-flow / desired speed for this road (m/s).
        gap_m: Bumper-to-bumper gap to the leading vehicle (m), or None if
            there is no leader within range (free-road driving).
        leader_speed_ms: Speed of the leading vehicle (m/s), or None.
        params: IDM parameter set.

    Returns:
        Acceleration in m/s^2 (may be negative, i.e. braking).
    """
    if desired_speed_ms <= 0:
        # No sensible desired speed (e.g. a zero-length or misconfigured
        # edge): brake at the comfortable rate rather than divide by zero.
        return -params.comfortable_deceleration_ms2

    free_road_term = 1.0 - (speed_ms / desired_speed_ms) ** params.acceleration_exponent

    if gap_m is None or leader_speed_ms is None:
        interaction_term = 0.0
    else:
        delta_v = speed_ms - leader_speed_ms
        s_star = (
            params.minimum_gap_m
            + speed_ms * params.time_headway_s
            + (speed_ms * delta_v)
            / (2 * math.sqrt(params.max_acceleration_ms2 * params.comfortable_deceleration_ms2))
        )
        s_star = max(s_star, params.minimum_gap_m)
        # A near-zero or negative gap (e.g. from discretisation overlap)
        # would blow up (s*/s)^2; floor it to a small positive value so the
        # model produces strong-but-finite braking instead.
        safe_gap = max(gap_m, 0.1)
        interaction_term = (s_star / safe_gap) ** 2

    return params.max_acceleration_ms2 * (free_road_term - interaction_term)
