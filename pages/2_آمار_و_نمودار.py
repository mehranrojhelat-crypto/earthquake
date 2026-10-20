import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="آمار و نمودار", page_icon="📊", layout="wide")
st.title("📊 آمار و نمودارها")

if "df" not in st.session_state:
    st.warning("ابتدا به صفحه اصلی بروید تا داده‌ها بارگذاری شوند.")
    st.stop()

df = st.session_state["df"]
min_mag = st.sidebar.slider("حداقل magnitude", 4.0, 7.5, 4.0, 0.1)
df_f = df[df["magnitude"] >= min_mag].copy()

c1, c2, c3 = st.columns(3)
c1.metric("تعداد", len(df_f))
c2.metric("بیشینه mag", f"{df_f['magnitude'].max():.1f}" if len(df_f) else "-")
c3.metric("میانگین عمق", f"{df_f['depth_km'].mean():.1f} km" if len(df_f) else "-")

yearly = df_f.groupby("year").size().reset_index(name="تعداد")
fig_year = px.bar(yearly, x="year", y="تعداد", text="تعداد",
                  title="تعداد زلزله در هر سال", color="تعداد",
                  color_continuous_scale="YlOrRd")
st.plotly_chart(fig_year, use_container_width=True)

bins = [4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 10]
labels = ["4.0-4.5", "4.5-5.0", "5.0-5.5", "5.5-6.0", "6.0-6.5", "6.5-7.0", "≥7.0"]
df_f["mag_bin"] = pd.cut(df_f["magnitude"], bins=bins, labels=labels, right=False)
count_df = df_f["mag_bin"].value_counts().reindex(labels).fillna(0).reset_index()
count_df.columns = ["شدت", "تعداد"]

fig_mag = px.bar(count_df, x="شدت", y="تعداد", text="تعداد",
                 title="توزیع شدت", color="تعداد",
                 color_continuous_scale="YlOrRd")
st.plotly_chart(fig_mag, use_container_width=True)

fig_heat = px.density_map(
    df_f, lat="latitude", lon="longitude", z="magnitude",
    radius=18, zoom=4.5, height=550,
    map_style="open-street-map",
    color_continuous_scale="YlOrRd",
    title="نقشه حرارتی",
)
st.plotly_chart(fig_heat, use_container_width=True)