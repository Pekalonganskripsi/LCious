"""
Background Workers Module

Contains all background worker processes for automated system maintenance.
"""
from app.workers.evaluation_worker import (
    UltraFastEvaluationWorker,
    evaluation_worker,
    run_scheduled_evaluation,
    run_event_driven_evaluation
)

# For backwards compatibility
EvaluationWorker = UltraFastEvaluationWorker
FastEvaluationWorker = UltraFastEvaluationWorker

__all__ = [
    "UltraFastEvaluationWorker",
    "EvaluationWorker",      # Backwards compatibility
    "FastEvaluationWorker",  # Backwards compatibility
    "evaluation_worker",
    "run_scheduled_evaluation",
    "run_event_driven_evaluation",
]