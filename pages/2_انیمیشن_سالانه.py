import streamlit as st
import plotly.express as px

st.set_page_config(page_title="انیمیشن سالانه", page_icon="🎬", layout="wide")
st.title("🎬 انیمیشن زلزله‌ها سال به سال")

st.markdown("""
در این صفحه می‌توانید ببینید زلزله‌ها در طول سال‌ها **چطور روی نقشه جابه‌جا و پخش شده‌اند**.
دکمه پخش را بزنید تا سال‌به‌سال جلو برود.
""")

if "df" not in st.session_state:
    st.warning("ابتدا به صفحه اصلی بروید تا داده‌ها بارگذاری شوند.")
    st.stop()

df = st.session_state["df"]
min_mag = st.sidebar.slider("حداقل شدت زلزله", 4.0, 7.5, 4.0, 0.1)
df_f = df[df["magnitude"] >= min_mag].copy().sort_values("year")

if df_f.empty:
    st.info("با این فیلتر داده‌ای نیست.")
    st.stop()

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
    zoom=5,
    height=700,
    title="پخش سال‌به‌سال زلزله‌های ایران",
)
fig.update_layout(map_style="open-street-map", margin={"r": 0, "t": 50, "l": 0, "b": 0})
st.plotly_chart(fig, use_container_width=True)

st.caption("نقطه‌های بزرگ‌تر و قرمزتر = زلزله قوی‌تر")