import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class RootCauseService:
    """
    Service responsible for deterministic, evidence-based root-cause reasoning.
    It evaluates ML explanations, feature values, state data, and events to 
    rank physical/operational root causes, without modifying the underlying prediction.
    """

    # Heuristic mapping of feature names to RootCause (category, name)
    FEATURE_TO_ROOT_CAUSE = {
        "vibration_mean": ("EQUIPMENT_DEGRADATION", "Abnormal Vibration"),
        "temperature_mean": ("THERMAL_ISSUE", "Overheating"),
        "avg_cycle_time": ("PROCESS_DEGRADATION", "Prolonged Cycle Time"),
        "cycle_time_trend": ("PROCESS_DEGRADATION", "Deteriorating Cycle Time"),
        "utilization": ("PROCESS_DEGRADATION", "Over-utilization"),
        "quality_event_count": ("QUALITY_ISSUE", "Frequent Defects"),
        "throughput": ("PROCESS_DEGRADATION", "Throughput Deviation"),
        "current_cycle_time": ("PROCESS_DEGRADATION", "Current Cycle Time Spike"),
    }

    def __init__(self, root_cause_repo, prediction_root_cause_repo):
        self.root_cause_repo = root_cause_repo
        self.prc_repo = prediction_root_cause_repo
        self.min_confidence_threshold = 0.1

    def analyze(self, prediction, explanations, features, state, events=None):
        """
        Analyzes evidence to determine the most likely root cause.
        Returns a persisted PredictionRootCause instance.
        """
        self._validate_inputs(prediction, explanations, features, state)

        scores = defaultdict(float)
        evidence_log = defaultdict(list)

        # 1. Evaluate Explanation Evidence (SHAP values)
        for exp in explanations:
            # Only features that pushed the model TOWARD high risk (POSITIVE direction) count as root cause evidence
            if exp.direction == "POSITIVE" and exp.contribution > 0:
                mapping = self.FEATURE_TO_ROOT_CAUSE.get(exp.feature_name)
                if mapping:
                    category, name = mapping
                    rc_key = (category, name)
                    scores[rc_key] += exp.contribution
                    evidence_log[rc_key].append(
                        f"ML Model strongly weighted {exp.feature_name} (contribution: +{exp.contribution:.2f})"
                    )

        # 2. Evaluate State Evidence
        if hasattr(state, "health_state") and state.health_state == "DEGRADED":
            rc_key = ("EQUIPMENT_DEGRADATION", "General Equipment Degradation")
            scores[rc_key] += 0.30
            evidence_log[rc_key].append("Station state explicitly reports DEGRADED health.")

        # 3. Evaluate Event Evidence (Optional)
        if events:
            for event in events:
                if hasattr(event, "maintenance_type"):
                    rc_key = ("EQUIPMENT_DEGRADATION", "Recent Maintenance")
                    scores[rc_key] += 0.20
                    evidence_log[rc_key].append(f"Recent maintenance event recorded: {event.maintenance_type}")
                elif hasattr(event, "defect_type"):
                    rc_key = ("QUALITY_ISSUE", "Recent Defect")
                    scores[rc_key] += 0.20
                    evidence_log[rc_key].append(f"Recent quality defect detected: {event.defect_type}")

        # 4. Rank and Calculate Confidence
        best_rc_key, best_score, confidence, final_evidence = self._resolve_best_cause(scores, evidence_log)

        # 5. Get or Create Master RootCause record
        master_rc = self._get_or_create_master_rc(best_rc_key[0], best_rc_key[1])

        # 6. Persist and return PredictionRootCause
        return self.prc_repo.create(
            prediction=prediction,
            root_cause=master_rc,
            contribution=best_score,
            confidence=confidence,
            evidence="\n".join(final_evidence)
        )

    def _validate_inputs(self, prediction, explanations, features, state):
        if not prediction or not getattr(prediction, 'prediction_id', None):
            raise ValueError("Invalid prediction object.")
        if not features or not state:
            raise ValueError("Features and state are required to analyze root causes.")
        
        for exp in explanations:
            if exp.prediction_id != prediction.prediction_id:
                raise ValueError("Mismatch: Explanation does not belong to the provided prediction.")

    def _resolve_best_cause(self, scores, evidence_log):
        if not scores:
            return ("UNKNOWN", "Insufficient Evidence"), 0.0, 0.0, ["No supporting evidence exceeded thresholds."]

        # Sort by score descending
        sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        best_rc_key, best_score = sorted_scores[0]
        
        if best_score < self.min_confidence_threshold:
            return ("UNKNOWN", "Insufficient Evidence"), best_score, 0.0, ["Available evidence fell below confidence threshold."]

        # Calculate heuristic confidence: best_score vs sum of top two
        second_best_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0.0
        confidence = min(1.0, best_score / (best_score + second_best_score + 0.1))

        return best_rc_key, float(best_score), float(confidence), evidence_log[best_rc_key]

    def _get_or_create_master_rc(self, category, name):
        rc = self.root_cause_repo.get_by_name(category, name)
        if not rc:
            rc = self.root_cause_repo.create(
                category=category,
                name=name,
                description=f"Auto-generated category for {name}"
            )
        return rc