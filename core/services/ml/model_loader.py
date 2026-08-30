from pathlib import Path
import joblib
import logging

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[3]
MODEL_DIR = BASE_DIR / "ml" / "models"

STATION_RISK_MODEL_PATH = MODEL_DIR / "station_risk_model.joblib"
VEHICLE_DEFECT_MODEL_PATH = MODEL_DIR / "vehicle_defect_model.joblib"


class MLModelLoader:
    """
    Loads and caches the trained TwinSight ML models.

    Models are loaded once and reused for inference.
    """

    _station_risk_model = None
    _vehicle_defect_model = None

    @classmethod
    def load_station_risk_model(cls):
        if cls._station_risk_model is None:
            if not STATION_RISK_MODEL_PATH.exists():
                raise FileNotFoundError(
                    f"Station risk model not found: "
                    f"{STATION_RISK_MODEL_PATH}"
                )

            logger.info(
                "Loading Station Risk model from %s",
                STATION_RISK_MODEL_PATH,
            )

            cls._station_risk_model = joblib.load(
                STATION_RISK_MODEL_PATH
            )

        return cls._station_risk_model

    @classmethod
    def load_vehicle_defect_model(cls):
        if cls._vehicle_defect_model is None:
            if not VEHICLE_DEFECT_MODEL_PATH.exists():
                raise FileNotFoundError(
                    f"Vehicle defect model not found: "
                    f"{VEHICLE_DEFECT_MODEL_PATH}"
                )

            logger.info(
                "Loading Vehicle Defect model from %s",
                VEHICLE_DEFECT_MODEL_PATH,
            )

            cls._vehicle_defect_model = joblib.load(
                VEHICLE_DEFECT_MODEL_PATH
            )

        return cls._vehicle_defect_model

    @classmethod
    def load_all(cls):
        """
        Load both models and return them as a dictionary.
        """

        return {
            "station_risk": cls.load_station_risk_model(),
            "vehicle_defect": cls.load_vehicle_defect_model(),
        }

    @classmethod
    def clear_cache(cls):
        """
        Clear cached models.
        Useful for tests or model replacement.
        """

        cls._station_risk_model = None
        cls._vehicle_defect_model = None
        