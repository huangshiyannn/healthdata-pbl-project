"""Reproducible grouped-validation analysis for the CTG ensemble project."""
from __future__ import annotations

import hashlib
import json
import platform
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.ensemble import AdaBoostClassifier, BaggingClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, balanced_accuracy_score, confusion_matrix,
                             roc_auc_score)
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data" / "ctg" / "student"
LABELS = BASE / "data" / "ctg" / "teacher" / "locked-test-labels.csv"
OUT = BASE / "outputs" / "tables"
SEED = 1010
N_SPLITS = 5
N_STABILITY = 200
N_TEST_BOOTSTRAP = 2000
FEATURES = ["LB", "AC", "FM", "UC", "DL", "DS", "DP", "ASTV", "MSTV", "ALTV", "MLTV",
            "Width", "Min", "Max", "Nmax", "Nzeros", "Mode", "Mean", "Median", "Variance", "Tendency"]
TREE_STABILITY_MODELS = ("single_tree", "bagging", "random_forest")


def models():
    return {
        "single_tree": DecisionTreeClassifier(max_depth=4, random_state=SEED),
        "bagging": BaggingClassifier(estimator=DecisionTreeClassifier(random_state=SEED),
                                     n_estimators=100, max_features=1.0, random_state=SEED, n_jobs=1),
        "random_forest": RandomForestClassifier(n_estimators=100, max_features="sqrt", random_state=SEED, n_jobs=1),
        "adaboost": AdaBoostClassifier(n_estimators=50, random_state=SEED),
        "gradient_boosting": GradientBoostingClassifier(n_estimators=100, random_state=SEED),
        "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000, random_state=SEED)),
        "rbf_svm": make_pipeline(StandardScaler(), SVC(C=1, kernel="rbf", probability=True, random_state=SEED)),
    }


def scores(model, X):
    return model.predict_proba(X)[:, 1]


def metric_row(name, y, prob, pred, evaluation):
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {"evaluation": evaluation, "model": name, "n": len(y), "positive_n": int(np.sum(y == 1)),
            "pr_auc": average_precision_score(y, prob) if len(np.unique(y)) == 2 else np.nan,
            "roc_auc": roc_auc_score(y, prob) if len(np.unique(y)) == 2 else np.nan,
            "balanced_accuracy": balanced_accuracy_score(y, pred),
            "sensitivity": tp / (tp + fn) if tp + fn else np.nan,
            "specificity": tn / (tn + fp) if tn + fp else np.nan,
            "tn": tn, "fp": fp, "fn": fn, "tp": tp}


def check_inputs(train, valid, test_x, manifest):
    expected = ["sample_id", "recording_id", *FEATURES, "pathologic"]
    issues = []
    for name, frame in (("train", train), ("validation", valid)):
        if frame.columns.tolist() != expected:
            issues.append(f"{name}: unexpected column order or columns")
    if test_x.columns.tolist() != expected[:-1]:
        issues.append("locked-test-features: unexpected column order or columns")
    for name, frame in (("train", train), ("validation", valid), ("locked-test-features", test_x)):
        if frame.isna().any().any():
            issues.append(f"{name}: contains missing cells")
        if frame["sample_id"].duplicated().any():
            issues.append(f"{name}: duplicate sample_id")
        if not all(pd.api.types.is_numeric_dtype(frame[c]) for c in FEATURES):
            issues.append(f"{name}: nonnumeric feature")
        if not np.isfinite(frame[FEATURES].to_numpy(dtype=float)).all():
            issues.append(f"{name}: non-finite feature")
    id_sets = {"train": set(train.recording_id), "validation": set(valid.recording_id),
               "test": set(test_x.recording_id)}
    overlaps = {f"{a}_{b}": sorted(id_sets[a] & id_sets[b]) for a, b in
                (("train", "validation"), ("train", "test"), ("validation", "test"))}
    if any(overlaps.values()):
        issues.append("recording_id overlap across fixed partitions")
    for name, frame in (("train", train), ("validation", valid), ("test", test_x)):
        expected_n = manifest["splits"][name]["n"]
        expected_groups = manifest["splits"][name]["n_recordings"]
        if len(frame) != expected_n or frame.recording_id.nunique() != expected_groups:
            issues.append(f"{name}: row/group counts do not match split manifest")
    if train.pathologic.nunique() != 2 or valid.pathologic.nunique() != 2:
        issues.append("development split must contain both outcome classes")
    return issues, overlaps


def cv_analysis(dev, grouped):
    splitter = (StratifiedGroupKFold(n_splits=N_SPLITS, shuffle=True, random_state=SEED) if grouped else
                StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=SEED))
    rows = []
    for fold, (itr, iva) in enumerate(splitter.split(dev[FEATURES], dev.pathologic,
                                                       dev.recording_id if grouped else None), 1):
        if grouped and set(dev.recording_id.iloc[itr]) & set(dev.recording_id.iloc[iva]):
            raise RuntimeError("group leakage detected inside CV")
        Xtr, ytr = dev.iloc[itr][FEATURES], dev.iloc[itr].pathologic.to_numpy()
        Xva, yva = dev.iloc[iva][FEATURES], dev.iloc[iva].pathologic.to_numpy()
        for name, estimator in models().items():
            fitted = clone(estimator).fit(Xtr, ytr)
            prob = scores(fitted, Xva)
            rows.append({**metric_row(name, yva, prob, (prob >= .5).astype(int),
                                      "grouped_cv" if grouped else "row_cv"),
                         "fold": fold, "n_recordings_train": dev.iloc[itr].recording_id.nunique(),
                         "n_recordings_eval": dev.iloc[iva].recording_id.nunique()})
    return rows


def group_bootstrap_indices(frame, rng, group_col="recording_id"):
    groups = frame[group_col].drop_duplicates().to_numpy()
    sampled = rng.choice(groups, size=len(groups), replace=True)
    pieces = [np.flatnonzero(frame[group_col].to_numpy() == group) for group in sampled]
    return np.concatenate(pieces)


def stability_analysis(train, valid):
    rng = np.random.default_rng(SEED)
    boot_rows = []
    sample_probabilities = {name: [] for name in TREE_STABILITY_MODELS}
    Xv, yv = valid[FEATURES], valid.pathologic.to_numpy()
    for b in range(1, N_STABILITY + 1):
        idx = group_bootstrap_indices(train, rng)
        Xb, yb = train.iloc[idx][FEATURES], train.iloc[idx].pathologic.to_numpy()
        for name in TREE_STABILITY_MODELS:
            fitted = clone(models()[name]).fit(Xb, yb)
            prob = scores(fitted, Xv)
            sample_probabilities[name].append(prob)
            boot_rows.append({"replicate": b, "model": name, "n_bootstrap_rows": len(idx),
                              "n_bootstrap_recording_draws": train.recording_id.nunique(),
                              "n_unique_recordings": train.iloc[idx].recording_id.nunique(),
                              "validation_pr_auc": average_precision_score(yv, prob),
                              "validation_roc_auc": roc_auc_score(yv, prob)})
    summaries = []
    for name, draws in sample_probabilities.items():
        values = np.asarray(draws)
        class_share = (values >= .5).mean(axis=0)
        per_sample_sd = values.std(axis=0, ddof=1)
        summaries.append({"model": name, "bootstrap_replicates": N_STABILITY,
                          "validation_n": len(valid), "mean_probability_sd": per_sample_sd.mean(),
                          "median_probability_sd": np.median(per_sample_sd),
                          "max_probability_sd": per_sample_sd.max(),
                          "class_flip_rate": np.mean((class_share > 0) & (class_share < 1)),
                          "mean_validation_pr_auc": np.mean([r["validation_pr_auc"] for r in boot_rows if r["model"] == name]),
                          "mean_validation_roc_auc": np.mean([r["validation_roc_auc"] for r in boot_rows if r["model"] == name])})
    return boot_rows, summaries


def test_bootstrap(predictions, y, test_x, n_boot=N_TEST_BOOTSTRAP):
    rng = np.random.default_rng(SEED + 1)
    groups = test_x.recording_id.drop_duplicates().to_numpy()
    group_rows = {g: np.flatnonzero(test_x.recording_id.to_numpy() == g) for g in groups}
    models_names = list(predictions)
    draws = []
    for b in range(1, n_boot + 1):
        selected = rng.choice(groups, size=len(groups), replace=True)
        idx = np.concatenate([group_rows[g] for g in selected])
        yb = y[idx]
        for name in models_names:
            pb = predictions[name][idx]
            row = {"replicate": b, "model": name, "n_rows": len(idx), "n_recording_draws": len(groups),
                   "n_unique_recordings": len(set(selected)), "positive_n": int((yb == 1).sum()),
                   "pr_auc": average_precision_score(yb, pb) if np.unique(yb).size == 2 else np.nan,
                   "roc_auc": roc_auc_score(yb, pb) if np.unique(yb).size == 2 else np.nan}
            draws.append(row)
    draw_frame = pd.DataFrame(draws)
    summary = []
    for name in models_names:
        part = draw_frame[draw_frame.model == name]
        for metric, value in (("pr_auc", None), ("roc_auc", None)):
            estimate = (average_precision_score(y, predictions[name]) if metric == "pr_auc" else
                        roc_auc_score(y, predictions[name]))
            summary.append({"model": name, "metric": metric, "estimate": estimate,
                            "bootstrap_ci_low": part[metric].quantile(.025),
                            "bootstrap_ci_high": part[metric].quantile(.975),
                            "valid_replicates": int(part[metric].notna().sum()), "bootstrap_replicates": n_boot})
    # Paired differences use the same resampled recordings for both models.
    diffs = []
    for comparator in ("logistic", "rbf_svm"):
        for metric in ("pr_auc", "roc_auc"):
            wide = draw_frame.pivot(index="replicate", columns="model", values=metric)
            difference = wide["random_forest"] - wide[comparator]
            point = (average_precision_score(y, predictions["random_forest"]) -
                     average_precision_score(y, predictions[comparator])) if metric == "pr_auc" else (
                     roc_auc_score(y, predictions["random_forest"]) - roc_auc_score(y, predictions[comparator]))
            diffs.append({"contrast": f"random_forest_minus_{comparator}", "metric": metric,
                          "estimate": point, "bootstrap_ci_low": difference.quantile(.025),
                          "bootstrap_ci_high": difference.quantile(.975),
                          "valid_replicates": int(difference.notna().sum()), "bootstrap_replicates": n_boot})
    return draw_frame, summary, diffs


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.time()
    manifest = json.loads((BASE / "data" / "ctg" / "teacher" / "split-manifest.json").read_text(encoding="utf-8"))
    train = pd.read_csv(DATA / "train.csv")
    valid = pd.read_csv(DATA / "validation.csv")
    test_x = pd.read_csv(DATA / "locked-test-features.csv")
    issues, overlaps = check_inputs(train, valid, test_x, manifest)
    if issues:
        raise ValueError("Input quality checks failed: " + "; ".join(issues))

    sample_flow = []
    for name, frame in (("train", train), ("validation", valid), ("locked_test_features", test_x)):
        sample_flow.append({"stage": name, "n_rows": len(frame), "n_recordings": frame.recording_id.nunique(),
                            "positive_n": int((frame.pathologic == 1).sum()) if "pathologic" in frame else np.nan,
                            "negative_n": int((frame.pathologic == 0).sum()) if "pathologic" in frame else np.nan,
                            "rows_removed": 0, "reason": "No rows removed; fixed course split retained"})
    pd.DataFrame(sample_flow).to_csv(OUT / "sample-flow.csv", index=False)

    quality = {"status": "passed", "dataset": manifest["dataset"], "source": manifest["source"],
               "raw_zip_sha256_manifest": manifest["raw_sha256"], "seed": SEED,
               "expected_features": FEATURES, "feature_count": len(FEATURES), "missing_cells": 0,
               "nonfinite_feature_values": 0, "duplicate_sample_ids": 0, "rows_removed": 0,
               "partition_recording_overlaps": overlaps,
               "partitions": {name: {"rows": len(frame), "recordings": frame.recording_id.nunique(),
                                     "class_counts": frame.pathologic.value_counts().sort_index().to_dict()
                                     if "pathologic" in frame else None}
                              for name, frame in (("train", train), ("validation", valid), ("test", test_x))},
               "limitations": ["Segments from one recording may overlap and are not independent patients.",
                               "No external validation cohort is available."]}
    (OUT / "data-quality.json").write_text(json.dumps(quality, indent=2), encoding="utf-8")

    dev = pd.concat([train, valid], ignore_index=True)
    grouped_rows = cv_analysis(dev, grouped=True)
    row_rows = cv_analysis(dev, grouped=False)
    cv_frame = pd.DataFrame(grouped_rows + row_rows)
    cv_frame.to_csv(OUT / "cv-fold-metrics.csv", index=False)
    summary_rows = []
    for (evaluation, name), part in cv_frame.groupby(["evaluation", "model"], sort=False):
        for metric in ("pr_auc", "roc_auc", "balanced_accuracy", "sensitivity", "specificity"):
            summary_rows.append({"evaluation": evaluation, "model": name, "metric": metric,
                                 "mean": part[metric].mean(), "sd": part[metric].std(ddof=1),
                                 "folds": int(part[metric].notna().sum())})
    pd.DataFrame(summary_rows).to_csv(OUT / "cv-summary.csv", index=False)

    valid_rows = []
    Xtr, ytr = train[FEATURES], train.pathologic.to_numpy()
    Xv, yv = valid[FEATURES], valid.pathologic.to_numpy()
    for name, estimator in models().items():
        fitted = clone(estimator).fit(Xtr, ytr)
        prob = scores(fitted, Xv)
        valid_rows.append(metric_row(name, yv, prob, (prob >= .5).astype(int), "fixed_validation"))
    pd.DataFrame(valid_rows).to_csv(OUT / "validation-metrics.csv", index=False)

    stability_draws, stability_summary = stability_analysis(train, valid)
    pd.DataFrame(stability_draws).to_csv(OUT / "stability-bootstrap-replicates.csv", index=False)
    pd.DataFrame(stability_summary).to_csv(OUT / "stability-summary.csv", index=False)

    # Lock the development analysis and predictions before opening test labels.
    dev = pd.concat([train, valid], ignore_index=True)
    test_pred = {}
    test_point_rows = []
    for name, estimator in models().items():
        fitted = clone(estimator).fit(dev[FEATURES], dev.pathologic)
        test_pred[name] = scores(fitted, test_x[FEATURES])

    labels = pd.read_csv(LABELS)
    if labels.columns.tolist() != ["sample_id", "pathologic", "nsp_3class"]:
        raise ValueError("Unexpected locked test label columns")
    if labels.sample_id.tolist() != test_x.sample_id.tolist():
        raise ValueError("Locked test feature and label IDs/order do not match")
    ytest = labels.pathologic.to_numpy()
    for name, prob in test_pred.items():
        test_point_rows.append(metric_row(name, ytest, prob, (prob >= .5).astype(int), "locked_test_once"))
    pd.DataFrame(test_point_rows).to_csv(OUT / "locked-test-metrics.csv", index=False)
    test_draws, test_summary, test_diffs = test_bootstrap(test_pred, ytest, test_x)
    test_draws.to_csv(OUT / "test-cluster-bootstrap-replicates.csv", index=False)
    pd.DataFrame(test_summary).to_csv(OUT / "test-cluster-bootstrap-summary.csv", index=False)
    pd.DataFrame(test_diffs).to_csv(OUT / "test-paired-differences.csv", index=False)

    flow = pd.read_csv(OUT / "sample-flow.csv")
    flow.loc[flow.stage == "locked_test_features", "positive_n"] = int((ytest == 1).sum())
    flow.loc[flow.stage == "locked_test_features", "negative_n"] = int((ytest == 0).sum())
    flow.to_csv(OUT / "sample-flow.csv", index=False)
    quality["partitions"]["test"]["class_counts"] = labels.pathologic.value_counts().sort_index().to_dict()
    (OUT / "data-quality.json").write_text(json.dumps(quality, indent=2), encoding="utf-8")

    run_info = {"script": str(Path(__file__).relative_to(BASE)), "started_unix": started,
                "finished_unix": time.time(), "elapsed_seconds": time.time() - started,
                "python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
                "sklearn": sklearn.__version__, "seed": SEED, "group_cv_folds": N_SPLITS,
                "stability_group_bootstrap_replicates": N_STABILITY,
                "test_group_bootstrap_replicates": N_TEST_BOOTSTRAP,
                "features": FEATURES, "model_names": list(models()),
                "locked_test_labels_opened_after_development_outputs": True}
    (OUT / "run-info.json").write_text(json.dumps(run_info, indent=2), encoding="utf-8")
    print("Data quality: PASS; no rows removed; fixed partitions preserved.")
    print("Grouped CV means:")
    print(pd.DataFrame(summary_rows).query("evaluation == 'grouped_cv' and metric in ['pr_auc','roc_auc','balanced_accuracy']").to_string(index=False))
    print("Bootstrap stability:")
    print(pd.DataFrame(stability_summary).to_string(index=False))
    print("Locked test metrics (single use):")
    print(pd.DataFrame(test_point_rows)[["model", "n", "positive_n", "pr_auc", "roc_auc", "balanced_accuracy", "sensitivity", "specificity"]].to_string(index=False))
    print("Elapsed seconds:", round(time.time() - started, 2))
    log_lines = [
        "CTG grouped-validation analysis",
        f"Python={platform.python_version()} numpy={np.__version__} pandas={pd.__version__} sklearn={sklearn.__version__}",
        f"seed={SEED}; grouped_cv_folds={N_SPLITS}; stability_group_bootstrap={N_STABILITY}; test_group_bootstrap={N_TEST_BOOTSTRAP}",
        f"data_quality=PASS; rows_removed=0; recording_partition_overlap=0; elapsed_seconds={time.time() - started:.2f}",
        "Grouped CV summary:",
        pd.DataFrame(summary_rows).query(
            "evaluation == 'grouped_cv' and metric in ['pr_auc','roc_auc','balanced_accuracy']"
        ).to_string(index=False),
        "Recording-cluster training bootstrap stability:",
        pd.DataFrame(stability_summary).to_string(index=False),
        "Locked test metrics (used once):",
        pd.DataFrame(test_point_rows)[
            ["model", "n", "positive_n", "pr_auc", "roc_auc", "balanced_accuracy", "sensitivity", "specificity"]
        ].to_string(index=False),
        "Paired recording-cluster bootstrap differences:",
        pd.DataFrame(test_diffs).to_string(index=False),
    ]
    log_path = BASE / "09_工作记录" / "ctg-analysis-output.log"
    log_path.write_text("\n\n".join(log_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        main()
    if caught:
        log_path = OUT / "analysis-warnings.txt"
        log_path.write_text("\n".join(str(w.message) for w in caught), encoding="utf-8")
