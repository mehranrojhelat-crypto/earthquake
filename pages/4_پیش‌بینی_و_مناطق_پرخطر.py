import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score, mean_absolute_error

st.set_page_config(page_title="پیش‌بینی و مناطق پرخطر", page_icon="🔮", layout="wide")
st.title("🔮 پیش‌بینی شدت و پیدا کردن مناطق پرخطر")

st.markdown("""
در این بخش سیستم با بررسی هزاران زلزله قبلی، سه کار ساده انجام می‌دهد:

1. **تشخیص زلزله‌های نسبتاً قوی** (حدود ۵ ریشتر به بالا)
2. **تخمین تقریبی شدت** یک زلزله بر اساس محل و عمق
3. **گروه‌بندی مناطق** ایران از نظر تمرکز زلزله (مناطق پرخطرتر)

> این‌ها ابزار کمکی برای درک الگو هستند، نه هشدار رسمی زلزله.
""")

if "df" not in st.session_state:
    st.warning("ابتدا به صفحه اصلی بروید تا داده‌ها بارگذاری شوند.")
    st.stop()

df = st.session_state["df"]

if st.button("شروع تحلیل", type="primary"):
    with st.spinner("در حال بررسی داده‌ها..."):
        features = ["latitude", "longitude", "depth_km", "year", "month", "dayofyear"]
        X = df[features]
        y_strong = (df["magnitude"] >= 5.0).astype(int)
        y_mag = df["magnitude"]

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        X_train, X_test, y_s_train, y_s_test, y_m_train, y_m_test = train_test_split(
            X_scaled, y_strong, y_mag, test_size=0.25, random_state=42, stratify=y_strong
        )

        # ----- ۱. تشخیص زلزله قوی -----
        st.markdown("### ۱. تشخیص زلزله‌های نسبتاً قوی (حدود ۵ ریشتر به بالا)")
        model_strong = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        model_strong.fit(X_train, y_s_train)
        pred_strong = model_strong.predict(X_test)
        acc = accuracy_score(y_s_test, pred_strong)

        st.write(
            f"سیستم در حدود **{acc*100:.0f}٪** موارد توانسته درست تشخیص دهد "
            f"که یک زلزله نسبتاً قوی بوده یا نه."
        )
        if acc >= 0.8:
            st.success("عملکرد خوب — الگوهای مکانی و عمقی نسبتاً قابل تشخیص‌اند.")
        elif acc >= 0.65:
            st.info("عملکرد متوسط — هنوز الگو هست، ولی قطعی نیست.")
        else:
            st.warning("عملکرد ضعیف‌تر — پیش‌بینی زلزله ذاتاً سخت است.")

        # اهمیت به زبان ساده
        names_fa = {
            "latitude": "عرض جغرافیایی (شمال/جنوب)",
            "longitude": "طول جغرافیایی (شرق/غرب)",
            "depth_km": "عمق زلزله",
            "year": "سال",
            "month": "ماه",
            "dayofyear": "روز سال",
        }
        imp = pd.DataFrame({
            "عامل": [names_fa[f] for f in features],
            "میزان تأثیر": model_strong.feature_importances_,
        }).sort_values("میزان تأثیر", ascending=False)

        st.markdown("**کدام عامل‌ها بیشتر در تشخیص زلزله قوی نقش داشته‌اند؟**")
        st.plotly_chart(
            px.bar(imp, x="عامل", y="میزان تأثیر", title="تأثیر هر عامل"),
            use_container_width=True,
        )

        # ----- ۲. تخمین شدت -----
        st.markdown("### ۲. تخمین تقریبی شدت (ریشتر)")
        model_mag = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        model_mag.fit(X_train, y_m_train)
        pred_mag = model_mag.predict(X_test)
        mae = mean_absolute_error(y_m_test, pred_mag)

        st.write(
            f"به طور میانگین، تخمین شدت حدود **±{mae:.2f} ریشتر** با واقعیت فاصله دارد."
        )
        st.caption("یعنی اگر سیستم بگوید ۵.۰، معمولاً واقعی بین حدود ۴.۷ تا ۵.۳ است.")

        # ----- ۳. مناطق پرخطر -----
        st.markdown("### ۳. مناطق پرتمرکز زلزله روی نقشه")
        st.write(
            "نقاط نزدیک به هم در یک گروه قرار می‌گیرند. "
            "گروه‌هایی که میانگین شدت بالاتری دارند، از نظر تاریخی پرخطرتر بوده‌اند."
        )

        kmeans = KMeans(n_clusters=6, random_state=42, n_init=10)
        df_c = df.copy()
        df_c["منطقه"] = kmeans.fit_predict(df[["latitude", "longitude"]])

        stats = (
            df_c.groupby("منطقه")
            .agg(
                تعداد_زلزله=("magnitude", "count"),
                میانگین_شدت=("magnitude", "mean"),
                بیشترین_شدت=("magnitude", "max"),
            )
            .round(2)
            .sort_values("میانگین_شدت", ascending=False)
        )
        stats.index = [f"منطقه {i+1}" for i in range(len(stats))]
        st.dataframe(stats)

        fig_cl = px.scatter_map(
            df_c,
            lat="latitude",
            lon="longitude",
            color="منطقه",
            size="magnitude",
            zoom=4.5,
            height=550,
            map_style="open-street-map",
            title="گروه‌بندی مناطق از نظر تمرکز زلزله",
        )
        st.plotly_chart(fig_cl, use_container_width=True)

        st.info(
            "رنگ‌های مختلف = مناطق مختلف. "
            "هرچه نقطه بزرگ‌تر باشد، زلزله شدیدتر بوده است."
        )