# components/metrics.py
import streamlit as st
import pandas as pd

def show_summary_metrics(df: pd.DataFrame, faults: dict, start_time: str, end_time: str):
    """کارت‌های آماری بالای داشبورد"""
    if df is None or df.empty:
        st.warning("داده‌ای برای نمایش وجود ندارد.")
        return

    last_24h = df[df["time"] >= (pd.Timestamp.now(tz="UTC") - pd.Timedelta(hours=24))]
    strongest = df.loc[df["magnitude"].idxmax()]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("کل زلزله‌ها", f"{len(df):,}")
    c2.metric("۲۴ ساعت اخیر", f"{len(last_24h):,}")
    c3.metric("قوی‌ترین رویداد", f"M {strongest['magnitude']:.1f}")
    c4.metric("گسل‌های نمایش‌داده‌شده", len(faults.get("features", [])))

    st.caption(f"بازه داده: {start_time} → {end_time}")