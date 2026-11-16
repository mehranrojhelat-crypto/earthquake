# components/recent_list.py
import streamlit as st
import pandas as pd

def _mag_color(m: float) -> str:
    if m < 4.5:
        return "#22C55E"
    if m < 5.5:
        return "#FACC15"
    if m < 6.5:
        return "#F97316"
    return "#EF4444"

def render_recent_earthquakes(df: pd.DataFrame, n: int = 8):
    st.markdown(
        '<div class="panel-card"><div class="panel-title">آخرین زلزله‌ها</div>',
        unsafe_allow_html=True,
    )

    if df is None or df.empty:
        st.write("داده‌ای نیست.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    recent = df.sort_values("time", ascending=False).head(n)
    for _, row in recent.iterrows():
        color = _mag_color(float(row["magnitude"]))
        t = row["time"]
        if hasattr(t, "strftime"):
            t = t.strftime("%m-%d %H:%M")
        place = str(row.get("place", ""))[:40]
        st.markdown(
            f"""
            <div class="eq-item">
                <span class="mag-pill" style="background:{color}22;color:{color};border:1px solid {color}55;">
                    M {row['magnitude']:.1f}
                </span>
                {place}<br>
                <span class="muted">{t} UTC</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)