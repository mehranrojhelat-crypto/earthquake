# components/header.py
import streamlit as st
import pandas as pd

def render_header(last_update: pd.Timestamp | None = None):
    update_txt = "—"
    if last_update is not None:
        update_txt = last_update.strftime("%Y-%m-%d %H:%M UTC")

    st.markdown(
        f"""
        <div class="app-header">
            <h1>🌍 Earthquake Intelligence Platform</h1>
            <p>مانیتورینگ و تحلیل زلزله ایران · آخرین به‌روزرسانی: {update_txt}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )