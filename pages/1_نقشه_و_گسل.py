import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="نقشه و گسل", page_icon="🗺️", layout="wide")
st.title("🗺️ نقشه زلزله‌ها + گسل‌های فعال")

if "df" not in st.session_state:
    st.warning("ابتدا به صفحه اصلی بروید تا داده‌ها بارگذاری شوند.")
    st.stop()

df = st.session_state["df"]
faults = st.session_state["faults"]

min_mag = st.sidebar.slider("حداقل magnitude", 4.0, 7.5, 4.0, 0.1)
show_faults = st.sidebar.checkbox("نمایش گسل‌ها", value=True)

df_f = df[df["magnitude"] >= min_mag].copy()

fig = go.Figure()

fig.add_trace(go.Scattermap(
    lat=df_f["latitude"],
    lon=df_f["longitude"],
    mode="markers",
    marker=dict(
        size=np.clip(df_f["size"] / 8, 4, 25),
        color=df_f["magnitude"],
        colorscale="YlOrRd",
        showscale=True,
        colorbar=dict(title="Magnitude"),
    ),
    text=df_f["place"],
    customdata=np.stack([
        df_f["magnitude"],
        df_f["depth_km"],
        df_f["time"].astype(str),
    ], axis=-1),
    hovertemplate="<b>%{text}</b><br>Mag: %{customdata[0]:.1f}<br>Depth: %{customdata[1]:.1f} km<br>%{customdata[2]}<extra></extra>",
    name="زلزله‌ها",
))

if show_faults and faults.get("features"):
    for feat in faults["features"]:
        geom = feat["geometry"]
        name = feat.get("properties", {}).get("name", "Fault")

        lines = []
        if geom["type"] == "LineString":
            lines = [geom["coordinates"]]
        elif geom["type"] == "MultiLineString":
            lines = geom["coordinates"]

        for line in lines:
            lons = [p[0] for p in line]
            lats = [p[1] for p in line]
            fig.add_trace(go.Scattermap(
                lat=lats, lon=lons,
                mode="lines",
                line=dict(width=2, color="black"),
                name=name,
                hoverinfo="name",
                showlegend=False,
            ))

fig.update_layout(
    map_style="open-street-map",
    map=dict(center=dict(lat=32.5, lon=54), zoom=4.5),
    height=700,
    margin=dict(l=0, r=0, t=30, b=0),
    title=f"زلزله‌های ≥ {min_mag} + گسل‌های فعال (GEM)",
)
st.plotly_chart(fig, use_container_width=True)
st.caption("خطوط سیاه = گسل‌های فعال GEM")