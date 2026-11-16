# pages/2_انیمیشن_سالانه.py
import streamlit as st
import plotly.express as px

from components.theme import apply_theme
from services.usgs import fetch_earthquakes

st.set_page_config(page_title="انیمیشن سالانه", page_icon="🎬", layout="wide")
apply_theme()

st.title("🎬 انیمیشن زلزله‌ها سال به سال")

if "df" not in st.session_state:
    with st.spinner("بارگذاری داده‌ها..."):
        df, start_time, end_time = fetch_earthquakes()
        st.session_state["df"] = df

df = st.session_state["df"]
min_mag = st.sidebar.slider("حداقل شدت", 4.0, 7.5, 4.0, 0.1)
df_f = df[df["magnitude"] >= min_mag].copy().sort_values("year")

if df_f.empty:
    st.info("با این فیلتر داده‌ای نیست.")
    st.stop()

if "size" not in df_f.columns:
    df_f["size"] = df_f["magnitude"] ** 2 * 3.5

fig = px.scatter_map(
    df_f,
    lat="latitude",
    lon="longitude",
    size="size",
    color="magnitude",
    animation_frame="year",
    color_continuous_scale="YlOrRd",
    hover_name="place",
    hover_data={"magnitude": ":.1f", "time": True, "size": False},
    height=700,
    title="پخش سال‌به‌سال زلزله‌های ایران",
)

fig.update_layout(
    map_style="open-street-map",
    map=dict(center=dict(lat=32.5, lon=54.0), zoom=4.5),  # تمرکز روی ایران
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
)
# برای ثابت ماندن نما هنگام پخش فریم‌ها
fig.update_traces(selector=dict(type="scattermap"))
st.plotly_chart(fig, use_container_width=True)

st.caption("نقطه‌های بزرگ‌تر و قرمزتر = زلزله قوی‌تر")