

import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, timezone

# ====================== تنظیمات ======================
days_back = 3650          # ۱۰ سال اخیر
min_magnitude = 4.0

# محدوده ایران
min_lat, max_lat = 25.0, 40.0
min_lon, max_lon = 44.0, 64.0
# =====================================================

def get_utc_now():
    return datetime.now(timezone.utc)

end_time = get_utc_now().strftime("%Y-%m-%d")
start_time = (get_utc_now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

def fetch_usgs_earthquakes(start, end, min_mag, minlat, maxlat, minlon, maxlon):
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",
        "starttime": start,
        "endtime": end,
        "minmagnitude": min_mag,
        "minlatitude": minlat,
        "maxlatitude": maxlat,
        "minlongitude": minlon,
        "maxlongitude": maxlon,
        "orderby": "time",
        "limit": 20000
    }
    
    print(f"در حال دریافت زلزله‌ها از {start} تا {end} ...")
    print("لطفاً صبر کنید (ممکن است کمی طول بکشد)...")
    
    response = requests.get(url, params=params, timeout=90)
    print(f"وضعیت پاسخ: {response.status_code}")
    
    if response.status_code != 200:
        print(response.text[:800])
        raise Exception(f"خطا از سمت USGS با کد {response.status_code}")
    
    data = response.json()
    if "metadata" not in data:
        raise Exception("ساختار پاسخ API نامعتبر است")
    
    return data

def parse_earthquakes(geojson_data):
    records = []
    for feature in geojson_data.get("features", []):
        props = feature["properties"]
        coords = feature["geometry"]["coordinates"]
        
        records.append({
            "magnitude": props.get("mag"),
            "place": props.get("place"),
            "time": pd.to_datetime(props.get("time"), unit="ms"),
            "longitude": coords[0],
            "latitude": coords[1],
            "depth_km": coords[2] if len(coords) > 2 else None,
            "url": props.get("url")
        })
    
    df = pd.DataFrame(records)
    df = df.dropna(subset=["magnitude", "latitude", "longitude"])
    df["year"] = df["time"].dt.year
    return df

def create_visualizations(df):
    if df.empty:
        print("هیچ زلزله‌ای پیدا نشد.")
        return
    
    print(f"\nدر حال ساخت نمودارها برای {len(df)} زلزله...")
    
    df["size"] = df["magnitude"] ** 2 * 3.5
    
    # ========== ۱. نقشه اصلی (نقاط) ==========
    fig_map = px.scatter_map(
        df,
        lat="latitude",
        lon="longitude",
        size="size",
        color="magnitude",
        color_continuous_scale="YlOrRd",
        hover_name="place",
        hover_data={"magnitude": ":.1f", "depth_km": ":.1f", "time": True, "size": False},
        zoom=5,
        height=650,
        title=f"نقشه زلزله‌های ۱۰ سال اخیر ایران (از {start_time} تا {end_time})"
    )
    fig_map.update_layout(map_style="open-street-map", margin={"r":0,"t":50,"l":0,"b":0})
    
    # ========== ۲. نقشه حرارتی (Heatmap) ==========
    fig_heat = px.density_map(
        df,
        lat="latitude",
        lon="longitude",
        z="magnitude",
        radius=18,
        zoom=5,
        height=650,
        color_continuous_scale="YlOrRd",
        title="نقشه حرارتی تراکم زلزله‌ها (Heatmap)"
    )
    fig_heat.update_layout(map_style="open-street-map", margin={"r":0,"t":50,"l":0,"b":0})
    
    # ========== ۳. نمودار تعداد زلزله در هر سال ==========
    yearly = df.groupby("year").size().reset_index(name="تعداد")
    
    fig_year = px.bar(
        yearly,
        x="year",
        y="تعداد",
        text="تعداد",
        title="تعداد زلزله‌ها در هر سال (۱۰ سال اخیر)",
        color="تعداد",
        color_continuous_scale="YlOrRd"
    )
    fig_year.update_traces(textposition="outside")
    fig_year.update_layout(xaxis_title="سال", yaxis_title="تعداد زلزله")
    
    # ========== ۴. نمودار شدت (قبلی) ==========
    bins = [0, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 10]
    labels = ["<4.0", "4.0-4.5", "4.5-5.0", "5.0-5.5", "5.5-6.0", "6.0-6.5", "6.5-7.0", "≥7.0"]
    df["mag_bin"] = pd.cut(df["magnitude"], bins=bins, labels=labels, right=False)
    
    count_df = df["mag_bin"].value_counts().reindex(labels).fillna(0).reset_index()
    count_df.columns = ["شدت", "تعداد"]
    
    fig_mag = px.bar(
        count_df,
        x="شدت",
        y="تعداد",
        text="تعداد",
        title="تعداد زلزله‌ها بر اساس شدت",
        color="تعداد",
        color_continuous_scale="YlOrRd"
    )
    fig_mag.update_traces(textposition="outside")
    
    # ========== ۵. انیمیشن زمانی (سال به سال) ==========
    fig_anim = px.scatter_map(
        df.sort_values("year"),
        lat="latitude",
        lon="longitude",
        size="size",
        color="magnitude",
        animation_frame="year",
        color_continuous_scale="YlOrRd",
        hover_name="place",
        hover_data={"magnitude": ":.1f", "time": True, "size": False},
        zoom=5,
        height=700,
        title="انیمیشن زلزله‌ها بر اساس سال"
    )
    fig_anim.update_layout(map_style="open-street-map", margin={"r":0,"t":50,"l":0,"b":0})
    
    # نمایش همه نمودارها
    fig_map.show()
    fig_heat.show()
    fig_year.show()
    fig_mag.show()
    fig_anim.show()
    
    # ذخیره فایل‌ها
    fig_map.write_html("1_map_points.html")
    fig_heat.write_html("2_heatmap.html")
    fig_year.write_html("3_yearly_count.html")
    fig_mag.write_html("4_magnitude_bar.html")
    fig_anim.write_html("5_animation.html")
    
    print("\nهمه فایل‌ها ذخیره شدند:")
    print("1_map_points.html          → نقشه نقاط")
    print("2_heatmap.html             → نقشه حرارتی")
    print("3_yearly_count.html        → تعداد در هر سال")
    print("4_magnitude_bar.html       → نمودار شدت")
    print("5_animation.html           → انیمیشن زمانی")

# ====================== اجرای اصلی ======================
if __name__ == "__main__":
    try:
        data = fetch_usgs_earthquakes(
            start_time, end_time, min_magnitude,
            min_lat, max_lat, min_lon, max_lon
        )
        
        count = data.get("metadata", {}).get("count", len(data.get("features", [])))
        print(f"تعداد کل زلزله‌های پیدا شده: {count}")
        
        if count >= 20000:
            print("هشدار: به سقف ۲۰٬۰۰۰ رسیده!")
        
        df = parse_earthquakes(data)
        print(f"تعداد رکوردهای معتبر: {len(df)}")
        
        if not df.empty:
            print("\nنمونه داده‌ها:")
            print(df[["time", "magnitude", "place"]].head(6).to_string())
            create_visualizations(df)
        else:
            print("داده‌ای یافت نشد.")
            
    except Exception as e:
        print(f"\nخطا رخ داد: {e}")
