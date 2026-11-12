# utils/geo.py
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree


def haversine_km(lat1, lon1, lat2, lon2):
    """فاصله تقریبی روی کره زمین (کیلومتر) — از عدد و آرایه پشتیبانی می‌کند"""
    R = 6371.0
    lat1 = np.radians(np.asarray(lat1, dtype=float))
    lon1 = np.radians(np.asarray(lon1, dtype=float))
    lat2 = np.radians(np.asarray(lat2, dtype=float))
    lon2 = np.radians(np.asarray(lon2, dtype=float))

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def filter_by_radius(df, center_lat, center_lon, radius_km):
    """زلزله‌های داخل شعاع مشخص از یک نقطه"""
    work = df.copy()
    dists = haversine_km(
        center_lat,
        center_lon,
        work["latitude"].values,
        work["longitude"].values,
    )
    work["distance_km"] = dists
    return work[work["distance_km"] <= radius_km].copy()


def _to_cartesian(lat_deg, lon_deg, radius_km: float = 6371.0):
    lat = np.radians(np.asarray(lat_deg, dtype=float))
    lon = np.radians(np.asarray(lon_deg, dtype=float))
    x = radius_km * np.cos(lat) * np.cos(lon)
    y = radius_km * np.cos(lat) * np.sin(lon)
    z = radius_km * np.sin(lat)
    return np.column_stack([x, y, z])


def extract_fault_points(faults: dict, max_points: int = 20000, step_div: int = 25):
    fault_lats, fault_lons, fault_names = [], [], []

    for feat in faults.get("features", []):
        geom = feat.get("geometry") or {}
        name = (feat.get("properties") or {}).get("name", "گسل")
        gtype = geom.get("type")
        coords = geom.get("coordinates", [])

        lines = []
        if gtype == "LineString":
            lines = [coords]
        elif gtype == "MultiLineString":
            lines = coords

        for line in lines:
            if not line:
                continue
            step = max(1, len(line) // step_div)
            for p in line[::step]:
                fault_lons.append(p[0])
                fault_lats.append(p[1])
                fault_names.append(name)

    if not fault_lats:
        return np.array([]), np.array([]), []

    return (
        np.array(fault_lats[:max_points]),
        np.array(fault_lons[:max_points]),
        fault_names[:max_points],
    )


def compute_distance_to_nearest_fault(
    df: pd.DataFrame,
    faults: dict,
    max_points: int = 20000,
) -> pd.DataFrame:
    """فاصله تقریبی هر زلزله تا نزدیک‌ترین نقطه گسل با KDTree"""
    out = df.copy()
    fault_lats, fault_lons, _ = extract_fault_points(faults, max_points=max_points)

    if len(fault_lats) == 0 or out.empty:
        out["dist_to_fault_km"] = np.nan
        return out

    fault_xyz = _to_cartesian(fault_lats, fault_lons)
    tree = cKDTree(fault_xyz)

    eq_xyz = _to_cartesian(out["latitude"].values, out["longitude"].values)
    dists, _ = tree.query(eq_xyz, k=1)

    out["dist_to_fault_km"] = dists.astype(float)
    return out