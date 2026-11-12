# models/classification.py
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from models.evaluation import (
    temporal_train_test_split,
    classification_report_dict,
    majority_baseline_accuracy,
)

FEATURE_COLS = ["latitude", "longitude", "depth_km", "dist_to_fault_km"]

def train_strong_earthquake_models(df, threshold: float = 5.0, test_ratio: float = 0.25):
    """
    مسئله: با داشتن موقعیت، عمق و فاصله از گسل یک رویداد ثبت‌شده،
    آیا magnitude آن >= threshold بوده است؟

    این پیش‌بینی وقوع آینده نیست؛ تحلیل الگوی رویدادهای رخ‌داده است.
    """
    work = df.dropna(subset=FEATURE_COLS + ["magnitude", "time"]).copy()
    work["is_strong"] = (work["magnitude"] >= threshold).astype(int)

    train_df, test_df = temporal_train_test_split(work, test_ratio=test_ratio)

    X_train = train_df[FEATURE_COLS]
    X_test = test_df[FEATURE_COLS]
    y_train = train_df["is_strong"]
    y_test = test_df["is_strong"]

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    # مدل‌ها
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )
    logreg = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)

    rf.fit(X_train_s, y_train)
    logreg.fit(X_train_s, y_train)

    rf_pred = rf.predict(X_test_s)
    lr_pred = logreg.predict(X_test_s)

    results = {
        "n_train": len(train_df),
        "n_test": len(test_df),
        "train_time_range": (str(train_df["time"].min()), str(train_df["time"].max())),
        "test_time_range": (str(test_df["time"].min()), str(test_df["time"].max())),
        "positive_rate_train": float(y_train.mean()),
        "positive_rate_test": float(y_test.mean()),
        "baseline_accuracy": majority_baseline_accuracy(y_train.values, y_test.values),
        "random_forest": classification_report_dict(y_test, rf_pred),
        "logistic_regression": classification_report_dict(y_test, lr_pred),
        "feature_importance": dict(zip(FEATURE_COLS, rf.feature_importances_.tolist())),
        "models": {"rf": rf, "logreg": logreg, "scaler": scaler},
        "y_test": y_test,
        "rf_pred": rf_pred,
        "lr_pred": lr_pred,
    }
    return results