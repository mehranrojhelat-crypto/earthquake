# app.py
import streamlit as st
from utils.data import fetch_earthquakes, fetch_iran_faults

st.set_page_config(
    page_title="سامانه تحلیل زلزله ایران",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🌍 سامانه تحلیل زلزله و گسل‌های ایران")
st.markdown("""
این سامانه داده‌های زلزله ایران را از **USGS** می‌گیرد، گسل‌های فعال را از **GEM** نمایش می‌دهد
و امکان آمارگیری و یادگیری ماشین را فراهم می‌کند.

از منوی سمت چپ صفحه مورد نظر را انتخاب کنید:
- 🗺️ نقشه و گسل
- 📊 آمار و نمودار
- 🤖 یادگیری ماشین
- ℹ️ درباره
""")

@st.cache_data(ttl=3600 * 24)
def load_eq():
    return fetch_earthquakes()

@st.cache_data(ttl=3600 * 24 * 7)
def load_faults():
    return fetch_iran_faults()

with st.spinner("در حال بارگذاری داده‌ها..."):
    df, start_time, end_time = load_eq()
    faults = load_faults()

# ذخیره در session تا صفحات دیگر استفاده کنند
st.session_state["df"] = df
st.session_state["faults"] = faults
st.session_state["start_time"] = start_time
st.session_state["end_time"] = end_time

col1, col2, col3 = st.columns(3)
col1.metric("تعداد زلزله", len(df))
col2.metric("بازه زمانی", f"{start_time} → {end_time}")
col3.metric("گسل فعال", len(faults.get("features", [])))

st.success("داده‌ها بارگذاری شد. از منوی کناری وارد صفحات شوید.")