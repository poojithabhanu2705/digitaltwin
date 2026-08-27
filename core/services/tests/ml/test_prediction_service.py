import unittest
from unittest.mock import Mock, MagicMock
from core.services.ml.prediction_service import PredictionService
from django.utils import timezone

class TestPredictionService(unittest.TestCase):
    def setUp(self):
        self.mock_repo = Mock()
        self.mock_repo.save_prediction.return_value = "MockedRiskPrediction"
        
        self.mock_model = Mock()
        self.mock_model.__class__.__name__ = "MockModel"
        # Probabilities: [Class 0: 0.2, Class 1: 0.8] -> risk_score = 0.8, confidence = 0.8
        self.mock_model.predict_proba.return_value = [[0.2, 0.8]]
        
        self.service = PredictionService(
            prediction_repository=self.mock_repo,
            risk_model=self.mock_model
        )
        
        # Mocking Django ORM dependencies dynamically
        self.station_feature = MagicMock()
        self.station_feature.station.station_id = "ST-01"
        self.station_feature.avg_cycle_time = 45.5
        
        self.station_state = MagicMock()
        self.station_state.current_cycle_time = 50.1

    def test_station_risk_success(self):
        result = self.service.predict(self.station_feature, self.station_state)
        
        # Assert inference was called correctly
        self.mock_model.predict_proba.assert_called_once()
        
        # Assert repository was called with correct probability values
        self.mock_repo.save_prediction.assert_called_once()
        call_args = self.mock_repo.save_prediction.call_args[1]
        
        self.assertEqual(call_args["entity_id"], "ST-01")
        self.assertEqual(call_args["risk_score"], 0.8)
        self.assertEqual(call_args["confidence"], 0.8)
        self.assertEqual(result, "MockedRiskPrediction")

    def test_validation_bounds(self):
        # Override to return invalid probabilities
        self.mock_model.predict_proba.return_value = [[-0.1, 1.2]]
        with self.assertRaises(ValueError):
            self.service.predict(self.station_feature, self.station_state)