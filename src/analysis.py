"""NumPy-only standardization, K-Means, and 2D PCA.

Clustering is a precompute step for interpretable space-type labels.
It is not used as a live recommender and is never run on the Streamlit request path.
PCA coordinates are for analysis / portfolio plots only — not the schematic map.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.synthetic import ARCHETYPE_CENTERS

FEATURES = [
    "quiet",
    "comfort",
    "wifi",
    "power",
    "discussion",
    "lighting",
    "low_crowding",
]

ARCHETYPE_ORDER = (
    "Deep Focus",
    "Quick Work",
    "Social Study",
    "Group Collaboration",
)


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["low_crowding"] = 6.0 - out["crowding"].astype(float)
    return out


def feature_matrix(df: pd.DataFrame) -> np.ndarray:
    work = add_derived_features(df)
    return work[FEATURES].to_numpy(dtype=float)


def standardize(X: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mu = X.mean(axis=0)
    sigma = X.std(axis=0) + 1e-8
    z = (X - mu) / sigma
    return z, mu, sigma


def kmeans(
    z: np.ndarray,
    k: int = 4,
    seed: int = 42,
    max_iter: int = 100,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    centers = z[rng.choice(len(z), size=k, replace=False)].copy()
    labels = np.zeros(len(z), dtype=int)

    for _ in range(max_iter):
        dist2 = ((z[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        labels = dist2.argmin(axis=1)
        new_centers = np.vstack(
            [
                z[labels == i].mean(axis=0) if np.any(labels == i) else centers[i]
                for i in range(k)
            ]
        )
        if np.allclose(new_centers, centers, atol=1e-5):
            break
        centers = new_centers

    return labels, centers


def pca_2d(z: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    _u, s, vt = np.linalg.svd(z, full_matrices=False)
    coords = z @ vt[:2].T
    explained = (s[:2] ** 2) / (s ** 2).sum()
    return coords, explained


def _archetype_matrix() -> np.ndarray:
    rows = []
    for name in ARCHETYPE_ORDER:
        c = ARCHETYPE_CENTERS[name]
        rows.append(
            [
                c["quiet"],
                c["comfort"],
                c["wifi"],
                c["power"],
                c["discussion"],
                c["lighting"],
                6.0 - c["crowding"],
            ]
        )
    return np.asarray(rows, dtype=float)


def name_clusters(centers: np.ndarray, mu: np.ndarray, sigma: np.ndarray) -> list[str]:
    """Map numeric K-Means centers onto the nearest unused archetype name."""
    archetype_z = (_archetype_matrix() - mu) / sigma
    assigned: list[str] = []
    used: set[str] = set()
    for center in centers:
        dist2 = ((archetype_z - center) ** 2).sum(axis=1)
        for idx in np.argsort(dist2):
            name = ARCHETYPE_ORDER[int(idx)]
            if name not in used:
                used.add(name)
                assigned.append(name)
                break
    return assigned


def assign_clusters_and_pca(
    df: pd.DataFrame,
    k: int = 4,
    seed: int = 42,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Attach named cluster labels and PCA coords. Runtime should only read the result."""
    x = feature_matrix(df)
    z, mu, sigma = standardize(x)
    labels, centers = kmeans(z, k=k, seed=seed)
    coords, explained = pca_2d(z)
    cluster_names = name_clusters(centers, mu, sigma)

    out = df.copy()
    out["cluster"] = [cluster_names[int(i)] for i in labels]
    out["pca_x"] = np.round(coords[:, 0], 4)
    out["pca_y"] = np.round(coords[:, 1], 4)

    counts = {name: int((out["cluster"] == name).sum()) for name in cluster_names}
    meta: dict[str, Any] = {
        "seed": seed,
        "k": k,
        "features": FEATURES,
        "mu": [round(float(v), 6) for v in mu],
        "sigma": [round(float(v), 6) for v in sigma],
        "pca_explained_variance": [round(float(v), 6) for v in explained],
        "cluster_names": cluster_names,
        "cluster_counts": counts,
        "note": "Clusters and PCA are precomputed. PCA is not geographic. Data are synthetic.",
    }
    return out, meta
