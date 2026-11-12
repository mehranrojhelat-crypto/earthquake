# models/evaluation.py
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    mean_absolute_error,
    r2_score,
)

def temporal_train_test_split(df: pd.DataFrame, time_col: str = "time", test_ratio: float = 0.25):
    """تقسیم بر اساس زمان: داده‌های قدیمی‌تر = train، جدیدتر = test"""
    work = df.sort_values(time_col).reset_index(drop=True)
    split_idx = int(len(work) * (1 - test_ratio))
    train_df = work.iloc[:split_idx].copy()
    test_df = work.iloc[split_idx:].copy()
    return train_df, test_df

def classification_report_dict(y_true, y_pred) -> dict:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }

def regression_report_dict(y_true, y_pred) -> dict:
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }

def majority_baseline_accuracy(y_train, y_test) -> float:
    """Baseline: همیشه کلاس غالب train را پیش‌بینی کن"""
    majority = int(np.round(np.mean(y_train)))  # برای 0/1
    # دقیق‌تر:
    vals, counts = np.unique(y_train, return_counts=True)
    majority = vals[np.argmax(counts)]
    pred = np.full_like(y_test, majority)
    return float(accuracy_score(y_test, pred))