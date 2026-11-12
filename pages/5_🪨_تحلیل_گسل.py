# pages/5_🪨_تحلیل_گسل.py
import streamlit as st
import pandas as pd
import plotly.express as px

from config import MAJOR_CITIES
from utils.geo import compute_distance_to_nearest_fault
from services.fault_analysis import distance_summary, compare_by_magnitude, city_fault_proximity
from components.map import build_earthquake_map
from components.theme import apply_theme
apply_theme()
st.set_page_config(page_title="تحلیل گسل", page_icon="🪨", layout="wide")
st.title("🪨 تحلیل ارتباط زلزله‌ها با گسل‌های فعال")

st.info(
    "این صفحه فاصله تقریبی زلزله‌های ثبت‌شده تا نزدیک‌ترین گسل GEM را بررسی می‌کند. "
    "نتیجه توصیفی است و به معنی پیش‌بینی زلزله نیست."
)

if "df" not in st.session_state:
    st.warning("ابتدا به صفحه اصلی بروید تا داده‌ها بارگذاری شوند.")
    st.stop()

df = st.session_state["df"].copy()
faults = st.session_state.get("faults", {"features": []})

# فیلترها
min_mag = st.sidebar.slider("حداقل بزرگی", 4.0, 7.0, 4.0, 0.1)
threshold = st.sidebar.slider("آستانه زلزله قوی", 4.5, 6.5, 5.0, 0.1)
city_radius = st.sidebar.slider("شعاع مقایسه شهرها (km)", 50, 300, 150, 10)

df = df[df["magnitude"] >= min_mag].copy()

run = st.button("محاسبه فاصله تا گسل", type="primary")

if not run and "df_fault_dist" not in st.session_state:
    st.warning("برای شروع، دکمه محاسبه را بزن.")
    st.stop()

if run:
    with st.spinner("در حال محاسبه فاصله تا نزدیک‌ترین گسل..."):
        df_dist = compute_distance_to_nearest_fault(df, faults)
        st.session_state["df_fault_dist"] = df_dist

df_dist = st.session_state["df_fault_dist"]

# ---------- خلاصه کلی ----------
summary = distance_summary(df_dist)
if not summary:
    st.error("فاصله‌ای محاسبه نشد. داده گسل یا زلزله را بررسی کنید.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("تعداد رویداد", f"{summary['count']:,}")
c2.metric("میانگین فاصله", f"{summary['mean']:.1f} km")
c3.metric("میانه فاصله", f"{summary['median']:.1f} km")
c4.metric("حداقل فاصله", f"{summary['min']:.1f} km")

st.caption(
    f"چارک اول/سوم: {summary['p25']:.1f} / {summary['p75']:.1f} km | "
    f"بیشینه: {summary['max']:.1f} km"
)

# ---------- نمودار توزیع فاصله ----------
left, right = st.columns(2)

with left:
    st.subheader("توزیع فاصله تا گسل")
    fig_hist = px.histogram(
        df_dist.dropna(subset=["dist_to_fault_km"]),
        x="dist_to_fault_km",
        nbins=40,
        color_discrete_sequence=["#3B82F6"],
    )
    fig_hist.update_layout(
        xaxis_title="فاصله تا نزدیک‌ترین گسل (km)",
        yaxis_title="تعداد",
        height=360,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with right:
    st.subheader("بزرگی در برابر فاصله تا گسل")
    fig_sc = px.scatter(
        df_dist.dropna(subset=["dist_to_fault_km"]),
        x="dist_to_fault_km",
        y="magnitude",
        opacity=0.65,
        color="magnitude",
        color_continuous_scale="YlOrRd",
        hover_data=["place", "depth_km"],
    )
    fig_sc.update_layout(
        xaxis_title="فاصله تا گسل (km)",
        yaxis_title="Magnitude",
        height=360,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_sc, use_container_width=True)

# ---------- مقایسه ضعیف/قوی ----------
st.subheader("مقایسه فاصله تا گسل: زلزله‌های ضعیف‌تر و قوی‌تر")
cmp = compare_by_magnitude(df_dist, threshold=threshold)
st.dataframe(cmp, use_container_width=True, hide_index=True)

fig_box = px.box(
    df_dist.dropna(subset=["dist_to_fault_km"]).assign(
        group=lambda d: d["magnitude"].ge(threshold).map({True: f"M≥{threshold}", False: f"M<{threshold}"})
    ),
    x="group",
    y="dist_to_fault_km",
    color="group",
    color_discrete_sequence=["#22C55E", "#EF4444"],
)
fig_box.update_layout(
    height=380,
    showlegend=False,
    yaxis_title="فاصله تا گسل (km)",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig_box, use_container_width=True)

# ---------- مقایسه شهرها ----------
st.subheader("مقایسه شهرها از نظر فاصله زلزله‌ها تا گسل")
city_table = city_fault_proximity(df_dist, MAJOR_CITIES, radius_km=city_radius)
st.dataframe(city_table, use_container_width=True, hide_index=True)

fig_city = px.bar(
    city_table.dropna(),
    x="شهر",
    y="میانگین فاصله تا گسل (km)",
    color="میانگین بزرگی",
    color_continuous_scale="YlOrRd",
    text="تعداد زلزله",
)
fig_city.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig_city, use_container_width=True)

# ---------- نقشه ----------
st.subheader("نقشه زلزله‌ها + گسل‌ها")
# برای خوانایی، نزدیک‌ترین‌ها را کمی برجسته‌تر نشان می‌دهیم
map_df = df_dist.dropna(subset=["dist_to_fault_km"]).copy()
map_df = map_df.sort_values("dist_to_fault_km").head(3000)  # محدود برای سرعت

fig_map = build_earthquake_map(
    map_df,
    faults=faults,
    show_faults=True,
    height=620,
)
st.plotly_chart(fig_map, use_container_width=True)

st.caption(
    "فاصله‌ها تقریبی‌اند (بر اساس نمونه‌برداری از خطوط گسل GEM). "
    "نزدیک بودن آماری به گسل به‌تنهایی احتمال وقوع آینده را مشخص نمی‌کند."
)