import pandas as pd
from services.fault_analysis import distance_summary, compare_by_magnitude

def test_distance_summary():
    df = pd.DataFrame({"dist_to_fault_km": [1.0, 2.0, 3.0, 4.0]})
    s = distance_summary(df)
    assert s["count"] == 4
    assert abs(s["mean"] - 2.5) < 1e-9

def test_compare_by_magnitude():
    df = pd.DataFrame({
        "magnitude": [4.2, 4.8, 5.5, 6.1],
        "dist_to_fault_km": [10, 12, 3, 4],
    })
    out = compare_by_magnitude(df, threshold=5.0)
    assert set(out["group"]) == {"M<5.0", "M≥5.0"}