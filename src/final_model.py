"""The selected model (workspace Section 6.3) saved as one file, so the app loads it instead of training it.

    python src/final_model.py        # fits the pipeline on the training days and writes models/heatcast_random_forest.joblib

The file holds the whole pipeline: make_preprocess(scale=False) (the city as 16 yes/no columns) + the Random Forest of
notebooks/03_random_forest.ipynb (depth 12, 5 days per leaf, balanced class weights, 500 trees, random state 42). It is the
same model that notebooks/05_final_test.ipynb scored once on the test days; tests/test_app.py checks that the saved file
gives exactly those test results. Fitting takes a few seconds and only uses the training days (2021-01-01 to 2024-12-27).
Load the file with the scikit-learn version in requirements.txt.
"""
from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline

import common as C

MODEL_FILE = C.ROOT / "models" / "heatcast_random_forest.joblib"
MODEL_CONFIG = dict(n_estimators=500, max_depth=12, min_samples_leaf=5, class_weight="balanced",
                    random_state=C.RANDOM_STATE, n_jobs=-1)


def build_model(train: pd.DataFrame, **overrides):
    """make_preprocess(scale=False) + Random Forest, fitted on the training days."""
    rf = RandomForestClassifier(**{**MODEL_CONFIG, **overrides})
    return make_pipeline(C.make_preprocess(scale=False), rf).fit(train[C.FEATURES], train[C.TARGET])


def save_model(model, path: Path = MODEL_FILE) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path, compress=3)          # about 10 MB instead of 37 MB
    return path


def load_model(path: Path = MODEL_FILE):
    return joblib.load(path)


if __name__ == "__main__":
    train, _ = C.split_train_test(C.load_data())
    path = save_model(build_model(train))
    print(f"saved {path.relative_to(C.ROOT)} ({path.stat().st_size / 1e6:.1f} MB), trained on {len(train):,} rows "
          f"({train['Date'].min().date()} to {train['Date'].max().date()})")
