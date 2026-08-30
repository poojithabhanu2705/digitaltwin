import logging

from django.utils import timezone

from core.services.ml.model_loader import MLModelLoader


logger = logging.getLogger(__name__)


class PredictionService:
    """
    Service responsible for:

    1. Loading trained ML models.
    2. Preparing feature vectors from Django feature/state models.
    3. Running ML inference.
    4. Validating prediction outputs.
    5. Persisting RiskPrediction records through PredictionRepository.

    Supported models:
        - StationRiskRandomForest
        - VehicleDefectRandomForest
    """

    STATION_RISK_FEATURES = [
        "avg_cycle_time",
        "cycle_time_std",
        "cycle_time_trend",
        "throughput",
        "temperature_mean",
        "vibration_mean",
        "utilization",
        "current_cycle_time",
    ]

    DEFECT_RISK_FEATURES = [
        "station_avg_cycle_time",
        "station_temperature_mean",
        "station_vibration_mean",
        "station_utilization",
        "station_current_cycle_time",
        "vehicle_avg_cycle_time",
        "vehicle_cycle_time_deviation",
        "vehicle_quality_event_count",
    ]

    def __init__(
        self,
        prediction_repository,
        risk_model=None,
        defect_model=None,
        model_version="1.0",
        prediction_horizon_minutes=30,
    ):
        """
        Initialize PredictionService.

        Models can be explicitly injected for testing, or loaded automatically
        from MLModelLoader for production use.
        """

        self.prediction_repository = prediction_repository

        # ------------------------------------------------------------
        # Load station-risk model
        # ------------------------------------------------------------

        if risk_model is None:
            risk_bundle = MLModelLoader.load_station_risk_model()
        else:
            risk_bundle = risk_model

        # ------------------------------------------------------------
        # Load vehicle-defect model
        # ------------------------------------------------------------

        if defect_model is None:
            defect_bundle = MLModelLoader.load_vehicle_defect_model()
        else:
            defect_bundle = defect_model

        # ------------------------------------------------------------
        # Extract actual sklearn models from bundles
        # ------------------------------------------------------------

        if isinstance(risk_bundle, dict):
            self.risk_model = risk_bundle["model"]

            self.risk_model_name = risk_bundle.get(
                "model_name",
                self.risk_model.__class__.__name__,
            )

            self.risk_model_version = risk_bundle.get(
                "model_version",
                model_version,
            )

        else:
            self.risk_model = risk_bundle

            self.risk_model_name = self.risk_model.__class__.__name__

            self.risk_model_version = model_version

        if isinstance(defect_bundle, dict):
            self.defect_model = defect_bundle["model"]

            self.defect_model_name = defect_bundle.get(
                "model_name",
                self.defect_model.__class__.__name__,
            )

            self.defect_model_version = defect_bundle.get(
                "model_version",
                model_version,
            )

        else:
            self.defect_model = defect_bundle

            self.defect_model_name = self.defect_model.__class__.__name__

            self.defect_model_version = model_version

        self.prediction_horizon = prediction_horizon_minutes

        logger.info(
            "PredictionService initialized. "
            "station_model=%s version=%s, "
            "defect_model=%s version=%s",
            self.risk_model_name,
            self.risk_model_version,
            self.defect_model_name,
            self.defect_model_version,
        )

    # ==================================================================
    # PUBLIC API
    # ==================================================================

    def predict(
        self,
        station_features,
        station_state,
        vehicle_features=None,
        vehicle_state=None,
    ):
        """
        Main prediction API.

        If vehicle data is supplied:
            Vehicle Defect model is used.

        Otherwise:
            Station Risk model is used.
        """

        if station_features is None or station_state is None:
            raise ValueError(
                "Station features and state are required for all predictions."
            )

        if vehicle_features is not None and vehicle_state is not None:
            return self._predict_defect(
                station_features=station_features,
                station_state=station_state,
                vehicle_features=vehicle_features,
                vehicle_state=vehicle_state,
            )

        return self._predict_station_risk(
            station_features=station_features,
            station_state=station_state,
        )

    # ==================================================================
    # STATION RISK
    # ==================================================================

    def _predict_station_risk(
        self,
        station_features,
        station_state,
    ):
        """
        Generate a station bottleneck/high-risk prediction.
        """

        if self.risk_model is None:
            raise RuntimeError(
                "Station risk model is not loaded."
            )

        feature_vector = self._prepare_station_risk_input(
            station_features,
            station_state,
        )

        risk_score, confidence = self._inference(
            self.risk_model,
            feature_vector,
        )

        self._validate_prediction(
            risk_score,
            confidence,
        )

        return self.prediction_repository.save_prediction(
            timestamp=timezone.now(),
            entity_type="STATION",
            entity_id=station_features.station.station_id,
            risk_type="BOTTLENECK",
            prediction_target="HIGH_RISK_STATE",
            risk_score=risk_score,
            confidence=confidence,
            prediction_horizon_minutes=self.prediction_horizon,
            model_name=self.risk_model_name,
            model_version=self.risk_model_version,
        )

    # ==================================================================
    # VEHICLE DEFECT
    # ==================================================================

    def _predict_defect(
        self,
        station_features,
        station_state,
        vehicle_features,
        vehicle_state,
    ):
        """
        Generate a vehicle quality-defect prediction.
        """

        if self.defect_model is None:
            raise RuntimeError(
                "Vehicle defect model is not loaded."
            )

        feature_vector = self._prepare_defect_input(
            station_features,
            station_state,
            vehicle_features,
            vehicle_state,
        )

        risk_score, confidence = self._inference(
            self.defect_model,
            feature_vector,
        )

        self._validate_prediction(
            risk_score,
            confidence,
        )

        return self.prediction_repository.save_prediction(
            timestamp=timezone.now(),
            entity_type="VEHICLE",
            entity_id=vehicle_features.vehicle.vehicle_id,
            risk_type="DEFECT",
            prediction_target="QUALITY_DEFECT",
            risk_score=risk_score,
            confidence=confidence,
            prediction_horizon_minutes=self.prediction_horizon,
            model_name=self.defect_model_name,
            model_version=self.defect_model_version,
        )

    # ==================================================================
    # FEATURE PREPARATION
    # ==================================================================

    def _prepare_station_risk_input(
        self,
        station_features,
        station_state,
    ):
        """
        Prepare the exact 8-feature vector expected by the station model.
        """

        try:
            feature_vector = [
                station_features.avg_cycle_time or 0.0,
                station_features.cycle_time_std or 0.0,
                station_features.cycle_time_trend or 0.0,
                station_features.throughput or 0.0,
                station_features.temperature_mean or 0.0,
                station_features.vibration_mean or 0.0,
                station_features.utilization or 0.0,
                station_state.current_cycle_time or 0.0,
            ]

            self._validate_feature_vector(
                feature_vector,
                expected_length=len(self.STATION_RISK_FEATURES),
                model_type="station risk",
            )

            return feature_vector

        except AttributeError as exc:
            logger.error(
                "Missing required station field: %s",
                exc,
            )

            raise ValueError(
                f"Invalid station input: {exc}"
            ) from exc

    def _prepare_defect_input(
        self,
        station_features,
        station_state,
        vehicle_features,
        vehicle_state,
    ):
        """
        Prepare the exact 8-feature vector expected by the vehicle model.
        """

        try:
            feature_vector = [
                station_features.avg_cycle_time or 0.0,
                station_features.temperature_mean or 0.0,
                station_features.vibration_mean or 0.0,
                station_features.utilization or 0.0,
                station_state.current_cycle_time or 0.0,
                vehicle_features.avg_cycle_time or 0.0,
                vehicle_features.cycle_time_deviation or 0.0,
                vehicle_features.quality_event_count or 0.0,
            ]

            self._validate_feature_vector(
                feature_vector,
                expected_length=len(self.DEFECT_RISK_FEATURES),
                model_type="vehicle defect",
            )

            return feature_vector

        except AttributeError as exc:
            logger.error(
                "Missing required vehicle/station field: %s",
                exc,
            )

            raise ValueError(
                f"Invalid vehicle/station input: {exc}"
            ) from exc

    # ==================================================================
    # INFERENCE
    # ==================================================================

    def _inference(
        self,
        model,
        feature_vector,
    ):
        """
        Execute sklearn model inference.

        Returns:
            (risk_score, confidence)

        risk_score:
            Probability of positive class (class 1).

        confidence:
            Highest probability returned by the classifier.

        Important:
            We only use model.classes_ when it is actually iterable.
            This is important for unittest.mock.Mock objects used by tests.
        """

        try:
            X = [feature_vector]

            # ----------------------------------------------------------
            # Preferred path: predict_proba
            # ----------------------------------------------------------

            if callable(getattr(model, "predict_proba", None)):

                probabilities = model.predict_proba(X)[0]

                # Convert numpy values / other numeric types to floats.
                probabilities = [
                    float(probability)
                    for probability in probabilities
                ]

                if len(probabilities) == 0:
                    raise ValueError(
                        "Model returned an empty probability array."
                    )

                # ------------------------------------------------------
                # Determine positive-class index.
                #
                # Real sklearn RandomForest:
                #     classes_ = [0, 1]
                #
                # Mock test object:
                #     classes_ may itself be a Mock.
                #
                # Therefore we safely inspect it.
                # ------------------------------------------------------

                positive_idx = None

                classes = getattr(
                    model,
                    "classes_",
                    None,
                )

                # A real sklearn classes_ is iterable.
                if classes is not None:

                    try:
                        classes_list = list(classes)

                        if len(classes_list) == len(probabilities):

                            if 1 in classes_list:
                                positive_idx = classes_list.index(1)

                    except (TypeError, ValueError):
                        # Mock or non-iterable classes_.
                        positive_idx = None

                # ------------------------------------------------------
                # Backward-compatible fallback.
                #
                # Our binary models use:
                #
                # [P(class 0), P(class 1)]
                #
                # Therefore class 1 is index 1.
                # ------------------------------------------------------

                if positive_idx is None:

                    if len(probabilities) > 1:
                        positive_idx = 1
                    else:
                        positive_idx = 0

                risk_score = probabilities[positive_idx]

                confidence = max(probabilities)

                return (
                    float(risk_score),
                    float(confidence),
                )

            # ----------------------------------------------------------
            # Fallback for classifiers without predict_proba
            # ----------------------------------------------------------

            if callable(getattr(model, "predict", None)):

                prediction = model.predict(X)[0]

                risk_score = float(prediction)

                confidence = 1.0

                return (
                    risk_score,
                    confidence,
                )

            raise RuntimeError(
                "Model does not implement predict_proba() or predict()."
            )

        except ValueError:
            # Validation errors should remain ValueError so tests and
            # callers can distinguish invalid model output from inference
            # infrastructure failures.
            raise

        except Exception as exc:

            logger.exception(
                "Model inference failed."
            )

            raise RuntimeError(
                f"Model inference failed: {exc}"
            ) from exc

    # ==================================================================
    # VALIDATION
    # ==================================================================

    def _validate_feature_vector(
        self,
        feature_vector,
        expected_length,
        model_type,
    ):
        """
        Validate the size and numerical validity of a feature vector.
        """

        if len(feature_vector) != expected_length:
            raise ValueError(
                f"{model_type.title()} model expected "
                f"{expected_length} features but received "
                f"{len(feature_vector)}."
            )

        for index, value in enumerate(feature_vector):

            try:
                numeric_value = float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Invalid feature at index {index}: {value}"
                ) from exc

            if not (
                numeric_value == numeric_value
            ):
                raise ValueError(
                    f"Feature at index {index} is NaN."
                )

    def _validate_prediction(
        self,
        risk_score,
        confidence,
    ):
        """
        Ensure model outputs are valid probabilities.
        """

        risk_score = float(risk_score)
        confidence = float(confidence)

        if not 0.0 <= risk_score <= 1.0:
            raise ValueError(
                f"Invalid risk score: {risk_score}. "
                "Must be in [0, 1]."
            )

        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                f"Invalid confidence: {confidence}. "
                "Must be in [0, 1]."
            )

        return True