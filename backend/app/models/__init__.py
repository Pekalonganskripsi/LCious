"""
Import all models for easy access
This file makes all models available when importing from app.models
"""
from app.models.user import User, Customer, Merchant, UserRole
from app.models.menu import Menu, MenuCategory
from app.models.fuzzy import FuzzyCriteria, CustomerPreference
from app.models.rating import Rating
from app.models.research import UserSimilarityMatrix, RecommendationLog, AlgorithmEvaluation
from app.models.algorithm import AlgorithmParameters
from app.models.evaluation_results import EvaluationResults

__all__ = [
    # User models
    "User",
    "Customer",
    "Merchant",
    "UserRole",

    # Content models
    "Menu",
    "MenuCategory",

    # Fuzzy models
    "FuzzyCriteria",
    "CustomerPreference",

    # Interaction models
    "Rating",

    # Research models
    "UserSimilarityMatrix",
    "RecommendationLog",
    "AlgorithmEvaluation",

    # Algorithm models
    "AlgorithmParameters",

    # Evaluation results
    "EvaluationResults",
]
