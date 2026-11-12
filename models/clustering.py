# models/clustering.py
from sklearn.cluster import KMeans
import pandas as pd

def cluster_events(df: pd.DataFrame, n_clusters: int = 6) -> pd.DataFrame:
    work = df.dropna(subset=["latitude", "longitude", "magnitude"]).copy()
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    work["cluster"] = km.fit_predict(work[["latitude", "longitude"]])
    work["cluster_label"] = work["cluster"].apply(lambda x: f"منطقه {x+1}")
    return work