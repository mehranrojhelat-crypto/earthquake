# services/fault_analysis.py
import pandas as pd
import numpy as np

def distance_summary(df: pd.DataFrame) -> dict:
    s = df["dist_to_fault_km"].dropna()
    if s.empty:
        return {}
    return {
        "count": int(s.shape[0]),
        "mean": float(s.mean()),
        "median": float(s.median()),
        "p25": float(s.quantile(0.25)),
        "p75": float(s.quantile(0.75)),
        "min": float(s.min()),
        "max": float(s.max()),
    }

def compare_by_magnitude(
    df: pd.DataFrame,
    threshold: float = 5.0,
) -> pd.DataFrame:
    work = df.dropna(subset=["dist_to_fault_km", "magnitude"]).copy()
    work["group"] = np.where(work["magnitude"] >= threshold, f"M≥{threshold}", f"M<{threshold}")
    out = (
        work.groupby("group")["dist_to_fault_km"]
        .agg(["count", "mean", "median", "min", "max"])
        .round(2)
        .reset_index()
    )
    return out

def city_fault_proximity(df_with_dist: pd.DataFrame, cities: dict, radius_km: float = 150) -> pd.DataFrame:
    """میانگین فاصله تا گسل برای زلزله‌های اطراف هر شهر"""
    from utils.geo import filter_by_radius

    rows = []
    for name, meta in cities.items():
        subset = filter_by_radius(df_with_dist, meta["lat"], meta["lon"], radius_km)
        if subset.empty or subset["dist_to_fault_km"].dropna().empty:
            rows.append({
                "شهر": name,
                "تعداد زلزله": 0,
                "میانگین فاصله تا گسل (km)": np.nan,
                "میانه فاصله تا گسل (km)": np.nan,
                "میانگین بزرگی": np.nan,
            })
            continue

        rows.append({
            "شهر": name,
            "تعداد زلزله": int(len(subset)),
            "میانگین فاصله تا گسل (km)": round(float(subset["dist_to_fault_km"].mean()), 2),
            "میانه فاصله تا گسل (km)": round(float(subset["dist_to_fault_km"].median()), 2),
            "میانگین بزرگی": round(float(subset["magnitude"].mean()), 2),
        })
    return pd.DataFrame(rows).sort_values("میانگین فاصله تا گسل (km)")