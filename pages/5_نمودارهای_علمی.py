# pages/5_نمودارهای_علمی.py
import streamlit as st
import os
from pathlib import Path

st.set_page_config(
    page_title="نمودارهای علمی",
    page_icon="📊",
    layout="wide",
)

st.title("📊 نمودارهای علمی (سبک کتاب)")

st.markdown(
    """
این بخش نمودارهای **استاتیک و آماده گزارش/مقاله** را با `matplotlib` می‌سازد:
- هیستوگرام و توزیع تجمعی بزرگی
- Boxplot
- ماتریس همبستگی
- نمودارهای باینری (Magnitude vs Depth و ...)
- Pairplot چندمتغیره

> برای ساخت نمودارها باید داده از صفحه اصلی بارگذاری شده باشد.
"""
)

# ---------- بررسی داده ----------
if "df" not in st.session_state:
    st.warning("ابتدا به **صفحه اصلی** بروید تا داده‌ها بارگذاری شوند.")
    st.stop()

df = st.session_state["df"]

if df is None or df.empty:
    st.error("داده خالی است.")
    st.stop()

st.info(f"تعداد رکوردهای موجود: **{len(df)}** زلزله")

# ---------- پیشوند ذخیره ----------
SAVE_PREFIX = "streamlit_eq"
OUTPUT_DIR = Path(".")  # همان پوشه پروژه

# لیست فایل‌هایی که scientific_plots می‌سازد
EXPECTED_FILES = [
    f"{SAVE_PREFIX}_hist_magnitude.png",
    f"{SAVE_PREFIX}_hist_cumulative.png",
    f"{SAVE_PREFIX}_boxplots.png",
    f"{SAVE_PREFIX}_correlation.png",
    f"{SAVE_PREFIX}_mag_vs_depth.png",
    f"{SAVE_PREFIX}_spatial_scatter.png",
    f"{SAVE_PREFIX}_strong_vs_weak.png",
    f"{SAVE_PREFIX}_pairplot.png",
]


def files_exist():
    return all((OUTPUT_DIR / f).exists() for f in EXPECTED_FILES)


# ---------- دکمه ساخت ----------
col1, col2 = st.columns([1, 3])
with col1:
    generate = st.button("ساخت نمودارهای علمی", type="primary")

with col2:
    if files_exist():
        st.success("نمودارهای قبلی پیدا شد. می‌توانید دوباره بسازید یا پایین ببینید.")

if generate:
    try:
        from scientific_plots import (
            plot_descriptive_stats,
            plot_binary_diagrams,
            plot_pairplot,
        )

        with st.spinner("در حال ساخت نمودارها با matplotlib ..."):
            plot_descriptive_stats(df, save_prefix=SAVE_PREFIX)
            plot_binary_diagrams(df, save_prefix=SAVE_PREFIX)
            plot_pairplot(df, save_prefix=SAVE_PREFIX)

        st.success("نمودارها با موفقیت ساخته و ذخیره شدند (DPI=300).")
        st.rerun()
    except ImportError:
        st.error(
            "فایل `scientific_plots.py` پیدا نشد. "
            "آن را در ریشه پروژه (کنار `app.py`) قرار دهید."
        )
    except Exception as e:
        st.error(f"خطا در ساخت نمودارها: {e}")

# ---------- نمایش نمودارها ----------
st.markdown("---")
st.subheader("نمایش نمودارها")

if not files_exist():
    st.warning("هنوز نموداری ساخته نشده. دکمه **ساخت نمودارهای علمی** را بزنید.")
else:
    tabs = st.tabs(
        [
            "هیستوگرام",
            "تجمعی",
            "Boxplot",
            "همبستگی",
            "Mag vs Depth",
            "پراکندگی فضایی",
            "قوی / ضعیف",
            "Pairplot",
        ]
    )

    images = [
        (f"{SAVE_PREFIX}_hist_magnitude.png", "توزیع بزرگی زلزله‌ها"),
        (f"{SAVE_PREFIX}_hist_cumulative.png", "توزیع تجمعی بزرگی"),
        (f"{SAVE_PREFIX}_boxplots.png", "Boxplot بزرگی و عمق"),
        (f"{SAVE_PREFIX}_correlation.png", "ماتریس همبستگی"),
        (f"{SAVE_PREFIX}_mag_vs_depth.png", "Magnitude در برابر Depth"),
        (f"{SAVE_PREFIX}_spatial_scatter.png", "پراکندگی جغرافیایی"),
        (f"{SAVE_PREFIX}_strong_vs_weak.png", "زلزله‌های قوی در برابر ضعیف"),
        (f"{SAVE_PREFIX}_pairplot.png", "روابط چندمتغیره (Pairplot)"),
    ]

    for tab, (filename, caption) in zip(tabs, images):
        with tab:
            path = OUTPUT_DIR / filename
            if path.exists():
                st.image(str(path), caption=caption, use_container_width=True)
                with open(path, "rb") as f:
                    st.download_button(
                        label=f"دانلود {filename}",
                        data=f,
                        file_name=filename,
                        mime="image/png",
                        key=f"dl_{filename}",
                    )
            else:
                st.warning(f"فایل {filename} پیدا نشد.")

st.markdown("---")
st.caption(
    "این نمودارها با matplotlib و سبک کتاب "
    "«Introduction to Python in Earth Science Data Analysis» ساخته می‌شوند."
)