"""The three selected models side by side on the same 5 folds (workspace Section 6.2, paper Tables III to V).

    python src/compare_models.py      # about 1 minute; writes results/comparison/

Each model is the setting its notebook selected (02, 03, 04). For every fold it is fitted on the fold's training days and
checked on the fold's check block, exactly like common.cross_validate. Written files:
    fold_scores.csv       the 5 scores of common.score for every model and fold (and the "copy today" rule)
    summary.csv           mean and standard deviation over the 5 folds (paper Table III)
    confusion_matrix.csv  true level x predicted level, summed over the 5 check blocks (paper Table IV)
    per_level_scores.csv  precision, recall and F1 of every level, from the summed matrix and as the mean over the folds (paper Table V)
The test days are not used here.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from sklearn.pipeline import make_pipeline
from sklearn.utils.class_weight import compute_sample_weight

import common as C
from final_model import MODEL_CONFIG

OUT = C.ROOT / "results" / "comparison"
LEVELS = ["Not Hazardous", *C.CORE_LEVELS]          # the levels that occur in the training days

MODELS = {
    "Logistic Regression": (make_pipeline(C.make_preprocess(scale=True),
                                          LogisticRegression(C=10, class_weight=None, max_iter=1000, random_state=C.RANDOM_STATE)),
                            None),
    "Random Forest": (make_pipeline(C.make_preprocess(scale=False), RandomForestClassifier(**MODEL_CONFIG)), None),
    "Gradient Boosting": (make_pipeline(C.make_preprocess(scale=False),
                                        GradientBoostingClassifier(learning_rate=0.1, max_depth=2, n_estimators=200,
                                                                   min_samples_leaf=20, random_state=C.RANDOM_STATE)),
                          lambda y: {"gradientboostingclassifier__sample_weight": compute_sample_weight("balanced", y)}),
}


def per_level(y_true, y_pred) -> pd.DataFrame:
    p, r, f, n = precision_recall_fscore_support(y_true, y_pred, labels=LEVELS, zero_division=0)
    return pd.DataFrame({"precision": p, "recall": r, "f1": f, "true_rows": n}, index=pd.Index(LEVELS, name="level"))


def main():
    train, _ = C.split_train_test(C.load_data())
    X, y = train[C.FEATURES], train[C.TARGET]
    folds = C.make_folds(train)
    fold_rows, cms, levels_pooled, levels_mean = [], [], [], []
    guess = C.persistence_predictions(train)
    for name in ["Copy today rule", *MODELS]:
        y_all, p_all, per_fold = [], [], []
        for k, (fit_idx, check_idx) in enumerate(folds, start=1):
            if name == "Copy today rule":
                pred = guess.iloc[check_idx].to_numpy()
            else:
                model, fit_params = MODELS[name]
                m = clone(model).fit(X.iloc[fit_idx], y.iloc[fit_idx], **(fit_params(y.iloc[fit_idx]) if fit_params else {}))
                pred = m.predict(X.iloc[check_idx])
            truth = y.iloc[check_idx].to_numpy()
            fold_rows.append({"model": name, "fold": k, **C.score(truth, pred)})
            per_fold.append(per_level(truth, pred))
            y_all.append(truth)
            p_all.append(pred)
        y_all, p_all = np.concatenate(y_all), np.concatenate(p_all)
        cm = pd.DataFrame(confusion_matrix(y_all, p_all, labels=LEVELS), index=LEVELS, columns=LEVELS)
        cms.append(cm.rename_axis(index="true", columns="predicted").stack().rename("rows").reset_index().assign(model=name))
        levels_pooled.append(per_level(y_all, p_all).assign(model=name, how="summed over the 5 check blocks"))
        stacked = pd.concat(per_fold)
        levels_mean.append(stacked.groupby(level=0).mean().reindex(LEVELS).assign(model=name, how="mean over the 5 folds"))
        print(f"{name}: done")

    OUT.mkdir(parents=True, exist_ok=True)
    folds_table = pd.DataFrame(fold_rows)
    folds_table.round(4).to_csv(OUT / "fold_scores.csv", index=False)
    summary = folds_table.drop(columns="fold").groupby("model", sort=False).agg(["mean", "std"]).round(3)
    summary.columns = [f"{a}_{'sd' if b == 'std' else b}" for a, b in summary.columns]
    summary.to_csv(OUT / "summary.csv")
    pd.concat(cms)[["model", "true", "predicted", "rows"]].to_csv(OUT / "confusion_matrix.csv", index=False)
    levels = pd.concat(levels_pooled + levels_mean).reset_index()[["model", "how", "level", "precision", "recall", "f1", "true_rows"]]
    levels.round(3).to_csv(OUT / "per_level_scores.csv", index=False)
    print(summary.to_string())
    print(levels[levels["how"].str.startswith("summed")].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
