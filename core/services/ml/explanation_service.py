import logging
import numpy as np

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

from core.models import PredictionExplanation
from core.services.ml.prediction_service import PredictionService

logger = logging.getLogger(__name__)


class ExplanationService:
    """
    Service responsible for explaining ML predictions using SHAP values.
    It strictly explains the positive class (high risk / defect) and persists
    feature-level contributions without modifying the original prediction.
    """

    def __init__(
        self,
        explanation_repository,
        risk_model=None,
        defect_model=None
    ):
        self.explanation_repository = explanation_repository
        self.risk_model = risk_model
        self.defect_model = defect_model

    def explain(self, prediction, feature_input):
        """
        Generates and persists SHAP-based feature contributions for a given RiskPrediction.
        """
        self._validate_input(prediction, feature_input)

        # 1. Map target model and expected feature names based on risk type
        model, feature_names = self._get_model_context(prediction)

        # 2. Validate feature dimension
        if len(feature_input) != len(feature_names):
            raise ValueError(
                f"Feature dimension mismatch. Expected {len(feature_names)} features, "
                f"but got {len(feature_input)}."
            )

        # 3. Generate SHAP values
        contributions = self._generate_shap_contributions(model, feature_input)

        # 4. Construct and validate Explanation objects
        explanations = self._construct_explanations(prediction, feature_names, contributions)

        # 5. Persist through repository
        try:
            self.explanation_repository.bulk_save_explanations(explanations)
        except Exception as e:
            logger.error(f"Failed to persist explanations: {e}")
            raise RuntimeError(f"Repository persistence failure: {e}")

        return explanations

    def _validate_input(self, prediction, feature_input):
        if not SHAP_AVAILABLE:
            raise RuntimeError("SHAP library is not installed or unavailable in this environment.")
        
        if not prediction or not getattr(prediction, 'prediction_id', None):
            raise ValueError("A valid RiskPrediction with a prediction_id is required.")
            
        if not feature_input or len(feature_input) == 0:
            raise ValueError("Feature input vector cannot be empty.")

    def _get_model_context(self, prediction):
        if prediction.risk_type == "BOTTLENECK":
            if not self.risk_model:
                raise RuntimeError("Risk model is unavailable for explanation.")
            return self.risk_model, PredictionService.STATION_RISK_FEATURES
            
        elif prediction.risk_type == "DEFECT":
            if not self.defect_model:
                raise RuntimeError("Defect model is unavailable for explanation.")
            return self.defect_model, PredictionService.DEFECT_RISK_FEATURES
            
        else:
            raise ValueError(f"Unsupported risk_type for explanation: {prediction.risk_type}")

    def _generate_shap_contributions(self, model, feature_input):
        try:
            explainer = shap.TreeExplainer(model)
            # Reshape input to 2D array for SHAP
            shap_values_raw = explainer.shap_values(np.array([feature_input]))
        except Exception as e:
            logger.error(f"SHAP explanation generation failed: {e}")
            raise RuntimeError(f"SHAP computation failed: {e}")

        # Extract underlying values if shap.Explanation object
        if hasattr(shap_values_raw, "values"):
            shap_values_raw = shap_values_raw.values

        # Map to the positive class (index 1) for binary classification
        if isinstance(shap_values_raw, list):
            positive_idx = 1 if len(shap_values_raw) > 1 else 0
            raw = shap_values_raw[positive_idx]
            return raw[0] if getattr(raw, 'ndim', 1) > 1 else raw
        elif isinstance(shap_values_raw, np.ndarray):
            if shap_values_raw.ndim == 3:
                positive_idx = 1 if shap_values_raw.shape[2] > 1 else 0
                return shap_values_raw[0, :, positive_idx]
            elif shap_values_raw.ndim == 2:
                return shap_values_raw[0]
            elif shap_values_raw.ndim == 1:
                return shap_values_raw
            else:
                return shap_values_raw.flatten()
        else:
            arr = np.array(shap_values_raw)
            if arr.ndim > 1:
                return arr[0]
            return arr

    def _construct_explanations(self, prediction, feature_names, contributions):
        if len(contributions) != len(feature_names):
            raise ValueError("SHAP output dimension does not match feature dimension.")

        explanations = []
        for name, contrib in zip(feature_names, contributions):
            contrib_val = float(contrib)
            if not np.isfinite(contrib_val):
                raise ValueError(f"Non-finite SHAP contribution generated for feature '{name}'.")

            direction = "POSITIVE" if contrib_val >= 0 else "NEGATIVE"
            
            exp = PredictionExplanation(
                prediction=prediction,
                feature_name=name,
                contribution=contrib_val,
                direction=direction
            )
            explanations.append(exp)

        # Rank by absolute magnitude descending to prioritize highly impactful features (both positive and negative)
        explanations.sort(key=lambda x: abs(x.contribution), reverse=True)
        return explanations