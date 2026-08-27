import logging
from datetime import datetime
from django.utils import timezone

logger = logging.getLogger(__name__)

class PredictionService:
    """
    Service responsible for loading ML models, preparing input data from
    existing Feature and State models, executing inference, and persisting
    RiskPredictions via the existing PredictionRepository.
    """

    STATION_RISK_FEATURES = [
        "avg_cycle_time",
        "cycle_time_std",
        "cycle_time_trend",
        "throughput",
        "temperature_mean",
        "vibration_mean",
        "utilization",
        "current_cycle_time"
    ]

    DEFECT_RISK_FEATURES = [
        "station_avg_cycle_time",
        "station_temperature_mean",
        "station_vibration_mean",
        "station_utilization",
        "station_current_cycle_time",
        "vehicle_avg_cycle_time",
        "vehicle_cycle_time_deviation",
        "vehicle_quality_event_count"
    ]

    def __init__(
        self, 
        prediction_repository,
        risk_model=None, 
        defect_model=None,
        model_version="1.0",
        prediction_horizon_minutes=30
    ):
        self.prediction_repository = prediction_repository
        self.risk_model = risk_model
        self.defect_model = defect_model
        self.model_version = model_version
        self.prediction_horizon = prediction_horizon_minutes

    def predict(
        self, 
        station_features, 
        station_state, 
        vehicle_features=None, 
        vehicle_state=None
    ):
        """
        Main API to predict risk. Defaults to Station Risk if no vehicle data 
        is provided, otherwise calculates Defect Risk.
        """
        if not station_features or not station_state:
            raise ValueError("Station features and state are required for all predictions.")

        if vehicle_features and vehicle_state:
            return self._predict_defect(
                station_features, station_state, vehicle_features, vehicle_state
            )
        else:
            return self._predict_station_risk(station_features, station_state)

    def _predict_station_risk(self, station_features, station_state):
        if not self.risk_model:
            raise RuntimeError("Station risk model is not loaded.")

        # 1. Prepare & Validate Input
        feature_vector = self._prepare_station_risk_input(station_features, station_state)
        
        # 2. Inference
        risk_score, confidence = self._inference(self.risk_model, feature_vector)

        # 3. Output Validation & Persistence
        self._validate_prediction(risk_score, confidence)
        
        return self.prediction_repository.save_prediction(
            timestamp=timezone.now(),
            entity_type="STATION",
            entity_id=station_features.station.station_id,
            risk_type="BOTTLENECK",
            prediction_target="HIGH_RISK_STATE",
            risk_score=risk_score,
            confidence=confidence,
            prediction_horizon_minutes=self.prediction_horizon,
            model_name=self.risk_model.__class__.__name__,
            model_version=self.model_version
        )

    def _predict_defect(self, station_features, station_state, vehicle_features, vehicle_state):
        if not self.defect_model:
            raise RuntimeError("Defect model is not loaded.")

        # 1. Prepare & Validate Input
        feature_vector = self._prepare_defect_input(
            station_features, station_state, vehicle_features, vehicle_state
        )
        
        # 2. Inference
        risk_score, confidence = self._inference(self.defect_model, feature_vector)

        # 3. Output Validation & Persistence
        self._validate_prediction(risk_score, confidence)
        
        return self.prediction_repository.save_prediction(
            timestamp=timezone.now(),
            entity_type="VEHICLE",
            entity_id=vehicle_features.vehicle.vehicle_id,
            risk_type="DEFECT",
            prediction_target="QUALITY_DEFECT",
            risk_score=risk_score,
            confidence=confidence,
            prediction_horizon_minutes=self.prediction_horizon,
            model_name=self.defect_model.__class__.__name__,
            model_version=self.model_version
        )

    def _prepare_station_risk_input(self, station_features, station_state):
        try:
            return [
                station_features.avg_cycle_time or 0.0,
                station_features.cycle_time_std or 0.0,
                station_features.cycle_time_trend or 0.0,
                station_features.throughput or 0.0,
                station_features.temperature_mean or 0.0,
                station_features.vibration_mean or 0.0,
                station_features.utilization or 0.0,
                station_state.current_cycle_time or 0.0
            ]
        except AttributeError as e:
            logger.error(f"Missing required field in Station models: {e}")
            raise ValueError(f"Invalid station input: {e}")

    def _prepare_defect_input(self, station_features, station_state, vehicle_features, vehicle_state):
        try:
            return [
                station_features.avg_cycle_time or 0.0,
                station_features.temperature_mean or 0.0,
                station_features.vibration_mean or 0.0,
                station_features.utilization or 0.0,
                station_state.current_cycle_time or 0.0,
                vehicle_features.avg_cycle_time or 0.0,
                vehicle_features.cycle_time_deviation or 0.0,
                vehicle_features.quality_event_count or 0.0
            ]
        except AttributeError as e:
            logger.error(f"Missing required field in models: {e}")
            raise ValueError(f"Invalid vehicle/station input: {e}")

    def _inference(self, model, feature_vector):
        """
        Executes model inference, expecting scikit-learn standard interface.
        Returns risk probability (positive class) and prediction confidence.
        """
        try:
            # Requires 2D array: reshape vector to (1, -1)
            X = [feature_vector]
            
            if hasattr(model, "predict_proba"):
                probabilities = model.predict_proba(X)[0]
                
                # Assume positive class is at index 1 or the last class 
                # (You should map this explicitly based on model.classes_ in a real scenario)
                positive_idx = 1 if len(probabilities) > 1 else 0
                
                risk_score = probabilities[positive_idx]
                confidence = max(probabilities)
            else:
                # Fallback for models without probability distributions
                prediction = model.predict(X)[0]
                risk_score = float(prediction)
                confidence = 1.0
                
            return risk_score, float(confidence)
            
        except Exception as e:
            logger.error(f"Model inference failed: {e}")
            raise RuntimeError(f"Model inference failed: {e}")

    def _validate_prediction(self, risk_score, confidence):
        if not (0.0 <= risk_score <= 1.0):
            raise ValueError(f"Invalid risk score: {risk_score}. Must be in [0, 1]")
        if not (0.0 <= confidence <= 1.0):
            raise ValueError(f"Invalid confidence: {confidence}. Must be in [0, 1]")