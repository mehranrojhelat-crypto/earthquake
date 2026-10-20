import streamlit as st

st.set_page_config(page_title="درباره", page_icon="ℹ️", layout="wide")
st.title("ℹ️ درباره پروژه")

st.markdown("""
### منابع داده
- **زلزله‌ها**: [USGS Earthquake Hazards Program](https://earthquake.usgs.gov/)
- **گسل‌های فعال**: [GEM Global Active Faults](https://github.com/cossatot/gem-global-active-faults) (CC BY-SA)

### قابلیت‌ها
- نقشه تعاملی زلزله + گسل
- آمار توصیفی و نمودارها
- طبقه‌بندی، رگرسیون و خوشه‌بندی

### اجرا
```bash
streamlit run app.py
```

### توسعه آینده
- پیش‌بینی زمانی
- فاصله از نزدیک‌ترین گسل
- هشدار مناطق پرخطر
""")