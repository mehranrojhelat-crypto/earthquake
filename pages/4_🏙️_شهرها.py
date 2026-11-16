# pages/4_🏙️_شهرها.py
import streamlit as st
import pandas as pd
import plotly.express as px

from config import MAJOR_CITIES
from utils.geo import filter_by_radius
from components.map import build_earthquake_map
from components.theme import apply_theme
from services.usgs import fetch_earthquakes
from services.gem import fetch_iran_faults

st.set_page_config(page_title="صفحات شهرها", page_icon="🏙️", layout="wide")
apply_theme()

st.title("🏙️ تحلیل لرزه‌ای شهرهای مهم")

# اگر مستقیم وارد صفحه شد، داده را همین‌جا لود کن
if "df" not in st.session_state:
    with st.spinner("در حال بارگذاری داده‌ها..."):
        df, start_time, end_time = fetch_earthquakes()
        faults = fetch_iran_faults()
        st.session_state["df"] = df
        st.session_state["faults"] = faults
        st.session_state["start_time"] = start_time
        st.session_state["end_time"] = end_time

df_all = st.session_state["df"].copy()
faults = st.session_state.get("faults", {"features": []})

if not MAJOR_CITIES:
    st.error("لیست شهرها در config.py تعریف نشده است.")
    st.stop()

# ---------- فیلترها ----------
city_name = st.sidebar.selectbox("انتخاب شهر", list(MAJOR_CITIES.keys()))
city = MAJOR_CITIES[city_name]

radius = st.sidebar.slider(
    "شعاع تحلیل (کیلومتر)",
    min_value=50,
    max_value=300,
    value=int(city["radius_km"]),
    step=10,
)
min_mag = st.sidebar.slider("حداقل بزرگی", 4.0, 7.0, 4.0, 0.1)

time_options = {
    "۹۰ روز اخیر": 90,
    "۱ سال اخیر": 365,
    "۵ سال اخیر": 365 * 5,
    "همه داده‌ها": None,
}
time_label = st.sidebar.selectbox("بازه زمانی", list(time_options.keys()), index=3)
days = time_options[time_label]

work = df_all.copy()
if work["time"].dt.tz is None:
    work["time"] = work["time"].dt.tz_localize("UTC")

if days is not None:
    cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=days)
    work = work[work["time"] >= cutoff]

work = work[work["magnitude"] >= min_mag]
city_df = filter_by_radius(work, city["lat"], city["lon"], radius)

st.subheader(f"تحلیل اطراف {city_name}")
st.caption(f"مرکز: ({city['lat']:.3f}, {city['lon']:.3f}) | شعاع: {radius} km")

# ---------- کارت‌ها ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("تعداد زلزله", f"{len(city_df):,}")

if city_df.empty:
    c2.metric("میانگین بزرگی", "—")
    c3.metric("بیشینه بزرگی", "—")
    c4.metric("نزدیک‌ترین رویداد", "—")
    st.warning("در این بازه و شعاع زلزله‌ای ثبت نشده. شعاع را بیشتر کن یا بازه را «همه داده‌ها» بگذار.")
    st.stop()

c2.metric("میانگین بزرگی", f"{city_df['magnitude'].mean():.2f}")
c3.metric("بیشینه بزرگی", f"{city_df['magnitude'].max():.1f}")
nearest = city_df.loc[city_df["distance_km"].idxmin()]
c4.metric("نزدیک‌ترین رویداد", f"{nearest['distance_km']:.1f} km")

# ---------- نقشه ----------
fig = build_earthquake_map(
    city_df,
    faults=faults,
    show_faults=True,
    center_lat=city["lat"],
    center_lon=city["lon"],
    zoom=6.2,
    height=560,
)
st.plotly_chart(fig, use_container_width=True)

# ---------- روند زمانی ----------
st.subheader("روند تعداد زلزله‌ها")
timeline = (
    city_df.set_index("time")
    .resample("MS")["magnitude"]
    .count()
    .rename("count")
    .reset_index()
)
fig_time = px.area(
    timeline,
    x="time",
    y="count",
    color_discrete_sequence=["#3B82F6"],
)
fig_time.update_layout(
    height=320,
    margin=dict(l=10, r=10, t=20, b=10),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis_title="زمان",
    yaxis_title="تعداد",
)
st.plotly_chart(fig_time, use_container_width=True)

# ---------- توزیع‌ها ----------
left, right = st.columns(2)
with left:
    st.subheader("توزیع بزرگی")
    fig_mag = px.histogram(
        city_df,
        x="magnitude",
        nbins=20,
        color_discrete_sequence=["#F97316"],
    )
    fig_mag.update_layout(
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_mag, use_container_width=True)

with right:
    st.subheader("فاصله از مرکز شهر")
    fig_dist = px.histogram(
        city_df,
        x="distance_km",
        nbins=20,
        color_discrete_sequence=["#22C55E"],
    )
    fig_dist.update_layout(
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_dist, use_container_width=True)

# ---------- جدول ----------
st.subheader("نزدیک‌ترین / جدیدترین زلزله‌ها")
table = (
    city_df.sort_values("time", ascending=False)
    .head(40)[
        ["time", "magnitude", "place", "depth_km", "distance_km", "latitude", "longitude"]
    ]
    .copy()
)
table["time"] = table["time"].dt.strftime("%Y-%m-%d %H:%M")
table = table.rename(
    columns={
        "time": "زمان (UTC)",
        "magnitude": "بزرگی",
        "place": "مکان",
        "depth_km": "عمق (km)",
        "distance_km": "فاصله از شهر (km)",
        "latitude": "عرض",
        "longitude": "طول",
    }
)
st.dataframe(table, use_container_width=True, hide_index=True)

st.caption(
    "این صفحه فقط رویدادهای ثبت‌شده اطراف شهر را تحلیل می‌کند و به معنی پیش‌بینی زلزله آینده نیست."
)