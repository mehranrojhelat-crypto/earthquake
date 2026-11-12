# components/map.py
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from config import MAG_COLORS

def magnitude_color(mag: float) -> str:
    if mag < 4.5:
        return MAG_COLORS["low"]
    if mag < 5.5:
        return MAG_COLORS["moderate"]
    if mag < 6.5:
        return MAG_COLORS["strong"]
    return MAG_COLORS["major"]

def build_earthquake_map(
    df: pd.DataFrame,
    faults: dict | None = None,
    show_faults: bool = True,
    center_lat: float = 32.5,
    center_lon: float = 54.0,
    zoom: float = 4.5,
    height: int = 700,
) -> go.Figure:
    """ساخت نقشه تعاملی زلزله + گسل"""
    fig = go.Figure()

    if df is not None and not df.empty:
        colors = [magnitude_color(m) for m in df["magnitude"]]
        sizes = np.clip(df["magnitude"] ** 2 * 1.8, 6, 28)

        fig.add_trace(
            go.Scattermap(
                lat=df["latitude"],
                lon=df["longitude"],
                mode="markers",
                marker=dict(
                    size=sizes,
                    color=colors,
                    opacity=0.85,
                ),
                text=df["place"],
                customdata=np.stack(
                    [
                        df["magnitude"].round(1),
                        df["depth_km"].round(1) if "depth_km" in df.columns else np.full(len(df), np.nan),
                        df["time"].astype(str),
                    ],
                    axis=-1,
                ),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "بزرگی: %{customdata[0]}<br>"
                    "عمق: %{customdata[1]} km<br>"
                    "زمان: %{customdata[2]}<extra></extra>"
                ),
                name="زلزله‌ها",
            )
        )

    if show_faults and faults and faults.get("features"):
        for feat in faults["features"]:
            geom = feat.get("geometry") or {}
            name = (feat.get("properties") or {}).get("name", "گسل")
            gtype = geom.get("type")
            coords = geom.get("coordinates", [])

            lines = []
            if gtype == "LineString":
                lines = [coords]
            elif gtype == "MultiLineString":
                lines = coords

            for line in lines:
                if not line:
                    continue
                lons = [p[0] for p in line]
                lats = [p[1] for p in line]
                fig.add_trace(
                    go.Scattermap(
                        lat=lats,
                        lon=lons,
                        mode="lines",
                        line=dict(width=1.5, color="#94A3B8"),
                        name=name,
                        hoverinfo="name",
                        showlegend=False,
                    )
                )

    fig.update_layout(
        map_style="carto-darkmatter",   # ظاهر حرفه‌ای‌تر
        map=dict(center=dict(lat=center_lat, lon=center_lon), zoom=zoom),
        height=height,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=0.01),
    )
    return fig