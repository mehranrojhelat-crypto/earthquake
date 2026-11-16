# pages/1_نقشه_و_گسل.py
import streamlit as st
import pandas as pd

from components.theme import apply_theme
from components.map import build_earthquake_map
from services.usgs import fetch_earthquakes
from services.gem import fetch_iran_faults

st.set_page_config(page_title="نقشه زنده", page_icon="🗺️", layout="wide")
apply_theme()

st.title("🗺️ نقشه زنده زلزله‌ها و گسل‌های فعال")

# اگر کاربر مستقیم آمد، داده را همین‌جا لود کن
if "df" not in st.session_state:
    with st.spinner("بارگذاری داده‌ها..."):
        df, start_time, end_time = fetch_earthquakes()
        faults = fetch_iran_faults()
        st.session_state["df"] = df
        st.session_state["faults"] = faults
        st.session_state["start_time"] = start_time
        st.session_state["end_time"] = end_time

df = st.session_state["df"].copy()
faults = st.session_state.get("faults", {"features": []})

st.sidebar.header("فیلترها")
time_options = {
    "۲۴ ساعت اخیر": 1,
    "۷ روز اخیر": 7,
    "۳۰ روز اخیر": 30,
    "۹۰ روز اخیر": 90,
    "۱ سال اخیر": 365,
    "همه داده‌ها": None,
}
time_label = st.sidebar.selectbox("بازه زمانی", list(time_options.keys()), index=5)
days = time_options[time_label]

min_mag, max_mag = st.sidebar.slider("بازه بزرگی", 4.0, 8.0, (4.0, 8.0), 0.1)
show_faults = st.sidebar.checkbox("نمایش گسل‌ها", value=True)

if df["time"].dt.tz is None:
    df["time"] = df["time"].dt.tz_localize("UTC")

if days is not None:
    cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=days)
    df = df[df["time"] >= cutoff]

df = df[(df["magnitude"] >= min_mag) & (df["magnitude"] <= max_mag)]

c1, c2, c3 = st.columns(3)
c1.metric("تعداد", f"{len(df):,}")
c2.metric("حداقل بزرگی", f"{min_mag}")
c3.metric("حداکثر بزرگی", f"{max_mag}")

if df.empty:
    st.info("با این فیلتر زلزله‌ای پیدا نشد.")
    st.stop()

fig = build_earthquake_map(
    df,
    faults=faults,
    show_faults=show_faults,
    center_lat=32.5,
    center_lon=54.0,
    zoom=4.5,
    height=720,
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("آخرین زلزله‌ها")
table_df = (
    df.sort_values("time", ascending=False)
    .head(30)[["time", "magnitude", "place", "depth_km", "latitude", "longitude"]]
    .copy()
)
table_df["time"] = table_df["time"].dt.strftime("%Y-%m-%d %H:%M")
st.dataframe(table_df, use_container_width=True, hide_index=True)