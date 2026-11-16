# components/theme.py
import streamlit as st

def apply_theme():
    st.markdown(
        """
        <style>
        /* اجبار پس‌زمینه تیره حتی اگر کاربر تم روشن بگذارد */
        html, body, [data-testid="stAppViewContainer"],
        [data-testid="stHeader"], [data-testid="stToolbar"],
        .main, .block-container {
            background-color: #0B1220 !important;
            color: #F8FAFC !important;
        }

        [data-testid="stSidebar"] {
            background-color: #0B1220 !important;
            border-right: 1px solid #1F2A44;
        }

        .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
            max-width: 1440px;
        }

        /* متن‌های عمومی */
        h1, h2, h3, h4, h5, h6, p, label, span, div {
            color: #F8FAFC;
        }
        .stMarkdown, .stCaption, .stText {
            color: #E2E8F0 !important;
        }

        /* هدر */
        .app-header {
            background: linear-gradient(90deg, #0B1220 0%, #151F30 100%);
            border: 1px solid #1F2A44;
            border-radius: 16px;
            padding: 18px 22px;
            margin-bottom: 16px;
        }
        .app-header h1 {
            margin: 0;
            color: #F8FAFC !important;
            font-size: 1.55rem;
        }
        .app-header p {
            margin: 6px 0 0 0;
            color: #94A3B8 !important;
            font-size: 0.92rem;
        }

        /* کارت متریک */
        div[data-testid="stMetric"] {
            background: #151F30 !important;
            border: 1px solid #1F2A44 !important;
            border-radius: 14px;
            padding: 12px 14px;
        }
        div[data-testid="stMetric"] label {
            color: #94A3B8 !important;
        }
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: #F8FAFC !important;
        }
        div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
            color: #93C5FD !important;
        }

        /* پنل‌ها */
        .panel-card {
            background: #151F30 !important;
            border: 1px solid #1F2A44 !important;
            border-radius: 14px;
            padding: 14px 16px;
            margin-bottom: 12px;
            color: #E2E8F0 !important;
        }
        .panel-title {
            color: #CBD5E1 !important;
            font-size: 0.9rem;
            margin-bottom: 8px;
            font-weight: 600;
        }
        .eq-item {
            border-bottom: 1px solid #1F2A44;
            padding: 8px 0;
            color: #E2E8F0 !important;
            font-size: 0.9rem;
        }
        .eq-item:last-child { border-bottom: none; }
        .mag-pill {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 999px;
            font-weight: 700;
            font-size: 0.78rem;
            margin-left: 6px;
        }
        .muted { color: #94A3B8 !important; font-size: 0.82rem; }

        /* ورودی‌ها و ویجت‌ها */
        .stSelectbox, .stSlider, .stButton, .stDataFrame {
            color: #F8FAFC !important;
        }

        /* هشدار/اینفو خواناتر */
        [data-testid="stAlert"] {
            background-color: #151F30 !important;
            color: #E2E8F0 !important;
            border: 1px solid #1F2A44 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )