import pytest
import numpy as np
from unittest.mock import Mock, patch
from ml.explanation_service import ExplanationService

@pytest.fixture
def mock_repository():
    return Mock()

@pytest.fixture
def mock_prediction():
    prediction = Mock()
    prediction.prediction_id = 999
    prediction.risk_type = "BOTTLENECK"
    return prediction

@pytest.fixture
def mock_model():
    return Mock()

@pytest.fixture
def service(mock_repository, mock_model):
    return ExplanationService(
        explanation_repository=mock_repository,
        risk_model=mock_model
    )

def test_1_basic_explanation_generation(service, mock_prediction):
    feature_input = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    
    with patch("shap.TreeExplainer") as MockExplainer:
        mock_explainer_instance = Mock()
        # Mock SHAP returning list of arrays (simulating binary classification)
        mock_explainer_instance.shap_values.return_value = [
            np.array([[-0.1] * 8]), 
            np.array([[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]])
        ]
        MockExplainer.return_value = mock_explainer_instance
        
        result = service.explain(mock_prediction, feature_input)
        
        assert len(result) == 8
        assert result[0].prediction == mock_prediction

def test_2_feature_contribution_count(service, mock_prediction):
    feature_input = [1.0] * 8
    
    with patch("shap.TreeExplainer") as MockExplainer:
        mock_explainer_instance = Mock()
        mock_explainer_instance.shap_values.return_value = [np.zeros((1, 8)), np.ones((1, 8))]
        MockExplainer.return_value = mock_explainer_instance
        
        result = service.explain(mock_prediction, feature_input)
        assert len(result) == 8

def test_3_feature_ordering(service, mock_prediction):
    feature_input = [1.0] * 8
    
    with patch("shap.TreeExplainer") as MockExplainer:
        mock_explainer_instance = Mock()
        # Return unique values to trace them
        mock_explainer_instance.shap_values.return_value = [
            np.zeros((1, 8)), 
            np.array([[10, 20, 30, 40, 50, 60, 70, 80]])
        ]
        MockExplainer.return_value = mock_explainer_instance
        
        result = service.explain(mock_prediction, feature_input)
        
        # Sort back to original model order to verify mapping
        original_order = sorted(result, key=lambda x: x.contribution)
        assert original_order[0].feature_name == "avg_cycle_time"
        assert original_order[-1].feature_name == "current_cycle_time"

def test_4_and_5_positive_and_negative_contribution(service, mock_prediction):
    feature_input = [1.0] * 8
    
    with patch("shap.TreeExplainer") as MockExplainer:
        mock_explainer_instance = Mock()
        mock_explainer_instance.shap_values.return_value = [
            np.zeros((1, 8)), 
            np.array([[0.32, -0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
        ]
        MockExplainer.return_value = mock_explainer_instance
        
        result = service.explain(mock_prediction, feature_input)
        
        positive_exp = next(x for x in result if x.feature_name == "avg_cycle_time")
        negative_exp = next(x for x in result if x.feature_name == "cycle_time_std")
        
        assert positive_exp.contribution == 0.32
        assert positive_exp.direction == "POSITIVE"
        
        assert negative_exp.contribution == -0.25
        assert negative_exp.direction == "NEGATIVE"

def test_6_ranking(service, mock_prediction):
    feature_input = [1.0] * 8
    
    with patch("shap.TreeExplainer") as MockExplainer:
        mock_explainer_instance = Mock()
        mock_explainer_instance.shap_values.return_value = [
            np.zeros((1, 8)), 
            np.array([[0.10, -0.40, 0.20, 0.0, 0.0, 0.0, 0.0, 0.0]])
        ]
        MockExplainer.return_value = mock_explainer_instance
        
        result = service.explain(mock_prediction, feature_input)
        
        assert result[0].contribution == -0.40
        assert result[1].contribution == 0.20
        assert result[2].contribution == 0.10

def test_7_missing_feature():
    # Empty feature vector
    service = ExplanationService(explanation_repository=Mock())
    with pytest.raises(ValueError):
        service.explain(Mock(prediction_id=1, risk_type="BOTTLENECK"), [])

def test_8_feature_dimension_mismatch(service, mock_prediction):
    # Model expects 8 features, passing 7
    feature_input = [1.0] * 7 
    with pytest.raises(ValueError, match="dimension mismatch"):
        service.explain(mock_prediction, feature_input)

def test_9_invalid_prediction(service):
    # No prediction ID
    invalid_pred = Mock(prediction_id=None)
    with pytest.raises(ValueError):
        service.explain(invalid_pred, [1.0] * 8)

def test_10_model_unavailable():
    # Service init without models
    service = ExplanationService(explanation_repository=Mock())
    with pytest.raises(RuntimeError, match="unavailable"):
        service.explain(Mock(prediction_id=1, risk_type="BOTTLENECK"), [1.0] * 8)

def test_11_shap_failure(service, mock_prediction):
    feature_input = [1.0] * 8
    with patch("shap.TreeExplainer") as MockExplainer:
        MockExplainer.side_effect = Exception("SHAP crashed")
        with pytest.raises(RuntimeError, match="SHAP computation failed"):
            service.explain(mock_prediction, feature_input)

def test_12_and_13_repository_persistence(service, mock_prediction):
    feature_input = [1.0] * 8
    with patch("shap.TreeExplainer") as MockExplainer:
        mock_explainer_instance = Mock()
        mock_explainer_instance.shap_values.return_value = [np.zeros((1, 8)), np.ones((1, 8))]
        MockExplainer.return_value = mock_explainer_instance
        
        result = service.explain(mock_prediction, feature_input)
        
        # Assert repository was called, not Django ORM direct create
        service.explanation_repository.bulk_save_explanations.assert_called_once_with(result)

def test_14_positive_class_consistency(service, mock_prediction):
    feature_input = [1.0] * 8
    with patch("shap.TreeExplainer") as MockExplainer:
        mock_explainer_instance = Mock()
        # Mock class 0 (negative) and class 1 (positive - high risk)
        class_0 = np.array([[-9.0] * 8])
        class_1 = np.array([[9.0] * 8])
        mock_explainer_instance.shap_values.return_value = [class_0, class_1]
        MockExplainer.return_value = mock_explainer_instance
        
        result = service.explain(mock_prediction, feature_input)
        
        # Verify class 1 (9.0) was used, not class 0 (-9.0)
        assert result[0].contribution == 9.0

def test_15_no_prediction_mutation(service, mock_prediction):
    feature_input = [1.0] * 8
    original_risk_type = mock_prediction.risk_type
    
    with patch("shap.TreeExplainer") as MockExplainer:
        mock_explainer_instance = Mock()
        mock_explainer_instance.shap_values.return_value = [np.zeros((1, 8)), np.ones((1, 8))]
        MockExplainer.return_value = mock_explainer_instance
        
        service.explain(mock_prediction, feature_input)
        
        assert mock_prediction.risk_type == original_risk_type