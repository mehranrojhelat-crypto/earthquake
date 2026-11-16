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
    max_fault_traces: int = 80,
) -> go.Figure:
    fig = go.Figure()

    if df is not None and not df.empty:
        plot_df = df.copy()
        if len(plot_df) > 4000:
            plot_df = plot_df.sort_values("time", ascending=False).head(4000)

        colors = [magnitude_color(float(m)) for m in plot_df["magnitude"]]
        sizes = np.clip(plot_df["magnitude"].astype(float) ** 2 * 1.8, 6, 28)

        if "depth_km" in plot_df.columns:
            depth = plot_df["depth_km"].astype(float).round(1)
        else:
            depth = pd.Series([np.nan] * len(plot_df), index=plot_df.index)

        if "time" in plot_df.columns:
            times = plot_df["time"].astype(str)
        else:
            times = pd.Series([""] * len(plot_df), index=plot_df.index)

        places = plot_df["place"] if "place" in plot_df.columns else pd.Series([""] * len(plot_df))

        fig.add_trace(
            go.Scattermap(
                lat=plot_df["latitude"],
                lon=plot_df["longitude"],
                mode="markers",
                marker=dict(size=sizes, color=colors, opacity=0.85),
                text=places,
                customdata=np.stack(
                    [
                        plot_df["magnitude"].astype(float).round(1),
                        depth,
                        times,
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
        count = 0
        for feat in faults["features"]:
            if count >= max_fault_traces:
                break

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
                if not line or count >= max_fault_traces:
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
                count += 1

    fig.update_layout(
        map_style="open-street-map",
        map=dict(center=dict(lat=center_lat, lon=center_lon), zoom=zoom),
        height=height,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=0.01),
        uirevision="iran-map",
    )
    return fig