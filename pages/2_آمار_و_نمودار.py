import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from components.filters import apply_common_filters
from components.theme import apply_theme
apply_theme()
st.set_page_config(page_title="آمار و تحلیل", page_icon="📊", layout="wide")
st.title("📊 آمار و تحلیل لرزه‌ای")

if "df" not in st.session_state:
    st.warning("ابتدا به صفحه اصلی بروید تا داده‌ها بارگذاری شوند.")
    st.stop()

df_all = st.session_state["df"]
df = apply_common_filters(df_all, key_prefix="stats")

if df.empty:
    st.info("با فیلترهای انتخاب‌شده داده‌ای وجود ندارد.")
    st.stop()

# ---------- کارت‌های خلاصه ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("تعداد زلزله", f"{len(df):,}")
c2.metric("میانگین بزرگی", f"{df['magnitude'].mean():.2f}")
c3.metric("بیشینه بزرگی", f"{df['magnitude'].max():.1f}")
c4.metric("میانگین عمق (km)", f"{df['depth_km'].mean():.1f}" if "depth_km" in df.columns else "—")

st.divider()

# ---------- ردیف نمودارها ----------
left, right = st.columns(2)

with left:
    st.subheader("توزیع بزرگی")
    fig_mag = px.histogram(
        df,
        x="magnitude",
        nbins=30,
        color_discrete_sequence=["#3B82F6"],
    )
    fig_mag.update_layout(
        xaxis_title="Magnitude",
        yaxis_title="تعداد",
        height=360,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_mag, use_container_width=True)

with right:
    st.subheader("توزیع عمق")
    if "depth_km" in df.columns:
        fig_depth = px.histogram(
            df,
            x="depth_km",
            nbins=30,
            color_discrete_sequence=["#22C55E"],
        )
        fig_depth.update_layout(
            xaxis_title="عمق (km)",
            yaxis_title="تعداد",
            height=360,
            margin=dict(l=10, r=10, t=30, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_depth, use_container_width=True)
    else:
        st.info("ستون عمق موجود نیست.")

# ---------- تایم‌لاین ----------
st.subheader("روند زمانی تعداد زلزله‌ها")

timeline = (
    df.set_index("time")
    .resample("MS")["magnitude"]
    .count()
    .rename("count")
    .reset_index()
)

fig_time = px.area(
    timeline,
    x="time",
    y="count",
    color_discrete_sequence=["#F97316"],
)
fig_time.update_layout(
    xaxis_title="زمان",
    yaxis_title="تعداد زلزله در ماه",
    height=380,
    margin=dict(l=10, r=10, t=20, b=10),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig_time, use_container_width=True)



st.subheader("نقشه حرارتی تراکم زلزله‌ها")

heat_df = df.copy()
if len(heat_df) > 5000:
    heat_df = heat_df.sort_values("time", ascending=False).head(5000)

fig_heat = px.density_map(
    heat_df,
    lat="latitude",
    lon="longitude",
    z="magnitude",
    radius=18,
    center=dict(lat=32.5, lon=54.0),
    zoom=4.5,
    height=650,
    color_continuous_scale="YlOrRd",
    title="نقشه حرارتی تراکم زلزله‌ها (Heatmap)",
)
fig_heat.update_layout(
    map_style="open-street-map",
    margin=dict(r=0, t=40, l=0, b=0),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig_heat, use_container_width=True)
st.caption("رنگ گرم‌تر = تراکم/شدت بیشتر رویدادها در آن ناحیه")

# ---------- رابطه بزرگی و عمق ----------
st.subheader("رابطه بزرگی و عمق")
if "depth_km" in df.columns:
    fig_scatter = px.scatter(
        df,
        x="depth_km",
        y="magnitude",
        color="magnitude",
        color_continuous_scale="YlOrRd",
        opacity=0.7,
        hover_data=["place", "time"],
    )
    fig_scatter.update_layout(
        xaxis_title="عمق (km)",
        yaxis_title="Magnitude",
        height=400,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ---------- جدول خلاصه سالانه ----------
st.subheader("خلاصه سالانه")
yearly = (
    df.groupby("year")
    .agg(
        count=("magnitude", "count"),
        mean_mag=("magnitude", "mean"),
        max_mag=("magnitude", "max"),
        mean_depth=("depth_km", "mean"),
    )
    .reset_index()
    .sort_values("year", ascending=False)
)
yearly["mean_mag"] = yearly["mean_mag"].round(2)
yearly["max_mag"] = yearly["max_mag"].round(1)
yearly["mean_depth"] = yearly["mean_depth"].round(1)
yearly = yearly.rename(
    columns={
        "year": "سال",
        "count": "تعداد",
        "mean_mag": "میانگین بزرگی",
        "max_mag": "بیشینه بزرگی",
        "mean_depth": "میانگین عمق",
    }
)
st.dataframe(yearly, use_container_width=True, hide_index=True)

st.caption("این آمارها توصیفی هستند و به معنی پیش‌بینی وقوع زلزله آینده نیستند.")