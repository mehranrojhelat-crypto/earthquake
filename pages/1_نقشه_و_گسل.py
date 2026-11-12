import streamlit as st
import pandas as pd
from components.map import build_earthquake_map
from components.theme import apply_theme
apply_theme()
st.markdown("""
<style>
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
    div[data-testid="stMetric"] {
        background: #151F30;
        border: 1px solid #1F2A44;
        border-radius: 12px;
        padding: 12px 14px;
    }
    div[data-testid="stMetric"] label { color: #94A3B8 !important; }
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="نقشه زنده", page_icon="🗺️", layout="wide")
st.title("🗺️ نقشه زنده زلزله‌ها و گسل‌های فعال")

if "df" not in st.session_state:
    st.warning("ابتدا به صفحه اصلی بروید تا داده‌ها بارگذاری شوند.")
    st.stop()

df = st.session_state["df"].copy()
faults = st.session_state.get("faults", {"features": []})

# ---------- فیلترها ----------
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

min_mag, max_mag = st.sidebar.slider(
    "بازه بزرگی (Magnitude)",
    min_value=4.0,
    max_value=8.0,
    value=(4.0, 8.0),
    step=0.1,
)

show_faults = st.sidebar.checkbox("نمایش گسل‌ها", value=True)

# فیلتر زمانی
if days is not None:
    cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=days)
    # اگر time بدون timezone باشد، آن را utc فرض می‌کنیم
    if df["time"].dt.tz is None:
        df["time"] = df["time"].dt.tz_localize("UTC")
    df = df[df["time"] >= cutoff]

# فیلتر بزرگی
df = df[(df["magnitude"] >= min_mag) & (df["magnitude"] <= max_mag)]

# ---------- خلاصه ----------
c1, c2, c3 = st.columns(3)
c1.metric("تعداد نمایش‌داده‌شده", f"{len(df):,}")
c2.metric("حداقل بزرگی", f"{min_mag}")
c3.metric("حداکثر بزرگی", f"{max_mag}")

if df.empty:
    st.info("با فیلترهای انتخاب‌شده زلزله‌ای پیدا نشد.")
    st.stop()

# ---------- نقشه ----------
fig = build_earthquake_map(df, faults=faults, show_faults=show_faults, height=720)
st.plotly_chart(fig, use_container_width=True)

# ---------- جدول آخرین رویدادها ----------
st.subheader("آخرین زلزله‌های فیلترشده")
table_df = (
    df.sort_values("time", ascending=False)
    .head(30)[["time", "magnitude", "place", "depth_km", "latitude", "longitude"]]
    .copy()
)
table_df["time"] = table_df["time"].dt.strftime("%Y-%m-%d %H:%M")
table_df = table_df.rename(
    columns={
        "time": "زمان (UTC)",
        "magnitude": "بزرگی",
        "place": "مکان",
        "depth_km": "عمق (km)",
        "latitude": "عرض",
        "longitude": "طول",
    }
)
st.dataframe(table_df, use_container_width=True, hide_index=True)

st.caption("منبع زلزله: USGS | منبع گسل: GEM Active Faults")