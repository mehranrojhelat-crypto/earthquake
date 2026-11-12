import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

from utils.geo import compute_distance_to_nearest_fault
from models.classification import train_strong_earthquake_models
from models.regression import train_magnitude_regressors
from models.clustering import cluster_events
from components.theme import apply_theme
apply_theme()
st.set_page_config(page_title="تحلیل الگو", page_icon="🤖", layout="wide")
st.title("🤖 تحلیل الگوهای لرزه‌ای (آزمایشی)")

st.warning(
    """
**توجه علمی مهم**  
این بخش «سامانه هشدار یا پیش‌بینی قطعی زلزله آینده» نیست.  
مدل‌ها روی **رویدادهای ثبت‌شده** کار می‌کنند و فقط الگوهای آماری/مکانی را بررسی می‌کنند.
"""
)

if "df" not in st.session_state:
    st.warning("ابتدا به صفحه اصلی بروید تا داده‌ها بارگذاری شوند.")
    st.stop()

df = st.session_state["df"].copy()
faults = st.session_state.get("faults", {"features": []})

threshold = st.sidebar.slider("آستانه زلزله قوی (Magnitude)", 4.5, 6.0, 5.0, 0.1)
n_clusters = st.sidebar.slider("تعداد خوشه", 3, 10, 6)

if st.button("اجرای تحلیل", type="primary"):
    with st.spinner("محاسبه فاصله تا گسل و آموزش مدل‌ها..."):
        df = compute_distance_to_nearest_fault(df, faults)

        # ----- Classification -----
        st.subheader("۱) طبقه‌بندی زلزله نسبتاً قوی")
        st.caption("سؤال مدل: برای یک رویداد ثبت‌شده با موقعیت/عمق/فاصله از گسل، آیا بزرگی‌اش از آستانه بالاتر بوده؟")

        clf = train_strong_earthquake_models(df, threshold=threshold)

        st.write(
            f"Train: **{clf['n_train']:,}** رویداد "
            f"({clf['train_time_range'][0]} → {clf['train_time_range'][1]})"
        )
        st.write(
            f"Test: **{clf['n_test']:,}** رویداد "
            f"({clf['test_time_range'][0]} → {clf['test_time_range'][1]})"
        )
        st.write(f"نسبت کلاس مثبت در test: **{clf['positive_rate_test']*100:.1f}%**")
        st.write(f"Baseline (اکثریت): Accuracy = **{clf['baseline_accuracy']*100:.1f}%**")

        m1, m2 = st.columns(2)
        with m1:
            st.markdown("**Random Forest**")
            r = clf["random_forest"]
            st.metric("Accuracy", f"{r['accuracy']*100:.1f}%")
            st.metric("Precision", f"{r['precision']*100:.1f}%")
            st.metric("Recall", f"{r['recall']*100:.1f}%")
            st.metric("F1", f"{r['f1']*100:.1f}%")
        with m2:
            st.markdown("**Logistic Regression**")
            r = clf["logistic_regression"]
            st.metric("Accuracy", f"{r['accuracy']*100:.1f}%")
            st.metric("Precision", f"{r['precision']*100:.1f}%")
            st.metric("Recall", f"{r['recall']*100:.1f}%")
            st.metric("F1", f"{r['f1']*100:.1f}%")

        # Confusion matrix RF
        cm = clf["random_forest"]["confusion_matrix"]
        z = cm
        fig_cm = ff.create_annotated_heatmap(
            z,
            x=["Pred 0", "Pred 1"],
            y=["True 0", "True 1"],
            colorscale="Blues",
            showscale=False,
        )
        fig_cm.update_layout(title="Confusion Matrix — Random Forest", height=320)
        st.plotly_chart(fig_cm, use_container_width=True)

        imp = pd.DataFrame(
            {
                "ویژگی": list(clf["feature_importance"].keys()),
                "اهمیت": list(clf["feature_importance"].values()),
            }
        ).sort_values("اهمیت", ascending=False)
        st.plotly_chart(
            px.bar(imp, x="ویژگی", y="اهمیت", title="اهمیت ویژگی‌ها (RF)"),
            use_container_width=True,
        )

        # ----- Regression -----
        st.subheader("۲) رگرسیون بزرگی (تخمینی)")
        reg = train_magnitude_regressors(df)
        c1, c2, c3 = st.columns(3)
        c1.metric("Baseline MAE (میانگین)", f"{reg['baseline_mae']:.3f}")
        c2.metric("RF MAE", f"{reg['random_forest']['mae']:.3f}")
        c3.metric("Linear MAE", f"{reg['linear_regression']['mae']:.3f}")
        st.caption("اگر MAE مدل خیلی نزدیک baseline باشد، یعنی قدرت پیش‌بینی واقعی محدود است.")

        # ----- Clustering -----
        st.subheader("۳) خوشه‌بندی مناطق پرتمرکز")
        clustered = cluster_events(df, n_clusters=n_clusters)
        stats = (
            clustered.groupby("cluster_label")
            .agg(
                count=("magnitude", "count"),
                mean_mag=("magnitude", "mean"),
                max_mag=("magnitude", "max"),
                mean_dist=("dist_to_fault_km", "mean"),
            )
            .round(2)
            .sort_values("mean_mag", ascending=False)
        )
        st.dataframe(stats, use_container_width=True)

        fig = px.scatter_map(
            clustered,
            lat="latitude",
            lon="longitude",
            color="cluster_label",
            size="magnitude",
            size_max=16,
            zoom=4.5,
            height=560,
            map_style="carto-darkmatter",
        )
        st.plotly_chart(fig, use_container_width=True)

        st.info(
            "خروجی‌ها برای درک الگوهای تاریخی مفیدند. "
            "برای تصمیم‌گیری ایمنی یا هشدار عمومی به منابع رسمی تکیه کنید."
        )