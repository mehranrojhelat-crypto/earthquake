import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score, mean_absolute_error

st.set_page_config(page_title="تحلیل الگو و مناطق پرتمرکز", page_icon="🔮", layout="wide")
st.title("🔮 تحلیل الگو، زلزله‌های قوی و مناطق پرتمرکز")

st.markdown("""
این بخش سه کار انجام می‌دهد (بر اساس داده‌های تاریخی، نه هشدار رسمی):

1. **تشخیص زلزله‌های نسبتاً قوی** (حدود ۵ ریشتر به بالا)
2. **تخمین تقریبی شدت** بر اساس محل، عمق و فاصله از گسل
3. **گروه‌بندی مناطق** از نظر تمرکز زلزله

> این ابزار کمکی برای درک الگو است، نه پیش‌بینی دقیق زلزله آینده.
""")

if "df" not in st.session_state:
    st.warning("ابتدا به صفحه اصلی بروید تا داده‌ها بارگذاری شوند.")
    st.stop()

df = st.session_state["df"].copy()
faults = st.session_state.get("faults", {"features": []})


# ---------- تابع فاصله تا نزدیک‌ترین گسل (تقریبی با نقاط گسل) ----------
def haversine_km(lat1, lon1, lat2, lon2):
    """فاصله تقریبی روی کره زمین (کیلومتر)"""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))


def compute_distance_to_nearest_fault(df, faults, max_points=8000):
    """
    برای هر زلزله، حداقل فاصله تا نزدیک‌ترین نقطه روی گسل‌ها را حساب می‌کند.
    برای سرعت، تعداد نقاط گسل را محدود می‌کنیم.
    """
    fault_lats, fault_lons = [], []

    for feat in faults.get("features", []):
        geom = feat.get("geometry")
        if not geom:
            continue
        lines = []
        if geom["type"] == "LineString":
            lines = [geom["coordinates"]]
        elif geom["type"] == "MultiLineString":
            lines = geom["coordinates"]

        for line in lines:
            # هر چند نقطه یک‌بار نمونه‌برداری (برای سرعت)
            step = max(1, len(line) // 30)
            for p in line[::step]:
                fault_lons.append(p[0])
                fault_lats.append(p[1])

    if not fault_lats:
        # اگر گسلی نبود، فاصله را NaN می‌گذاریم
        df["dist_to_fault_km"] = np.nan
        return df

    fault_lats = np.array(fault_lats[:max_points])
    fault_lons = np.array(fault_lons[:max_points])

    distances = []
    eq_lats = df["latitude"].values
    eq_lons = df["longitude"].values

    # برای سرعت: هر زلزله را با همه نقاط گسل مقایسه می‌کنیم (قابل قبول برای چند هزار نقطه)
    for lat, lon in zip(eq_lats, eq_lons):
        d = haversine_km(lat, lon, fault_lats, fault_lons)
        distances.append(np.min(d))

    df["dist_to_fault_km"] = distances
    return df


# ---------- دکمه شروع ----------
if st.button("شروع تحلیل (با فاصله تا گسل)", type="primary"):
    with st.spinner("در حال محاسبه فاصله تا گسل و آموزش مدل‌ها..."):
        df = compute_distance_to_nearest_fault(df, faults)

        # ویژگی‌ها (حالا فاصله تا گسل هم هست)
        features = ["latitude", "longitude", "depth_km", "year", "month", "dayofyear", "dist_to_fault_km"]
        # اگر بعضی فاصله‌ها NaN باشند، آن‌ها را حذف یا پر می‌کنیم
        df_model = df.dropna(subset=features + ["magnitude"]).copy()

        X = df_model[features]
        y_strong = (df_model["magnitude"] >= 5.0).astype(int)
        y_mag = df_model["magnitude"]

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        X_train, X_test, y_s_train, y_s_test, y_m_train, y_m_test = train_test_split(
            X_scaled, y_strong, y_mag, test_size=0.25, random_state=42, stratify=y_strong
        )

        # ----- ۱. تشخیص زلزله قوی -----
        st.markdown("### ۱. تشخیص زلزله‌های نسبتاً قوی (حدود ۵ ریشتر به بالا)")
        model_strong = RandomForestClassifier(n_estimators=120, random_state=42, n_jobs=-1)
        model_strong.fit(X_train, y_s_train)
        pred_strong = model_strong.predict(X_test)
        acc = accuracy_score(y_s_test, pred_strong)

        st.write(
            f"سیستم در حدود **{acc*100:.0f}٪** موارد توانسته درست تشخیص دهد "
            f"که یک زلزله نسبتاً قوی بوده یا نه."
        )
        if acc >= 0.8:
            st.success("عملکرد خوب — الگوهای مکانی، عمق و فاصله از گسل نسبتاً قابل تشخیص‌اند.")
        elif acc >= 0.65:
            st.info("عملکرد متوسط — هنوز الگو هست، ولی قطعی نیست.")
        else:
            st.warning("عملکرد ضعیف‌تر — پیش‌بینی زلزله ذاتاً سخت است.")

        names_fa = {
            "latitude": "عرض جغرافیایی",
            "longitude": "طول جغرافیایی",
            "depth_km": "عمق (کیلومتر)",
            "year": "سال",
            "month": "ماه",
            "dayofyear": "روز سال",
            "dist_to_fault_km": "فاصله تا نزدیک‌ترین گسل (کیلومتر)",
        }
        imp = pd.DataFrame({
            "عامل": [names_fa[f] for f in features],
            "میزان تأثیر": model_strong.feature_importances_,
        }).sort_values("میزان تأثیر", ascending=False)

        st.markdown("**کدام عامل‌ها بیشتر در تشخیص زلزله قوی نقش داشته‌اند؟**")
        st.plotly_chart(
            px.bar(imp, x="عامل", y="میزان تأثیر",
                   color="میزان تأثیر", color_continuous_scale="YlOrRd",
                   title="اهمیت ویژگی‌ها"),
            use_container_width=True,
        )

        # ----- ۲. تخمین شدت -----
        st.markdown("### ۲. تخمین تقریبی شدت (ریشتر)")
        model_mag = RandomForestRegressor(n_estimators=120, random_state=42, n_jobs=-1)
        model_mag.fit(X_train, y_m_train)
        pred_mag = model_mag.predict(X_test)
        mae = mean_absolute_error(y_m_test, pred_mag)

        st.write(
            f"به طور میانگین، تخمین شدت حدود **±{mae:.2f} ریشتر** با واقعیت فاصله دارد."
        )
        st.caption("یعنی اگر سیستم بگوید ۵.۰، معمولاً واقعی بین حدود ۴.۷ تا ۵.۳ است.")

        # ----- ۳. مناطق پرتمرکز (خوشه‌بندی با رنگ واضح) -----
        st.markdown("### ۳. مناطق پرتمرکز زلزله روی نقشه")
        st.write(
            "نقاط نزدیک به هم در یک گروه قرار می‌گیرند. "
            "گروه‌هایی که میانگین شدت بالاتری دارند، از نظر تاریخی پرتمرکزتر بوده‌اند."
        )

        kmeans = KMeans(n_clusters=6, random_state=42, n_init=10)
        df_c = df_model.copy()
        df_c["منطقه"] = kmeans.fit_predict(df_c[["latitude", "longitude"]])
        # برچسب خوانا
        df_c["منطقه_برچسب"] = df_c["منطقه"].apply(lambda x: f"منطقه {x+1}")

        stats = (
            df_c.groupby("منطقه_برچسب")
            .agg(
                تعداد_زلزله=("magnitude", "count"),
                میانگین_شدت=("magnitude", "mean"),
                بیشترین_شدت=("magnitude", "max"),
                میانگین_فاصله_گسل=("dist_to_fault_km", "mean"),
            )
            .round(2)
            .sort_values("میانگین_شدت", ascending=False)
        )
        st.dataframe(stats)

        # رنگ‌های واضح و متفاوت (نه همه آبی)
        color_sequence = [
            "#e41a1c",  # قرمز
            "#377eb8",  # آبی
            "#4daf4a",  # سبز
            "#984ea3",  # بنفش
            "#ff7f00",  # نارنجی
            "#a65628",  # قهوه‌ای
        ]

        fig_cl = px.scatter_map(
            df_c,
            lat="latitude",
            lon="longitude",
            color="منطقه_برچسب",
            size="magnitude",
            size_max=18,
            color_discrete_sequence=color_sequence,
            zoom=4.5,
            height=580,
            map_style="open-street-map",
            title="گروه‌بندی مناطق از نظر تمرکز زلزله (رنگ‌های متمایز)",
            hover_data={
                "magnitude": ":.1f",
                "depth_km": ":.1f",
                "dist_to_fault_km": ":.1f",
                "منطقه_برچسب": True,
            },
        )
        st.plotly_chart(fig_cl, use_container_width=True)

        st.info(
            "هر رنگ = یک منطقه جدا. "
            "اندازه نقطه = شدت زلزله. "
            "در جدول بالا می‌توانید میانگین فاصله از گسل هر منطقه را هم ببینید."
        )

        # آمار ساده فاصله از گسل
        st.markdown("### خلاصه فاصله تا گسل")
        st.write(
            f"میانگین فاصله زلزله‌ها تا نزدیک‌ترین گسل: "
            f"**{df_model['dist_to_fault_km'].mean():.1f} کیلومتر**"
        )
        st.write(
            f"زلزله‌های ≥ ۵ ریشتر به‌طور میانگین "
            f"**{df_model.loc[df_model['magnitude'] >= 5, 'dist_to_fault_km'].mean():.1f} کیلومتر** "
            f"از گسل فاصله داشته‌اند."
        )