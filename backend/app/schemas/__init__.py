"""
Import all schemas for easy access
"""
from app.schemas.user import (
    UserBase, UserCreate, UserUpdate, UserResponse, UserInDB,
    LoginRequest, TokenResponse, TokenPayload,
    CustomerBase, CustomerCreate, CustomerUpdate, CustomerResponse, CustomerWithUser,
    CustomerPreferenceBase, CustomerPreferenceCreate, CustomerPreferenceUpdate, CustomerPreferenceResponse,
    MerchantBase, MerchantCreate, MerchantUpdate, MerchantResponse, MerchantWithUser
)
from app.schemas.menu import (
    MenuBase, MenuCreate, MenuUpdate, MenuResponse, MenuWithMerchant,
    RatingBase, RatingCreate, RatingUpdate, RatingResponse, RatingWithDetails,
    FuzzyCriteriaBase, FuzzyCriteriaCreate, FuzzyCriteriaUpdate, FuzzyCriteriaResponse
)
from app.schemas.recommendation import (
    RecommendationRequest, RecommendationItem, RecommendationScoreBreakdown,
    RecommendationScores, RecommendationResponse, RecommendationListResponse,
    RatingPredictionRequest, RatingPredictionResponse,
    UserSimilarityResponse, SimilarityMatrixResponse,
    AlgorithmEvaluationRequest, AlgorithmEvaluationResponse, AlphaComparisonResult,
    CrossValidationResponse, ExportRequest, ExportResponse
)

__all__ = [
    # User schemas
    "UserBase", "UserCreate", "UserUpdate", "UserResponse", "UserInDB",
    "LoginRequest", "TokenResponse", "TokenPayload",

    # Customer schemas
    "CustomerBase", "CustomerCreate", "CustomerUpdate", "CustomerResponse", "CustomerWithUser",

    # Customer Preference schemas
    "CustomerPreferenceBase", "CustomerPreferenceCreate", "CustomerPreferenceUpdate", "CustomerPreferenceResponse",

    # Merchant schemas
    "MerchantBase", "MerchantCreate", "MerchantUpdate", "MerchantResponse", "MerchantWithUser",

    # Menu schemas
    "MenuBase", "MenuCreate", "MenuUpdate", "MenuResponse", "MenuWithMerchant",

    # Rating schemas
    "RatingBase", "RatingCreate", "RatingUpdate", "RatingResponse", "RatingWithDetails",

    # Fuzzy Criteria schemas
    "FuzzyCriteriaBase", "FuzzyCriteriaCreate", "FuzzyCriteriaUpdate", "FuzzyCriteriaResponse",

    # Recommendation schemas
    "RecommendationRequest", "RecommendationItem", "RecommendationScoreBreakdown",
    "RecommendationScores", "RecommendationResponse", "RecommendationListResponse",

    # Rating Prediction schemas
    "RatingPredictionRequest", "RatingPredictionResponse",

    # Similarity Matrix schemas
    "UserSimilarityResponse", "SimilarityMatrixResponse",

    # Evaluation schemas
    "AlgorithmEvaluationRequest", "AlgorithmEvaluationResponse", "AlphaComparisonResult",
    "CrossValidationResponse",

    # Export schemas
    "ExportRequest", "ExportResponse",
]
