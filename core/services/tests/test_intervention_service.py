# tests/test_intervention_service.py

import pytest
from unittest.mock import Mock
from datetime import datetime

from decision.intervention_service import InterventionService
from core.models import Recommendation, InterventionExecution
from core.services.exceptions import (
    NotFoundError,
    ValidationError,
    ConflictError,
    InvalidStateTransitionError,
    ServiceError
)

@pytest.fixture
def mock_repo():
    return Mock()

@pytest.fixture
def service(mock_repo):
    return InterventionService(intervention_repository=mock_repo)

@pytest.fixture
def mock_recommendation():
    rec = Mock(spec=Recommendation)
    rec.recommendation_id = 1
    rec.status = "PENDING"
    rec.rationale = ""
    return rec

def test_execute_intervention_success(service, mock_repo, mock_recommendation):
    mock_repo.get_recommendation_by_id.return_value = mock_recommendation
    
    def mock_save_tx(rec, exec_rec):
        return exec_rec
        
    mock_repo.save_execution_transaction.side_effect = mock_save_tx

    result = service.execute_intervention(1, "Executed safely")

    assert result.status == "SUCCESS"
    assert result.execution_notes == "Executed safely"
    assert result.recommendation == mock_recommendation
    assert mock_recommendation.status == "EXECUTED"
    mock_repo.save_execution_transaction.assert_called_once()

def test_execute_intervention_missing_id(service):
    with pytest.raises(ValidationError) as exc:
        service.execute_intervention(None)
    assert "must be provided" in str(exc.value)

def test_execute_intervention_not_found(service, mock_repo):
    mock_repo.get_recommendation_by_id.return_value = None
    with pytest.raises(NotFoundError) as exc:
        service.execute_intervention(999)
    assert "was not found" in str(exc.value)

def test_execute_intervention_idempotency_conflict(service, mock_repo, mock_recommendation):
    mock_recommendation.status = "EXECUTED"
    mock_repo.get_recommendation_by_id.return_value = mock_recommendation

    with pytest.raises(ConflictError) as exc:
        service.execute_intervention(1)
    assert "already been executed" in str(exc.value)
    mock_repo.save_execution_transaction.assert_not_called()

def test_execute_intervention_invalid_transition(service, mock_repo, mock_recommendation):
    mock_recommendation.status = "REJECTED"
    mock_repo.get_recommendation_by_id.return_value = mock_recommendation

    with pytest.raises(InvalidStateTransitionError) as exc:
        service.execute_intervention(1)
    assert "Cannot transition" in str(exc.value)

def test_approve_recommendation_success(service, mock_repo, mock_recommendation):
    mock_repo.get_recommendation_by_id.return_value = mock_recommendation
    mock_repo.save_recommendation.return_value = mock_recommendation

    result = service.approve_recommendation(1, "Cost effective")

    assert result.status == "APPROVED"
    assert result.rationale == "Cost effective"
    mock_repo.save_recommendation.assert_called_once_with(mock_recommendation)

def test_reject_recommendation_success(service, mock_repo, mock_recommendation):
    mock_repo.get_recommendation_by_id.return_value = mock_recommendation
    mock_repo.save_recommendation.return_value = mock_recommendation

    result = service.reject_recommendation(1, "Too expensive")

    assert result.status == "REJECTED"
    assert result.rationale == "Too expensive"
    mock_repo.save_recommendation.assert_called_once_with(mock_recommendation)

def test_approve_invalid_transition(service, mock_repo, mock_recommendation):
    mock_recommendation.status = "EXECUTED"
    mock_repo.get_recommendation_by_id.return_value = mock_recommendation

    with pytest.raises(InvalidStateTransitionError):
        service.approve_recommendation(1)

def test_execute_intervention_db_failure(service, mock_repo, mock_recommendation):
    mock_repo.get_recommendation_by_id.return_value = mock_recommendation
    mock_repo.save_execution_transaction.side_effect = Exception("DB Error")

    with pytest.raises(ServiceError) as exc:
        service.execute_intervention(1)
    assert "Database error" in str(exc.value)

def test_immutability_of_input_reference(service, mock_repo, mock_recommendation):
    mock_repo.get_recommendation_by_id.return_value = mock_recommendation
    initial_cost = 5000.0
    mock_recommendation.cost = initial_cost
    
    mock_repo.save_execution_transaction.return_value = Mock(spec=InterventionExecution)
    service.execute_intervention(1)
    
    assert mock_recommendation.cost == initial_cost