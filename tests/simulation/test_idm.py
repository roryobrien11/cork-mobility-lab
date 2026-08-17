"""
Unit tests for the Intelligent Driver Model (IDM) car-following model.
"""

import pytest

from simulation.agents.idm import IDMParameters, idm_acceleration


class TestIDMFreeRoad:
    """Behaviour with no leader (free-road driving)."""

    def test_accelerates_from_standstill(self):
        """A stationary vehicle below its desired speed should accelerate at close to max."""
        params = IDMParameters()
        accel = idm_acceleration(speed_ms=0.0, desired_speed_ms=20.0, params=params)
        assert accel == pytest.approx(params.max_acceleration_ms2)

    def test_zero_acceleration_at_desired_speed(self):
        """At exactly the desired speed with no leader, acceleration should vanish."""
        accel = idm_acceleration(speed_ms=15.0, desired_speed_ms=15.0)
        assert accel == pytest.approx(0.0, abs=1e-9)

    def test_decelerates_above_desired_speed(self):
        """Above the desired speed (e.g. entering a lower speed-limit edge), it should brake."""
        accel = idm_acceleration(speed_ms=25.0, desired_speed_ms=15.0)
        assert accel < 0

    def test_approaches_desired_speed_monotonically(self):
        """Acceleration should shrink as speed approaches the desired speed."""
        a1 = idm_acceleration(speed_ms=5.0, desired_speed_ms=20.0)
        a2 = idm_acceleration(speed_ms=15.0, desired_speed_ms=20.0)
        assert a1 > a2 > 0

    def test_handles_zero_desired_speed_without_crashing(self):
        """A degenerate zero desired speed should brake, not divide by zero."""
        params = IDMParameters()
        accel = idm_acceleration(speed_ms=5.0, desired_speed_ms=0.0, params=params)
        assert accel == pytest.approx(-params.comfortable_deceleration_ms2)


class TestIDMCarFollowing:
    """Behaviour with a leading vehicle present."""

    def test_brakes_hard_when_close_to_slow_leader(self):
        """A small gap to a much slower/stopped leader should force strong braking."""
        accel = idm_acceleration(
            speed_ms=15.0,
            desired_speed_ms=20.0,
            gap_m=3.0,
            leader_speed_ms=0.0,
        )
        params = IDMParameters()
        assert accel < -params.comfortable_deceleration_ms2

    def test_large_gap_behaves_like_free_road(self):
        """A very large gap should have negligible effect on acceleration."""
        free_road = idm_acceleration(speed_ms=10.0, desired_speed_ms=20.0)
        with_distant_leader = idm_acceleration(
            speed_ms=10.0,
            desired_speed_ms=20.0,
            gap_m=100_000.0,
            leader_speed_ms=20.0,
        )
        assert with_distant_leader == pytest.approx(free_road, abs=1e-6)

    def test_zero_gap_does_not_raise(self):
        """A (physically invalid) zero or negative gap must not raise a ZeroDivisionError."""
        accel = idm_acceleration(speed_ms=10.0, desired_speed_ms=20.0, gap_m=0.0, leader_speed_ms=5.0)
        assert accel < 0

    def test_closing_speed_increases_braking(self):
        """Approaching a leader faster than it's moving should brake harder than matching its speed."""
        matching_speed = idm_acceleration(
            speed_ms=15.0, desired_speed_ms=20.0, gap_m=20.0, leader_speed_ms=15.0
        )
        closing_fast = idm_acceleration(
            speed_ms=15.0, desired_speed_ms=20.0, gap_m=20.0, leader_speed_ms=5.0
        )
        assert closing_fast < matching_speed

    def test_deterministic(self):
        """Same inputs must always produce the same output."""
        kwargs = dict(speed_ms=12.3, desired_speed_ms=18.0, gap_m=15.0, leader_speed_ms=10.0)
        assert idm_acceleration(**kwargs) == idm_acceleration(**kwargs)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
