from datetime import timedelta

# محدوده جغرافیایی ایران (تقریبی)
IRAN_BBOX = {
    "min_lat": 25.0,
    "max_lat": 40.0,
    "min_lon": 44.0,
    "max_lon": 64.0,
}

# تنظیمات دریافت داده
DEFAULT_DAYS_BACK = 3650          # حدود ۱۰ سال
DEFAULT_MIN_MAGNITUDE = 4.0
USGS_LIMIT = 20000

# کش
CACHE_TTL_EARTHQUAKES = 60 * 60 * 6      # ۶ ساعت
CACHE_TTL_FAULTS = 60 * 60 * 24 * 7      # یک هفته

# رنگ‌بندی شدت زلزله (برای نقشه و UI)
MAG_COLORS = {
    "low": "#22C55E",        # < 4.5
    "moderate": "#FACC15",   # 4.5 – 5.4
    "strong": "#F97316",     # 5.5 – 6.4
    "major": "#EF4444",      # >= 6.5
}

# تم تیره پیشنهادی
THEME = {
    "bg": "#0B1220",
    "card": "#151F30",
    "primary": "#3B82F6",
    "text": "#F8FAFC",
}

# شهرهای مهم برای صفحات اختصاصی (بعداً استفاده می‌شود)
MAJOR_CITIES = {
    "تهران": {"lat": 35.6892, "lon": 51.3890, "radius_km": 150},
    "تبریز": {"lat": 38.0962, "lon": 46.2738, "radius_km": 120},
    "کرمان": {"lat": 30.2839, "lon": 57.0834, "radius_km": 150},
    "مشهد": {"lat": 36.2605, "lon": 59.6168, "radius_km": 120},
    "شیراز": {"lat": 29.5918, "lon": 52.5837, "radius_km": 120},
    "بندرعباس": {"lat": 27.1832, "lon": 56.2666, "radius_km": 120},
    "کرمانشاه": {"lat": 34.3142, "lon": 47.0650, "radius_km": 120},
}