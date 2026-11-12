# app.py
import streamlit as st
import pandas as pd

from services.usgs import fetch_earthquakes
from services.gem import fetch_iran_faults
from components.metrics import show_summary_metrics
from components.header import render_header
from components.recent_list import render_recent_earthquakes
from components.map import build_earthquake_map
from config import CACHE_TTL_EARTHQUAKES, CACHE_TTL_FAULTS

st.set_page_config(
    page_title="Earthquake Intelligence | ایران",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS همان بلوک بالا را اینجا قرار بده
st.markdown("""...CSS...""", unsafe_allow_html=True)

@st.cache_data(ttl=CACHE_TTL_EARTHQUAKES, show_spinner="دریافت زلزله‌ها...")
def load_eq():
    return fetch_earthquakes()

@st.cache_data(ttl=CACHE_TTL_FAULTS, show_spinner="دریافت گسل‌ها...")
def load_faults():
    return fetch_iran_faults()

try:
    df, start_time, end_time = load_eq()
    faults = load_faults()

    st.session_state["df"] = df
    st.session_state["faults"] = faults
    st.session_state["start_time"] = start_time
    st.session_state["end_time"] = end_time
    st.session_state["last_update"] = pd.Timestamp.now(tz="UTC")

except Exception as e:
    st.error(f"خطا در بارگذاری داده‌ها: {e}")
    st.stop()

# ----- Header -----
render_header(st.session_state["last_update"])

# ----- Metrics -----
show_summary_metrics(df, faults, start_time, end_time)

st.write("")

# ----- Main layout: map + side panel -----
left, right = st.columns([2.3, 1], gap="large")

with left:
    st.markdown("### نقشه کلی ایران")
    # برای سرعت، فقط زلزله‌های اخیرتر یا نمونه‌ای از داده‌ها
    map_df = df.sort_values("time", ascending=False).head(2500)
    fig = build_earthquake_map(
        map_df,
        faults=faults,
        show_faults=True,
        height=640,
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown("### خلاصه وضعیت")
    last_24h = df.copy()
    if last_24h["time"].dt.tz is None:
        last_24h["time"] = last_24h["time"].dt.tz_localize("UTC")
    last_24h = last_24h[last_24h["time"] >= pd.Timestamp.now(tz="UTC") - pd.Timedelta(hours=24)]

    strongest = df.loc[df["magnitude"].idxmax()]
    st.markdown(
        f"""
        <div class="panel-card">
            <div class="panel-title">وضعیت سریع</div>
            <div style="color:#E2E8F0; line-height:1.8;">
                زلزله ۲۴ ساعت اخیر: <b>{len(last_24h)}</b><br>
                قوی‌ترین کل بازه: <b>M {strongest['magnitude']:.1f}</b><br>
                مکان: <b>{str(strongest.get('place', ''))[:40]}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_recent_earthquakes(df, n=8)

    st.markdown(
        """
        <div class="panel-card">
            <div class="panel-title">راهنما</div>
            <div style="color:#94A3B8; font-size:0.88rem; line-height:1.7;">
                از منوی سمت چپ وارد بخش‌های نقشه زنده، آمار، تحلیل گسل، شهرها و یادگیری ماشین شوید.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.caption("منبع زلزله: USGS | منبع گسل: GEM | این سامانه برای تحلیل آماری است، نه هشدار رسمی.")