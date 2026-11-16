import streamlit as st
import pandas as pd

from services.usgs import fetch_earthquakes
from services.gem import fetch_iran_faults
from components.theme import apply_theme
from components.header import render_header
from components.metrics import show_summary_metrics
from components.recent_list import render_recent_earthquakes
from components.map import build_earthquake_map
from config import CACHE_TTL_EARTHQUAKES, CACHE_TTL_FAULTS
from components.theme import apply_theme
apply_theme()
st.set_page_config(
    page_title="Earthquake Intelligence | ایران",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

@st.cache_data(ttl=CACHE_TTL_EARTHQUAKES, show_spinner="دریافت زلزله‌ها از USGS...")
def load_eq():
    return fetch_earthquakes()

@st.cache_data(ttl=CACHE_TTL_FAULTS, show_spinner="دریافت گسل‌ها از GEM...")
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

render_header(st.session_state["last_update"])
show_summary_metrics(df, faults, start_time, end_time)

# اطمینان از timezone
work = df.copy()
if work["time"].dt.tz is None:
    work["time"] = work["time"].dt.tz_localize("UTC")

last_24h = work[work["time"] >= pd.Timestamp.now(tz="UTC") - pd.Timedelta(hours=24)]
strongest = work.loc[work["magnitude"].idxmax()]

left, right = st.columns([2.35, 1], gap="large")

with left:
    st.markdown("### نقشه کلی")
    map_df = work.sort_values("time", ascending=False).head(2500)
    fig = build_earthquake_map(
        map_df,
        faults=faults,
        show_faults=True,
        height=640,
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown("### وضعیت سریع")
    st.markdown(
        f"""
        <div class="panel-card">
            <div class="panel-title">خلاصه ۲۴ ساعت</div>
            <div style="color:#E2E8F0;line-height:1.85;">
                تعداد: <b>{len(last_24h)}</b><br>
                قوی‌ترین کل بازه: <b>M {strongest['magnitude']:.1f}</b><br>
                مکان: <b>{str(strongest.get('place', ''))[:42]}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_recent_earthquakes(work, n=8)

    st.markdown(
        """
        <div class="panel-card">
            <div class="panel-title">منو</div>
            <div class="muted" style="line-height:1.7;">
                نقشه زنده · آمار · تحلیل گسل · شهرها · یادگیری ماشین
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.caption("منبع: USGS + GEM | خروجی‌ها تحلیلی هستند و هشدار رسمی محسوب نمی‌شوند.")