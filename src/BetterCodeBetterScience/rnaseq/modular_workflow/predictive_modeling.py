"""Predictive modeling module for scRNA-seq analysis workflow.

Functions for building and evaluating age prediction models.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import ShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVR


def prepare_features(
    counts_df: pd.DataFrame,
    metadata: pd.DataFrame,
) -> tuple[pd.DataFrame, np.ndarray]:
    """Prepare feature matrix and target variable.

    Parameters
    ----------
    counts_df : pd.DataFrame
        Gene expression counts
    metadata : pd.DataFrame
        Metadata with 'age' and 'sex' columns

    Returns
    -------
    tuple[pd.DataFrame, np.ndarray]
        Feature matrix (genes + sex) and age target
    """
    X_genes = counts_df.copy()

    # Add sex as binary feature
    sex_encoded = pd.get_dummies(metadata["sex"], drop_first=True)
    X = pd.concat([X_genes, sex_encoded], axis=1)

    # Target: age
    y = metadata["age"].values

    print(f"Feature matrix shape: {X.shape}")
    print(f"Number of samples: {len(y)}")
    print(f"Age range: {y.min():.1f} - {y.max():.1f} years")

    return X, y


def prepare_baseline_features(metadata: pd.DataFrame) -> pd.DataFrame:
    """Prepare baseline feature matrix (sex only).

    Parameters
    ----------
    metadata : pd.DataFrame
        Metadata with 'sex' column

    Returns
    -------
    pd.DataFrame
        Sex-only feature matrix
    """
    return pd.get_dummies(metadata["sex"], drop_first=True)


def train_evaluate_fold(
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
    C: float = 1.0,
    max_iter: int = 10000,
    random_state: int = 42,
) -> tuple[float, float, np.ndarray]:
    """Train and evaluate model for one fold.

    Parameters
    ----------
    X_train : np.ndarray
        Training features
    X_test : np.ndarray
        Test features
    y_train : np.ndarray
        Training target
    y_test : np.ndarray
        Test target
    C : float
        Regularization parameter
    max_iter : int
        Maximum iterations
    random_state : int
        Random seed

    Returns
    -------
    tuple[float, float, np.ndarray]
        R2 score, MAE, and predictions
    """
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train model
    model = LinearSVR(C=C, max_iter=max_iter, random_state=random_state, dual="auto")
    model.fit(X_train_scaled, y_train)

    # Predict
    y_pred = model.predict(X_test_scaled)

    # Metrics
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)

    return r2, mae, y_pred


def run_cross_validation(
    X: pd.DataFrame,
    y: np.ndarray,
    n_splits: int = 5,
    test_size: float = 0.2,
    random_state: int = 42,
) -> tuple[list[float], list[float], list[float], list[float]]:
    """Run cross-validation for age prediction.

    Parameters
    ----------
    X : pd.DataFrame
        Feature matrix
    y : np.ndarray
        Target variable
    n_splits : int
        Number of CV splits
    test_size : float
        Fraction for test set
    random_state : int
        Random seed

    Returns
    -------
    tuple[list, list, list, list]
        R2 scores, MAE scores, predictions, actuals
    """
    cv = ShuffleSplit(n_splits=n_splits, test_size=test_size, random_state=random_state)

    r2_scores = []
    mae_scores = []
    predictions_list = []
    actual_list = []

    for fold, (train_idx, test_idx) in enumerate(cv.split(X)):
        print(f"\nFold {fold + 1}/{n_splits}")

        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        r2, mae, y_pred = train_evaluate_fold(
            X_train.values, X_test.values, y_train, y_test
        )

        r2_scores.append(r2)
        mae_scores.append(mae)
        predictions_list.extend(y_pred)
        actual_list.extend(y_test)

        print(f"  R2 Score: {r2:.3f}")
        print(f"  MAE: {mae:.2f} years")

    return r2_scores, mae_scores, predictions_list, actual_list


def print_cv_results(
    r2_scores: list[float],
    mae_scores: list[float],
    model_name: str = "Model",
) -> None:
    """Print cross-validation summary.

    Parameters
    ----------
    r2_scores : list[float]
        R2 scores per fold
    mae_scores : list[float]
        MAE scores per fold
    model_name : str
        Name of the model
    """
    print("\n" + "=" * 50)
    print(f"{model_name} CROSS-VALIDATION RESULTS")
    print("=" * 50)
    print(f"R2 Score: {np.mean(r2_scores):.3f} +/- {np.std(r2_scores):.3f}")
    print(f"MAE: {np.mean(mae_scores):.2f} +/- {np.std(mae_scores):.2f} years")
    print("=" * 50)


def plot_predictions(
    actual: list[float],
    predicted: list[float],
    r2_scores: list[float],
    mae_scores: list[float],
    figure_dir: Path | None = None,
) -> None:
    """Plot predicted vs actual ages.

    Parameters
    ----------
    actual : list[float]
        Actual ages
    predicted : list[float]
        Predicted ages
    r2_scores : list[float]
        R2 scores
    mae_scores : list[float]
        MAE scores
    figure_dir : Path, optional
        Directory to save figures
    """
    plt.figure(figsize=(8, 6))

    plt.scatter(actual, predicted, alpha=0.6, s=80)

    min_age = min(min(actual), min(predicted))
    max_age = max(max(actual), max(predicted))
    plt.plot(
        [min_age, max_age],
        [min_age, max_age],
        "r--",
        linewidth=2,
        label="Perfect Prediction",
    )

    plt.xlabel("Actual Age (years)", fontsize=12)
    plt.ylabel("Predicted Age (years)", fontsize=12)
    plt.title(
        f"Age Prediction Performance\n"
        f"R2 = {np.mean(r2_scores):.3f}, MAE = {np.mean(mae_scores):.2f} years",
        fontsize=14,
    )
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    if figure_dir is not None:
        plt.savefig(
            figure_dir / "age_prediction_performance.png", dpi=300, bbox_inches="tight"
        )
    plt.close()


def compare_models(
    full_r2: list[float],
    full_mae: list[float],
    baseline_r2: list[float],
    baseline_mae: list[float],
) -> None:
    """Print comparison between full and baseline models.

    Parameters
    ----------
    full_r2 : list[float]
        R2 scores for full model
    full_mae : list[float]
        MAE scores for full model
    baseline_r2 : list[float]
        R2 scores for baseline
    baseline_mae : list[float]
        MAE scores for baseline
    """
    print("=" * 60)
    print("MODEL COMPARISON")
    print("=" * 60)
    print("Full Model (Genes + Sex):")
    print(f"  R2 Score: {np.mean(full_r2):.3f} +/- {np.std(full_r2):.3f}")
    print(f"  MAE: {np.mean(full_mae):.2f} +/- {np.std(full_mae):.2f} years")
    print("\nBaseline Model (Sex Only):")
    print(f"  R2 Score: {np.mean(baseline_r2):.3f} +/- {np.std(baseline_r2):.3f}")
    print(f"  MAE: {np.mean(baseline_mae):.2f} +/- {np.std(baseline_mae):.2f} years")
    print("\nImprovement:")
    print(f"  Delta R2: {np.mean(full_r2) - np.mean(baseline_r2):.3f}")
    print(f"  Delta MAE: {np.mean(baseline_mae) - np.mean(full_mae):.2f} years")
    print("=" * 60)


def run_predictive_modeling_pipeline(
    counts_df: pd.DataFrame,
    metadata: pd.DataFrame,
    n_splits: int = 5,
    figure_dir: Path | None = None,
) -> dict:
    """Run complete predictive modeling pipeline.

    Parameters
    ----------
    counts_df : pd.DataFrame
        Gene expression counts
    metadata : pd.DataFrame
        Metadata with age and sex
    n_splits : int
        Number of CV splits
    figure_dir : Path, optional
        Directory to save figures

    Returns
    -------
    dict
        Results dictionary with scores
    """
    # Prepare features
    X, y = prepare_features(counts_df, metadata)
    X_baseline = prepare_baseline_features(metadata)

    # Run full model
    print("\n--- Full Model (Genes + Sex) ---")
    r2_scores, mae_scores, predictions, actuals = run_cross_validation(X, y, n_splits)
    print_cv_results(r2_scores, mae_scores, "Full Model")

    # Plot predictions
    plot_predictions(actuals, predictions, r2_scores, mae_scores, figure_dir)

    # Run baseline model
    print("\n--- Baseline Model (Sex Only) ---")
    baseline_r2, baseline_mae, _, _ = run_cross_validation(X_baseline, y, n_splits)
    print_cv_results(baseline_r2, baseline_mae, "Baseline")

    # Compare models
    compare_models(r2_scores, mae_scores, baseline_r2, baseline_mae)

    return {
        "full_r2": r2_scores,
        "full_mae": mae_scores,
        "baseline_r2": baseline_r2,
        "baseline_mae": baseline_mae,
        "predictions": predictions,
        "actuals": actuals,
    }
