"""
Import all algorithms for easy access
"""
from app.algorithms.fuzzy import FuzzyLogicEngine
from app.algorithms.collaborative_filtering import CollaborativeFilteringEngine
from app.algorithms.hybrid import HybridRecommender
from app.algorithms.evaluation import AlgorithmEvaluator

__all__ = [
    "FuzzyLogicEngine",
    "CollaborativeFilteringEngine",
    "HybridRecommender",
    "AlgorithmEvaluator",
]
