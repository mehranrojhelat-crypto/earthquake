from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from models.evaluation import temporal_train_test_split, regression_report_dict

FEATURE_COLS = ["latitude", "longitude", "depth_km", "dist_to_fault_km"]

def train_magnitude_regressors(df, test_ratio: float = 0.25):
    work = df.dropna(subset=FEATURE_COLS + ["magnitude", "time"]).copy()
    train_df, test_df = temporal_train_test_split(work, test_ratio=test_ratio)

    X_train = train_df[FEATURE_COLS]
    X_test = test_df[FEATURE_COLS]
    y_train = train_df["magnitude"]
    y_test = test_df["magnitude"]

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    rf = RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
    )
    lr = LinearRegression()

    rf.fit(X_train_s, y_train)
    lr.fit(X_train_s, y_train)

    rf_pred = rf.predict(X_test_s)
    lr_pred = lr.predict(X_test_s)

    # baseline: میانگین train
    mean_pred = [float(y_train.mean())] * len(y_test)

    return {
        "n_train": len(train_df),
        "n_test": len(test_df),
        "baseline_mae": regression_report_dict(y_test, mean_pred)["mae"],
        "random_forest": regression_report_dict(y_test, rf_pred),
        "linear_regression": regression_report_dict(y_test, lr_pred),
        "feature_importance": dict(zip(FEATURE_COLS, rf.feature_importances_.tolist())),
    }