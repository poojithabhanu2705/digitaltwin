"""
TwinSight ML Model Training Pipeline

Trains the two production ML models:

1. Station Risk Model
   Predicts whether a station is likely to enter a high-risk /
   bottleneck state.

2. Vehicle Defect Model
   Predicts whether a vehicle is likely to experience a
   quality defect.

The feature order MUST remain synchronized with
core.services.ml.prediction_service.PredictionService.
"""

from pathlib import Path
import logging

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split


# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "ml" / "data"
MODEL_DIR = BASE_DIR / "ml" / "models"

STATION_DATASET = DATA_DIR / "station_training_data.csv"
VEHICLE_DATASET = DATA_DIR / "vehicle_training_data.csv"

STATION_MODEL_PATH = MODEL_DIR / "station_risk_model.joblib"
VEHICLE_MODEL_PATH = MODEL_DIR / "vehicle_defect_model.joblib"

RANDOM_STATE = 42


# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------
# Feature definitions
# -------------------------------------------------------------------

STATION_FEATURES = [
    "avg_cycle_time",
    "cycle_time_std",
    "cycle_time_trend",
    "throughput",
    "temperature_mean",
    "vibration_mean",
    "utilization",
    "current_cycle_time",
]

VEHICLE_FEATURES = [
    "station_avg_cycle_time",
    "station_temperature_mean",
    "station_vibration_mean",
    "station_utilization",
    "station_current_cycle_time",
    "vehicle_avg_cycle_time",
    "vehicle_cycle_time_deviation",
    "vehicle_quality_event_count",
]


STATION_TARGET = "high_risk"
VEHICLE_TARGET = "defect"


# -------------------------------------------------------------------
# Validation
# -------------------------------------------------------------------

def validate_dataset(df, features, target, dataset_name):
    """
    Validate that a training dataset contains all required columns.
    """

    required_columns = set(features + [target])
    actual_columns = set(df.columns)

    missing = required_columns - actual_columns

    if missing:
        raise ValueError(
            f"{dataset_name} dataset is missing columns: "
            f"{sorted(missing)}"
        )

    if df.empty:
        raise ValueError(
            f"{dataset_name} dataset is empty."
        )

    # Check target values
    unique_targets = sorted(df[target].dropna().unique())

    if not set(unique_targets).issubset({0, 1}):
        raise ValueError(
            f"{dataset_name} target '{target}' must contain only "
            f"0 and 1. Found: {unique_targets}"
        )

    # Check missing feature values
    missing_values = df[features].isnull().sum()

    if missing_values.any():
        logger.warning(
            "%s contains missing feature values. "
            "They will be filled using column medians.",
            dataset_name,
        )

        for feature in features:
            if df[feature].isnull().any():
                df[feature] = df[feature].fillna(
                    df[feature].median()
                )

    return df


# -------------------------------------------------------------------
# Dataset preparation
# -------------------------------------------------------------------

def prepare_dataset(
    dataset_path,
    features,
    target,
    dataset_name,
):
    """
    Load and prepare a training dataset.
    """

    logger.info(
        "Loading %s dataset from %s",
        dataset_name,
        dataset_path,
    )

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Training dataset not found: {dataset_path}"
        )

    df = pd.read_csv(dataset_path)

    df = validate_dataset(
        df,
        features,
        target,
        dataset_name,
    )

    X = df[features].copy()
    y = df[target].astype(int)

    # Convert everything to numeric.
    for feature in features:
        X[feature] = pd.to_numeric(
            X[feature],
            errors="coerce",
        )

    # Fill values introduced by conversion.
    for feature in features:
        if X[feature].isnull().any():
            X[feature] = X[feature].fillna(
                X[feature].median()
            )

    # Final finite-value validation
    if not np.isfinite(X.to_numpy()).all():
        raise ValueError(
            f"{dataset_name} contains non-finite feature values."
        )

    logger.info(
        "%s samples: %d",
        dataset_name,
        len(df),
    )

    logger.info(
        "%s positive samples: %d",
        dataset_name,
        int(y.sum()),
    )

    logger.info(
        "%s negative samples: %d",
        dataset_name,
        int((y == 0).sum()),
    )

    return X, y


# -------------------------------------------------------------------
# Model training
# -------------------------------------------------------------------

def train_random_forest(X_train, y_train):
    """
    Train deterministic Random Forest classifier.
    """

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train,
    )

    return model


# -------------------------------------------------------------------
# Evaluation
# -------------------------------------------------------------------

def evaluate_model(
    model,
    X_test,
    y_test,
    model_name,
):
    """
    Evaluate trained model.
    """

    predictions = model.predict(X_test)

    probabilities = model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    logger.info(
        "\n%s\nAccuracy: %.4f",
        model_name,
        accuracy,
    )

    print("\n" + "=" * 70)
    print(model_name)
    print("=" * 70)

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            digits=4,
        )
    )

    print("\nConfusion Matrix:")
    print(
        confusion_matrix(
            y_test,
            predictions,
        )
    )

    # ROC-AUC requires both classes to exist in test set.
    if len(np.unique(y_test)) == 2:
        auc = roc_auc_score(
            y_test,
            probabilities,
        )

        print(f"\nROC-AUC: {auc:.4f}")

    print("\nFeature Importance:")

    feature_importance = pd.Series(
        model.feature_importances_,
        index=X_test.columns,
    ).sort_values(
        ascending=False
    )

    print(feature_importance)

    return {
        "accuracy": accuracy,
        "feature_importance": feature_importance,
    }


# -------------------------------------------------------------------
# Save model
# -------------------------------------------------------------------

def save_model(
    model,
    path,
    feature_names,
    model_name,
):
    """
    Save trained model and metadata.
    """

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    artifact = {
        "model": model,
        "feature_names": feature_names,
        "model_name": model_name,
        "model_version": "1.0",
        "random_state": RANDOM_STATE,
    }

    joblib.dump(
        artifact,
        path,
    )

    logger.info(
        "Saved %s to %s",
        model_name,
        path,
    )


# -------------------------------------------------------------------
# Station model
# -------------------------------------------------------------------

def train_station_model():
    """
    Train the station bottleneck/high-risk model.
    """

    X, y = prepare_dataset(
        STATION_DATASET,
        STATION_FEATURES,
        STATION_TARGET,
        "Station Risk",
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    logger.info(
        "Training Station Risk Model..."
    )

    model = train_random_forest(
        X_train,
        y_train,
    )

    evaluate_model(
        model,
        X_test,
        y_test,
        "STATION RISK MODEL",
    )

    save_model(
        model,
        STATION_MODEL_PATH,
        STATION_FEATURES,
        "StationRiskRandomForest",
    )

    return model


# -------------------------------------------------------------------
# Vehicle model
# -------------------------------------------------------------------

def train_vehicle_model():
    """
    Train the vehicle defect model.
    """

    X, y = prepare_dataset(
        VEHICLE_DATASET,
        VEHICLE_FEATURES,
        VEHICLE_TARGET,
        "Vehicle Defect",
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    logger.info(
        "Training Vehicle Defect Model..."
    )

    model = train_random_forest(
        X_train,
        y_train,
    )

    evaluate_model(
        model,
        X_test,
        y_test,
        "VEHICLE DEFECT MODEL",
    )

    save_model(
        model,
        VEHICLE_MODEL_PATH,
        VEHICLE_FEATURES,
        "VehicleDefectRandomForest",
    )

    return model


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main():
    print()
    print("=" * 70)
    print("TwinSight ML Training Pipeline")
    print("=" * 70)
    print()

    logger.info(
        "Project directory: %s",
        BASE_DIR,
    )

    logger.info(
        "Model output directory: %s",
        MODEL_DIR,
    )

    train_station_model()

    print()

    train_vehicle_model()

    print()
    print("=" * 70)
    print("TRAINING COMPLETE")
    print("=" * 70)
    print()

    print(
        f"Station model: {STATION_MODEL_PATH}"
    )

    print(
        f"Vehicle model: {VEHICLE_MODEL_PATH}"
    )


if __name__ == "__main__":
    main()