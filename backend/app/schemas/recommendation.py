"""
Recommendation-related Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# =====================
# Recommendation Request Schemas
# =====================

class RecommendationRequest(BaseModel):
    """Schema for recommendation request"""
    n: int = Field(default=20, ge=1, le=100, description="Number of recommendations")
    alpha: Optional[float] = Field(None, ge=0, le=1, description="Alpha weight for hybrid")
    k_neighbors: int = Field(default=10, ge=5, le=50, description="Number of neighbors for CF")
    adaptive_alpha: bool = Field(default=False, description="Use adaptive alpha")


class RecommendationItem(BaseModel):
    """Single recommendation item"""
    menu_id: str
    item_name: str
    merchant_id: str
    shop_name: str
    merchant_address: str
    price: float
    category: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    spice_level: Optional[int] = None
    sweetness_level: Optional[int] = None
    savory_level: Optional[int] = None
    cuisine_type: Optional[str] = None


class RecommendationScoreBreakdown(BaseModel):
    """Score breakdown for transparency"""
    price_score: float
    distance_score: float
    popularity_score: float
    taste_score: float
    cuisine_score: float
    distance_km: float


class RecommendationScores(BaseModel):
    """All scores for a recommendation"""
    fuzzy_score: float = Field(..., ge=0, le=1, description="Fuzzy preference match score")
    cf_score: float = Field(..., ge=0, le=1, description="Collaborative filtering score (normalized)")
    predicted_rating: float = Field(..., ge=1, le=5, description="Predicted rating from CF")
    hybrid_score: float = Field(..., ge=0, le=1, description="Final hybrid score")
    alpha_used: float = Field(..., ge=0, le=1, description="Alpha weight used")
    breakdown: RecommendationScoreBreakdown


class RecommendationResponse(BaseModel):
    """Complete recommendation response"""
    rank: int = Field(..., ge=1, description="Rank position")
    menu: RecommendationItem
    scores: RecommendationScores
    distance_km: float
    explanation: Optional[str] = None


class RecommendationListResponse(BaseModel):
    """List of recommendations"""
    customer_id: str
    total_recommendations: int
    alpha_used: float
    adaptive_used: bool
    recommendations: List[RecommendationResponse]
    generated_at: datetime


# =====================
# Rating Prediction Schema
# =====================

class RatingPredictionRequest(BaseModel):
    """Schema for rating prediction request"""
    menu_id: str
    k_neighbors: int = Field(default=10, ge=5, le=50)


class RatingPredictionResponse(BaseModel):
    """Schema for rating prediction response"""
    menu_id: str
    predicted_rating: float = Field(..., ge=1, le=5)
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Confidence score (optional)")
    k_neighbors_used: int


# =====================
# Similarity Matrix Schemas
# =====================

class UserSimilarityResponse(BaseModel):
    """User similarity response"""
    id: str
    user_id_1: str
    user_id_2: str
    similarity_score: float = Field(..., ge=-1, le=1)
    similarity_method: str
    common_items_rated: int
    created_at: datetime


class SimilarityMatrixResponse(BaseModel):
    """Similarity matrix response"""
    total_pairs: int
    method: str
    similarities: List[UserSimilarityResponse]


# =====================
# Algorithm Evaluation Schemas
# =====================

class AlgorithmEvaluationRequest(BaseModel):
    """Schema for algorithm evaluation request"""
    test_split: float = Field(default=0.2, ge=0.1, le=0.5, description="Test data split ratio")
    alpha_values: List[float] = Field(default=[0.2, 0.5, 0.8], description="Alpha values to test")
    k_folds: Optional[int] = Field(None, ge=2, le=10, description="Number of folds for cross-validation")


class AlphaComparisonResult(BaseModel):
    """Result for single alpha value"""
    alpha: float
    mae: float = Field(..., description="Mean Absolute Error")
    rmse: float = Field(..., description="Root Mean Square Error")
    hit_rate: float = Field(..., ge=0, le=1, description="Hit Rate")
    n_predictions: int


class AlgorithmEvaluationResponse(BaseModel):
    """Algorithm evaluation response"""
    test_split: float
    method: str = "train_test_split"
    results: List[AlphaComparisonResult]
    best_alpha: float = Field(..., description="Best alpha based on MAE")
    tested_at: datetime


class CrossValidationResponse(BaseModel):
    """Cross-validation results"""
    n_splits: int
    alpha_values: List[float]
    results: List[AlphaComparisonResult]
    best_config: dict
    completed_at: datetime


# =====================
# Research Data Export Schemas
# =====================

class ExportRequest(BaseModel):
    """Schema for data export request"""
    format: str = Field(default="csv", pattern="^(csv|excel|json)$")
    include_recommendation_logs: bool = True
    include_similarity_matrix: bool = True
    include_evaluation_results: bool = True
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None


class ExportResponse(BaseModel):
    """Export response"""
    file_url: str
    format: str
    records_count: int
    file_size_mb: float
    generated_at: datetime
    expires_at: datetime
