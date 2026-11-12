import time
import numpy as np
import pandas as pd

from utils.geo import (
    haversine_km,
    filter_by_radius,
    compute_distance_to_nearest_fault,
)


def test_haversine_zero_distance():
    d = haversine_km(35.0, 51.0, 35.0, 51.0)
    assert np.isclose(d, 0.0, atol=1e-6)


def test_haversine_known_approx():
    d = haversine_km(35.6892, 51.3890, 35.8400, 50.9391)
    assert 30 < float(d) < 60


def test_filter_by_radius():
    df = pd.DataFrame({
        "latitude": [35.6892, 32.0],
        "longitude": [51.3890, 54.0],
        "magnitude": [4.5, 5.0],
    })
    out = filter_by_radius(df, 35.6892, 51.3890, 20)
    assert len(out) == 1
    assert "distance_km" in out.columns


def test_fault_distance_runs_fast_enough():
    faults = {
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "test"},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[51.0 + i * 0.01, 35.0] for i in range(500)],
                },
            }
        ]
    }
    df = pd.DataFrame({
        "latitude": [35.0 + i * 0.001 for i in range(1000)],
        "longitude": [51.0 + i * 0.001 for i in range(1000)],
        "magnitude": [4.5] * 1000,
    })

    t0 = time.time()
    out = compute_distance_to_nearest_fault(df, faults)
    elapsed = time.time() - t0

    assert "dist_to_fault_km" in out.columns
    assert out["dist_to_fault_km"].notna().all()
    assert elapsed < 2.0