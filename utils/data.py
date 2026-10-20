# utils/data.py
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone

DAYS_BACK = 3650
MIN_MAG = 4.0
MIN_LAT, MAX_LAT = 25.0, 40.0
MIN_LON, MAX_LON = 44.0, 64.0

GEM_FAULTS_URL = "https://raw.githubusercontent.com/cossatot/gem-global-active-faults/master/geojson/gem_active_faults.geojson"

def fetch_earthquakes():
    end = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    start = (datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)).strftime("%Y-%m-%d")

    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",
        "starttime": start,
        "endtime": end,
        "minmagnitude": MIN_MAG,
        "minlatitude": MIN_LAT,
        "maxlatitude": MAX_LAT,
        "minlongitude": MIN_LON,
        "maxlongitude": MAX_LON,
        "orderby": "time",
        "limit": 20000,
    }
    r = requests.get(url, params=params, timeout=90)
    r.raise_for_status()
    data = r.json()

    records = []
    for f in data.get("features", []):
        props = f["properties"]
        coords = f["geometry"]["coordinates"]
        records.append({
            "magnitude": props.get("mag"),
            "place": props.get("place"),
            "time": pd.to_datetime(props.get("time"), unit="ms"),
            "longitude": coords[0],
            "latitude": coords[1],
            "depth_km": coords[2] if len(coords) > 2 else None,
            "url": props.get("url"),
        })

    df = pd.DataFrame(records).dropna(subset=["magnitude", "latitude", "longitude", "depth_km"])
    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month
    df["dayofyear"] = df["time"].dt.dayofyear
    df["size"] = df["magnitude"] ** 2 * 3.5
    return df, start, end

def fetch_iran_faults():
    try:
        r = requests.get(GEM_FAULTS_URL, timeout=120)
        r.raise_for_status()
        geojson = r.json()

        iran_features = []
        for feat in geojson.get("features", []):
            geom = feat.get("geometry")
            if not geom:
                continue

            points = []
            if geom["type"] == "LineString":
                points = geom["coordinates"]
            elif geom["type"] == "MultiLineString":
                for line in geom["coordinates"]:
                    points.extend(line)

            if not points:
                continue

            lons = [p[0] for p in points]
            lats = [p[1] for p in points]

            if (min(lons) <= MAX_LON and max(lons) >= MIN_LON and
                    min(lats) <= MAX_LAT and max(lats) >= MIN_LAT):
                iran_features.append(feat)

        return {"type": "FeatureCollection", "features": iran_features}
    except Exception:
        return {"type": "FeatureCollection", "features": []}