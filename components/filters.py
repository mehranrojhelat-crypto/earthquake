# components/filters.py
import streamlit as st
import pandas as pd

def apply_common_filters(df: pd.DataFrame, key_prefix: str = "common") -> pd.DataFrame:
    """فیلتر زمانی و بزرگی مشترک برای صفحات مختلف"""
    if df is None or df.empty:
        return df

    work = df.copy()
    if work["time"].dt.tz is None:
        work["time"] = work["time"].dt.tz_localize("UTC")

    st.sidebar.header("فیلترها")

    time_options = {
        "۲۴ ساعت اخیر": 1,
        "۷ روز اخیر": 7,
        "۳۰ روز اخیر": 30,
        "۹۰ روز اخیر": 90,
        "۱ سال اخیر": 365,
        "همه داده‌ها": None,
    }
    time_label = st.sidebar.selectbox(
        "بازه زمانی",
        list(time_options.keys()),
        index=5,
        key=f"{key_prefix}_time",
    )
    days = time_options[time_label]

    min_mag, max_mag = st.sidebar.slider(
        "بازه بزرگی",
        4.0, 8.0, (4.0, 8.0), 0.1,
        key=f"{key_prefix}_mag",
    )

    if days is not None:
        cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=days)
        work = work[work["time"] >= cutoff]

    work = work[(work["magnitude"] >= min_mag) & (work["magnitude"] <= max_mag)]
    return work