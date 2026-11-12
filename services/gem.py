import requests
from config import IRAN_BBOX

GEM_FAULTS_URL = (
    "https://raw.githubusercontent.com/cossatot/gem-global-active-faults/"
    "master/geojson/gem_active_faults.geojson"
)

def fetch_iran_faults() -> dict:
    """دریافت گسل‌های فعال در محدوده ایران از GEM"""
    try:
        r = requests.get(GEM_FAULTS_URL, timeout=120)
        r.raise_for_status()
        geojson = r.json()
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"خطا در دریافت گسل‌ها از GEM: {e}") from e

    iran_features = []
    for feat in geojson.get("features", []):
        geom = feat.get("geometry")
        if not geom:
            continue

        # فیلتر ساده بر اساس مختصات (می‌توان بعداً دقیق‌تر کرد)
        coords = geom.get("coordinates", [])
        if _is_in_iran_bbox(coords):
            iran_features.append(feat)

    return {
        "type": "FeatureCollection",
        "features": iran_features,
    }

def _is_in_iran_bbox(coords) -> bool:
    """بررسی تقریبی اینکه آیا هندسه داخل محدوده ایران است"""
    def check_point(lon, lat):
        return (
            IRAN_BBOX["min_lon"] <= lon <= IRAN_BBOX["max_lon"]
            and IRAN_BBOX["min_lat"] <= lat <= IRAN_BBOX["max_lat"]
        )

    if not coords:
        return False

    # LineString یا MultiLineString
    if isinstance(coords[0], (int, float)):
        return check_point(coords[0], coords[1])
    if isinstance(coords[0][0], (int, float)):
        return any(check_point(p[0], p[1]) for p in coords)
    # Multi
    for line in coords:
        if any(check_point(p[0], p[1]) for p in line):
            return True
    return False