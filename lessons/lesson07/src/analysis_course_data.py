from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    log_loss,
    roc_auc_score,
)
from sklearn.model_selection import RepeatedStratifiedKFold, train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


RANDOM_STATE = 2026
BASE = Path(__file__).resolve().parent
OUTPUT = BASE / ".tmp" / "article-analysis.json"

TARGET = "heart_disease_present"
FEATURES = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
]
NUMERIC = ["age", "trestbps", "chol", "thalach", "oldpeak", "ca"]
BINARY = ["sex", "fbs", "exang"]
CATEGORICAL = ["cp", "restecg", "slope", "thal"]
CATEGORY_LEVELS = [[1, 2, 3, 4], [0, 1, 2], [1, 2, 3], [3, 6, 7]]


def make_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        [
            (
                "numeric",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler()),
                    ]
                ),
                NUMERIC,
            ),
            (
                "binary",
                SimpleImputer(strategy="most_frequent"),
                BINARY,
            ),
            (
                "categorical",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="most_frequent")),
                        (
                            "onehot",
                            OneHotEncoder(
                                categories=CATEGORY_LEVELS,
                                drop="first",
                                handle_unknown="ignore",
                            ),
                        ),
                    ]
                ),
                CATEGORICAL,
            ),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def make_models() -> dict[str, object]:
    return {
        "Logistic regression": Pipeline(
            [
                ("preprocess", make_preprocessor()),
                (
                    "model",
                    LogisticRegression(
                        penalty=None, max_iter=5000, random_state=RANDOM_STATE
                    ),
                ),
            ]
        ),
        "LDA": Pipeline(
            [
                ("preprocess", make_preprocessor()),
                ("model", LinearDiscriminantAnalysis(solver="svd")),
            ]
        ),
        "Gaussian NB": Pipeline(
            [("preprocess", make_preprocessor()), ("model", GaussianNB())]
        ),
        "Prevalence baseline": DummyClassifier(strategy="prior"),
    }


def metrics(y_true: pd.Series | np.ndarray, probability: np.ndarray, threshold: float) -> dict:
    probability = np.asarray(probability)
    prediction = (probability >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, prediction, labels=[0, 1]).ravel()
    return {
        "roc_auc": float(roc_auc_score(y_true, probability)),
        "pr_auc": float(average_precision_score(y_true, probability)),
        "brier": float(brier_score_loss(y_true, probability)),
        "log_loss": float(log_loss(y_true, probability, labels=[0, 1])),
        "accuracy": float(accuracy_score(y_true, prediction)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, prediction)),
        "sensitivity": float(tp / (tp + fn)),
        "specificity": float(tn / (tn + fp)),
        "precision": float(tp / (tp + fp)) if tp + fp else 0.0,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "cost_5fn_fp": int(fp + 5 * fn),
    }


def main() -> None:
    data = pd.read_csv(BASE / "data" / "heart.csv")
    x = data[FEATURES]
    y = data[TARGET].astype(int)
    x_dev, x_test, y_dev, y_test = train_test_split(
        x,
        y,
        test_size=0.20,
        stratify=y,
        random_state=RANDOM_STATE,
    )
    models = make_models()

    cv = RepeatedStratifiedKFold(
        n_splits=5, n_repeats=5, random_state=RANDOM_STATE
    )
    cv_rows: list[dict] = []
    oof_sum = {name: np.zeros(len(x_dev)) for name in models}
    oof_count = np.zeros(len(x_dev), dtype=int)
    for fold, (train_idx, validation_idx) in enumerate(cv.split(x_dev, y_dev), 1):
        for name, model in models.items():
            fitted = clone(model).fit(x_dev.iloc[train_idx], y_dev.iloc[train_idx])
            probability = fitted.predict_proba(x_dev.iloc[validation_idx])[:, 1]
            cv_rows.append(
                {
                    "model": name,
                    "fold": fold,
                    **metrics(y_dev.iloc[validation_idx], probability, 0.5),
                }
            )
            oof_sum[name][validation_idx] += probability
        oof_count[validation_idx] += 1

    cv_frame = pd.DataFrame(cv_rows)
    aggregations = {}
    for metric in [
        "roc_auc",
        "pr_auc",
        "brier",
        "log_loss",
        "sensitivity",
        "specificity",
        "cost_5fn_fp",
    ]:
        aggregations[f"{metric}_mean"] = (metric, "mean")
        aggregations[f"{metric}_sd"] = (metric, "std")
    cv_summary = cv_frame.groupby("model").agg(**aggregations).reset_index()

    oof_probability = {name: values / oof_count for name, values in oof_sum.items()}
    threshold_grid = np.round(np.arange(0.05, 0.951, 0.01), 2)
    selected_thresholds = {}
    for name in ["Logistic regression", "LDA"]:
        probability = oof_probability[name]
        candidates = []
        for threshold in threshold_grid:
            result = metrics(y_dev, probability, float(threshold))
            candidates.append(
                (
                    result["cost_5fn_fp"],
                    -result["sensitivity"],
                    -result["specificity"],
                    -float(threshold),
                    float(threshold),
                )
            )
        selected_thresholds[name] = min(candidates)[-1]

    threshold_curves = []
    for name in ["Logistic regression", "LDA"]:
        probability = oof_probability[name]
        for threshold in threshold_grid:
            threshold_curves.append(
                {
                    "model": name,
                    "threshold": float(threshold),
                    **metrics(y_dev, probability, float(threshold)),
                }
            )

    fitted_models = {}
    test_probabilities = {}
    test_rows = []
    for name, model in models.items():
        fitted = clone(model).fit(x_dev, y_dev)
        probability = fitted.predict_proba(x_test)[:, 1]
        fitted_models[name] = fitted
        test_probabilities[name] = probability
        test_rows.append(
            {
                "model": name,
                "threshold": selected_thresholds.get(name, 0.5),
                **metrics(y_test, probability, selected_thresholds.get(name, 0.5)),
            }
        )
    test_frame = pd.DataFrame(test_rows)

    rng = np.random.default_rng(RANDOM_STATE)
    negative_idx = np.flatnonzero(y_test.to_numpy() == 0)
    positive_idx = np.flatnonzero(y_test.to_numpy() == 1)
    bootstrap_metrics = [
        "roc_auc",
        "pr_auc",
        "brier",
        "sensitivity",
        "specificity",
        "cost_5fn_fp",
    ]
    bootstrap = {
        name: {metric: [] for metric in bootstrap_metrics} for name in models
    }
    for _ in range(2000):
        sample_idx = np.concatenate(
            [
                rng.choice(negative_idx, len(negative_idx), replace=True),
                rng.choice(positive_idx, len(positive_idx), replace=True),
            ]
        )
        rng.shuffle(sample_idx)
        y_boot = y_test.to_numpy()[sample_idx]
        for name in models:
            result = metrics(
                y_boot,
                test_probabilities[name][sample_idx],
                selected_thresholds.get(name, 0.5),
            )
            for metric in bootstrap_metrics:
                bootstrap[name][metric].append(result[metric])
    bootstrap_ci = {
        name: {
            metric: [
                float(np.quantile(values, 0.025)),
                float(np.quantile(values, 0.975)),
            ]
            for metric, values in model_metrics.items()
        }
        for name, model_metrics in bootstrap.items()
    }

    # Descriptive LDA diagnostics use development data only.
    imputed_numeric = SimpleImputer(strategy="median").fit_transform(x_dev[NUMERIC])
    standardized_numeric = (
        imputed_numeric - imputed_numeric.mean(axis=0)
    ) / imputed_numeric.std(axis=0, ddof=0)
    standardized_frame = pd.DataFrame(standardized_numeric, columns=NUMERIC)
    covariance_0 = standardized_frame[y_dev.to_numpy() == 0].cov().to_numpy()
    covariance_1 = standardized_frame[y_dev.to_numpy() == 1].cov().to_numpy()
    covariance_difference = float(
        np.linalg.norm(covariance_1 - covariance_0, "fro")
        / ((np.linalg.norm(covariance_1, "fro") + np.linalg.norm(covariance_0, "fro")) / 2)
    )
    class_skewness = (
        x_dev[NUMERIC]
        .assign(outcome=y_dev.to_numpy())
        .groupby("outcome")
        .skew()
        .to_dict()
    )

    logistic_fit = fitted_models["Logistic regression"]
    feature_names = logistic_fit.named_steps["preprocess"].get_feature_names_out().tolist()
    coefficients = logistic_fit.named_steps["model"].coef_[0]
    age_index = feature_names.index("age")
    age_coefficient = float(coefficients[age_index])
    development_age_sd = float(x_dev["age"].std(ddof=0))
    boot_age_coefficients = []
    numeric_bootstrap = {name: [] for name in NUMERIC}
    reference_scales = {
        name: float(logistic_fit.named_steps["preprocess"].named_transformers_["numeric"].named_steps["scale"].scale_[index])
        for index, name in enumerate(NUMERIC)
    }
    for _ in range(500):
        sample_idx = rng.integers(0, len(x_dev), len(x_dev))
        if y_dev.iloc[sample_idx].nunique() < 2:
            continue
        fitted = clone(models["Logistic regression"]).fit(
            x_dev.iloc[sample_idx], y_dev.iloc[sample_idx]
        )
        names = fitted.named_steps["preprocess"].get_feature_names_out().tolist()
        boot_scales = fitted.named_steps["preprocess"].named_transformers_["numeric"].named_steps["scale"].scale_
        boot_coef = fitted.named_steps["model"].coef_[0]
        for index, feature in enumerate(NUMERIC):
            value = float(boot_coef[names.index(feature)])
            numeric_bootstrap[feature].append(
                value * reference_scales[feature] / float(boot_scales[index])
            )
        boot_age_coefficients.append(numeric_bootstrap["age"][-1])

    continuous_coefficients = []
    for feature in NUMERIC:
        index = feature_names.index(feature)
        beta = float(coefficients[index])
        values = numeric_bootstrap[feature]
        continuous_coefficients.append(
            {
                "feature": feature,
                "beta_per_development_sd": beta,
                "odds_ratio_per_development_sd": float(np.exp(beta)),
                "beta_ci95_percentile": [
                    float(np.quantile(values, 0.025)),
                    float(np.quantile(values, 0.975)),
                ],
                "or_ci95_percentile": [
                    float(np.exp(np.quantile(values, 0.025))),
                    float(np.exp(np.quantile(values, 0.975))),
                ],
                "sign_stability": float(
                    np.mean(np.sign(values) == np.sign(beta))
                ),
            }
        )

    result = {
        "dataset": {
            "n": int(len(data)),
            "n_features": len(FEATURES),
            "class_counts": {
                str(key): int(value)
                for key, value in y.value_counts().sort_index().items()
            },
            "missing_by_feature": {
                key: int(value)
                for key, value in data[FEATURES].isna().sum().items()
            },
            "missing_cells": int(data[FEATURES].isna().sum().sum()),
            "site_counts": {
                str(key): int(value)
                for key, value in data["site"].value_counts(dropna=False).items()
            },
            "duplicate_feature_outcome_rows": int(
                data[FEATURES + [TARGET]].duplicated().sum()
            ),
        },
        "split": {
            "development_n": int(len(x_dev)),
            "development_positive": int(y_dev.sum()),
            "test_n": int(len(x_test)),
            "test_positive": int(y_test.sum()),
            "test_negative": int((y_test == 0).sum()),
        },
        "method": {
            "numeric": NUMERIC,
            "categorical": CATEGORICAL,
            "binary": BINARY,
            "onehot_dimensions": len(feature_names) - len(NUMERIC) - len(BINARY),
            "transformed_dimensions": len(feature_names),
            "logistic_parameters_including_intercept": len(feature_names) + 1,
            "lda_formal_parameters": int(
                2 * len(feature_names)
                + len(feature_names) * (len(feature_names) + 1) / 2
                + 1
            ),
            "cross_validation": "5-fold repeated 5 times with fold-level imputation, scaling, and one-hot encoding",
            "threshold_selection": "minimum 5*FN+FP on development out-of-fold probabilities averaged across repeats",
        },
        "cv_summary": cv_summary.round(6).to_dict(orient="records"),
        "selected_thresholds_development_oof": selected_thresholds,
        "threshold_curves_development_oof": threshold_curves,
        "test_metrics": test_frame.round(6).to_dict(orient="records"),
        "test_predictions": {
            "y": y_test.astype(int).tolist(),
            **{
                name: probability.astype(float).tolist()
                for name, probability in test_probabilities.items()
            },
        },
        "test_stratified_bootstrap_95ci": bootstrap_ci,
        "assumption_audit_development": {
            "relative_covariance_difference": covariance_difference,
            "class_specific_skewness": class_skewness,
        },
        "age_logistic": {
            "beta_per_development_sd": age_coefficient,
            "odds_ratio_per_development_sd": float(np.exp(age_coefficient)),
            "bootstrap_n": len(boot_age_coefficients),
            "beta_fixed_development_sd_percentiles": [
                float(np.quantile(boot_age_coefficients, 0.025)),
                float(np.quantile(boot_age_coefficients, 0.5)),
                float(np.quantile(boot_age_coefficients, 0.975)),
            ],
            "sign_stability": float(
                np.mean(
                    np.sign(boot_age_coefficients) == np.sign(age_coefficient)
                )
            ),
        },
        "continuous_coefficients": continuous_coefficients,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
