import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from config import IRAN_BBOX, DEFAULT_DAYS_BACK, DEFAULT_MIN_MAGNITUDE, USGS_LIMIT

def fetch_earthquakes(
    days_back: int = DEFAULT_DAYS_BACK,
    min_magnitude: float = DEFAULT_MIN_MAGNITUDE,
) -> tuple[pd.DataFrame, str, str]:
    """دریافت زلزله‌های ایران از USGS"""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days_back)

    start_str = start.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")

    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",
        "starttime": start_str,
        "endtime": end_str,
        "minmagnitude": min_magnitude,
        "minlatitude": IRAN_BBOX["min_lat"],
        "maxlatitude": IRAN_BBOX["max_lat"],
        "minlongitude": IRAN_BBOX["min_lon"],
        "maxlongitude": IRAN_BBOX["max_lon"],
        "orderby": "time",
        "limit": USGS_LIMIT,
    }

    try:
        r = requests.get(url, params=params, timeout=90)
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"خطا در دریافت داده از USGS: {e}") from e

    records = []
    for f in data.get("features", []):
        props = f["properties"]
        coords = f["geometry"]["coordinates"]
        records.append({
            "magnitude": props.get("mag"),
            "place": props.get("place"),
            "time": pd.to_datetime(props.get("time"), unit="ms", utc=True),
            "longitude": coords[0],
            "latitude": coords[1],
            "depth_km": coords[2] if len(coords) > 2 else None,
            "url": props.get("url"),
            "usgs_id": f.get("id"),
        })

    df = pd.DataFrame(records)
    if df.empty:
        return df, start_str, end_str

    df = df.dropna(subset=["magnitude", "latitude", "longitude"])
    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month
    df["dayofyear"] = df["time"].dt.dayofyear
    df["size"] = (df["magnitude"] ** 2) * 3.5

    return df, start_str, end_str