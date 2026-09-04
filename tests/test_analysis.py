"""Phase 2: NumPy K-Means / PCA — determinism, no NaN, four non-empty clusters."""

import numpy as np

from src.analysis import (
    assign_clusters_and_pca,
    feature_matrix,
    kmeans,
    pca_2d,
    standardize,
)
from src.synthetic import build_synthetic_dataset


def _standardized(seed: int = 42):
    df = build_synthetic_dataset(seed=seed)
    x = feature_matrix(df)
    return standardize(x)


def test_standardize_zero_mean_unit_scale():
    z, _mu, _sigma = _standardized()
    assert np.isfinite(z).all()
    np.testing.assert_allclose(z.mean(axis=0), 0.0, atol=1e-10)
    np.testing.assert_allclose(z.std(axis=0), 1.0, atol=1e-6)


def test_kmeans_four_nonempty_clusters():
    z, _mu, _sigma = _standardized()
    labels, centers = kmeans(z, k=4, seed=42)
    assert centers.shape == (4, z.shape[1])
    unique, counts = np.unique(labels, return_counts=True)
    assert set(unique.tolist()) == {0, 1, 2, 3}
    assert np.all(counts > 0)


def test_kmeans_is_deterministic():
    z, _mu, _sigma = _standardized()
    labels_a, centers_a = kmeans(z, k=4, seed=42)
    labels_b, centers_b = kmeans(z, k=4, seed=42)
    np.testing.assert_array_equal(labels_a, labels_b)
    np.testing.assert_allclose(centers_a, centers_b)


def test_pca_shape_finite_and_deterministic():
    z, _mu, _sigma = _standardized()
    coords_a, explained_a = pca_2d(z)
    coords_b, explained_b = pca_2d(z)
    assert coords_a.shape == (18, 2)
    assert explained_a.shape == (2,)
    assert np.isfinite(coords_a).all()
    assert np.isfinite(explained_a).all()
    assert not np.isnan(coords_a).any()
    np.testing.assert_allclose(coords_a, coords_b)
    np.testing.assert_allclose(explained_a, explained_b)
    assert float(explained_a.sum()) <= 1.0 + 1e-8


def test_assign_clusters_names_four_nonempty():
    df = build_synthetic_dataset(seed=42)
    out, meta = assign_clusters_and_pca(df, k=4, seed=42)
    assert out["cluster"].nunique() == 4
    assert set(out["cluster"]) <= {
        "Deep Focus",
        "Quick Work",
        "Social Study",
        "Group Collaboration",
    }
    assert all(count > 0 for count in meta["cluster_counts"].values())
    assert out["pca_x"].notna().all()
    assert out["pca_y"].notna().all()
    assert np.isfinite(out["pca_x"].to_numpy()).all()
    assert np.isfinite(out["pca_y"].to_numpy()).all()
