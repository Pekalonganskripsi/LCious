"""
Recommendation API endpoints

Main API for generating personalized recommendations using Hybrid Fuzzy-Collaborative Filtering
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import time

from app.api.deps import get_db, get_current_user, get_current_customer
from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    RecommendationListResponse,
    RatingPredictionRequest,
    RatingPredictionResponse
)
from app.schemas.user import CustomerPreferenceResponse
from app.algorithms import HybridRecommender
from app.models.user import User, Customer
from app.models.fuzzy import CustomerPreference
from app.models.algorithm import AlgorithmParameters
from app.core.config import settings

router = APIRouter()


def get_algorithm_param(db: Session, param_name: str, default_value):
    """
    Helper to get algorithm parameter from database with fallback to default
    """
    try:
        param = db.query(AlgorithmParameters).filter(
            AlgorithmParameters.parameter_name == param_name
        ).first()
        return param.parameter_value if param else default_value
    except:
        return default_value


def get_customer_preferences_dict(db: Session, customer_id: str) -> dict:
    """
    Helper to get customer preferences as dictionary

    Args:
        db: Database session
        customer_id: Customer UUID

    Returns:
        Dictionary with customer preferences
    """
    preference = db.query(CustomerPreference).filter(
        CustomerPreference.customer_id == customer_id
    ).first()

    if not preference:
        # Return default preferences
        return {
            'pref_price_importance': 0.5,
            'pref_price_sensitivity': 'medium',
            'pref_distance_importance': 0.3,
            'pref_max_distance_km': 10,
            'pref_popularity_importance': 0.2,
            'pref_spice_level': 0,
            'pref_sweetness_level': 0,
            'pref_savory_level': 0,
            'pref_cuisines': [],
            'pref_dietary_restrictions': []
        }

    return {
        'pref_price_importance': float(preference.pref_price_importance or 0.5),
        'pref_price_sensitivity': preference.pref_price_sensitivity or 'medium',
        'pref_distance_importance': float(preference.pref_distance_importance or 0.3),
        'pref_max_distance_km': int(preference.pref_max_distance_km or 10),
        'pref_popularity_importance': float(preference.pref_popularity_importance or 0.2),
        'pref_spice_level': int(preference.pref_spice_level or 0),
        'pref_sweetness_level': int(preference.pref_sweetness_level or 0),
        'pref_savory_level': int(preference.pref_savory_level or 0),
        'pref_cuisines': (preference.pref_cuisines.split(',') if preference.pref_cuisines and isinstance(preference.pref_cuisines, str) else preference.pref_cuisines or []),
        'pref_dietary_restrictions': (preference.pref_dietary_restrictions.split(',') if preference.pref_dietary_restrictions and isinstance(preference.pref_dietary_restrictions, str) else preference.pref_dietary_restrictions or [])
    }


@router.post("/my-recommendations", response_model=RecommendationListResponse)
async def get_personalized_recommendations(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Generate personalized recommendations using Hybrid Fuzzy-Collaborative Filtering

    ## Algorithm

    This endpoint uses the hybrid recommendation system:

    **Hscore(u,i) = (alpha * Sf(u,i)) + ((1-alpha) * Pcf(u,i)/Rmax)**

    Where:
    - **Sf(u,i)**: Fuzzy score based on your preferences (price, distance, taste)
    - **Pcf(u,i)**: Predicted rating from collaborative filtering (community patterns)
    - **alpha**: Weight parameter (default: 0.5 for balanced)

    ## Parameters

    - **n**: Number of recommendations (1-100, default: 20)
    - **alpha**: Weight parameter (0-1, default: null -> use adaptive)
        - 0.0 = Pure Collaborative Filtering
        - 0.5 = Balanced (recommended)
        - 1.0 = Pure Fuzzy Logic
    - **k_neighbors**: Number of similar users for CF (5-50, default: 10)
    - **adaptive_alpha**: Use adaptive alpha based on your rating history (default: false)

    ## Adaptive Alpha

    If adaptive_alpha=true:
    - New users (0-5 ratings): alpha = 0.8 -> favor Fuzzy (cold start)
    - Medium users (6-20 ratings): alpha = 0.5 -> balanced
    - Active users (20+ ratings): alpha = 0.2 -> favor CF

    ## Response

    Returns ranked list of menus with:
    - Menu details (name, price, category, etc.)
    - Scores breakdown (fuzzy, CF, hybrid)
    - Predicted rating
    - Distance from your location
    - Explanation of why it was recommended

    ## Research Transparency

    All recommendations are logged to database for research analysis.
    You can view your recommendation history in the research dashboard.
    """

    # Get customer
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )

    # Get customer preferences
    customer_pref = get_customer_preferences_dict(db, customer.id)

    # Get customer location
    try:
        customer_location = (
            float(customer.latitude) if customer.latitude else -6.2088,
            float(customer.longitude) if customer.longitude else 106.8456
        )
    except:
        # Default to Jakarta if location invalid
        customer_location = (-6.2088, 106.8456)

    # Initialize recommender with parameters from database
    default_alpha = get_algorithm_param(db, "default_alpha", settings.DEFAULT_ALPHA)
    default_k_neighbors = int(get_algorithm_param(db, "default_k_neighbors", settings.DEFAULT_K_NEIGHBORS))

    alpha = request.alpha if request.alpha is not None else default_alpha
    k_neighbors = request.k_neighbors if request.k_neighbors is not None else default_k_neighbors

    recommender = HybridRecommender(db, alpha=alpha)

    # Generate recommendations
    start_time = time.time()

    recommendations = recommender.generate_recommendations(
        customer_id=str(customer.id),
        customer_pref=customer_pref,
        customer_location=customer_location,
        n_recommendations=request.n,
        alpha=alpha,
        k_neighbors=k_neighbors,
        adaptive_alpha=request.adaptive_alpha
    )

    generation_time = time.time() - start_time

    # Log recommendations for research
    try:
        recommender.log_recommendations(str(customer.id), recommendations)
    except Exception as e:
        # Don't fail request if logging fails
        print(f"Error logging recommendations: {e}")

    # Convert to response format
    from app.schemas.recommendation import (
        RecommendationItem,
        RecommendationScoreBreakdown,
        RecommendationScores
    )

    recommendation_responses = []

    for rec in recommendations:
        try:
            # Create menu item - exclude 'id' and 'popularity_score' as they're not in schema
            menu_data = {k: v for k, v in rec['menu'].items() if k not in ['id', 'popularity_score']}
            menu_item = RecommendationItem(**menu_data)

            # Create score breakdown
            breakdown_data = rec['scores']['breakdown']['fuzzy_breakdown'].copy()
            breakdown_data['distance_km'] = rec['scores']['breakdown']['distance_km']
            breakdown = RecommendationScoreBreakdown(**breakdown_data)

            # Create scores
            scores = RecommendationScores(
                breakdown=breakdown,
                **{k: v for k, v in rec['scores'].items() if k != 'breakdown'}
            )

            # Get explanation
            explanation = recommender.get_recommendation_explanation(rec)

            # Create response
            recommendation_responses.append(RecommendationResponse(
                rank=rec['rank'],
                menu=menu_item,
                scores=scores,
                distance_km=rec['distance_km'],
                explanation=explanation
            ))
        except Exception as e:
            print(f"Error creating response: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Determine actual alpha used
    alpha_used = alpha
    if recommendations:
        alpha_used = recommendations[0]['scores']['alpha_used']

    return RecommendationListResponse(
        customer_id=str(customer.id),
        total_recommendations=len(recommendation_responses),
        alpha_used=alpha_used,
        adaptive_used=request.adaptive_alpha,
        recommendations=recommendation_responses,
        generated_at=datetime.utcnow()
    )


@router.get("/my-recommendations", response_model=RecommendationListResponse)
async def get_recommendations_quick(
    n: int = Query(20, ge=1, le=100, description="Number of recommendations"),
    alpha: Optional[float] = Query(None, ge=0, le=1, description="Alpha weight"),
    k_neighbors: int = Query(10, ge=5, le=50, description="K neighbors for CF"),
    adaptive: bool = Query(False, description="Use adaptive alpha"),
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Quick GET endpoint for recommendations (simpler parameters)

    Same functionality as POST endpoint but with query parameters
    """
    request = RecommendationRequest(
        n=n,
        alpha=alpha,
        k_neighbors=k_neighbors,
        adaptive_alpha=adaptive
    )

    return await get_personalized_recommendations(request, current_user, db)


@router.post("/predict-rating", response_model=RatingPredictionResponse)
async def predict_menu_rating(
    prediction_request: RatingPredictionRequest,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Predict rating for a specific menu item

    Uses Collaborative Filtering to predict what rating you would give
    to a menu based on similar users' ratings.

    ## Algorithm

    **Pcf(u,i) = R̄u + (Σ sim(u,v) × (Rv,i - R̄v)) / Σ|sim(u,v)|**

    Where:
    - **R̄u**: Your average rating
    - **sim(u,v)**: Similarity between you and user v (Pearson correlation)
    - **Rv,i**: User v's rating for this menu

    ## Parameters

    - **menu_id**: ID of menu to predict rating for
    - **k_neighbors**: Number of similar users to consider (default: 10)

    ## Returns

    - **predicted_rating**: Predicted rating from 1 to 5
    - **k_neighbors_used**: Actual number of neighbors used
    """
    from app.algorithms import CollaborativeFilteringEngine

    # Get customer
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )

    # Initialize CF engine
    cf_engine = CollaborativeFilteringEngine(db)

    # Build user-item matrix
    cf_engine.build_user_item_matrix()

    # Predict rating
    predicted = cf_engine.predict_rating(
        user_id=str(customer.id),
        menu_id=prediction_request.menu_id,
        k=prediction_request.k_neighbors,
        method='pearson'
    )

    return RatingPredictionResponse(
        menu_id=prediction_request.menu_id,
        predicted_rating=round(predicted, 2),
        confidence=None,  # Can be calculated in future
        k_neighbors_used=prediction_request.k_neighbors
    )


@router.get("/history", response_model=List[dict])
async def get_recommendation_history(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get your recommendation history

    Shows past recommendations generated for you (for research transparency)
    """
    from app.models.research import RecommendationLog

    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )

    # Get recommendation logs
    logs = db.query(RecommendationLog).filter(
        RecommendationLog.customer_id == customer.id
    ).order_by(RecommendationLog.timestamp.desc()).limit(limit).all()

    # Convert to list of dicts
    history = []
    for log in logs:
        history.append({
            "id": str(log.id),
            "menu_id": str(log.menu_id),
            "fuzzy_score": float(log.fuzzy_score),
            "cf_score": float(log.cf_score) if log.cf_score else None,
            "hybrid_score": float(log.hybrid_final_score),
            "alpha_used": float(log.alpha_weight),
            "rank": log.rank_position,
            "algorithm_version": log.algorithm_version,
            "timestamp": log.timestamp
        })

    return history


@router.get("/preferences", response_model=CustomerPreferenceResponse)
async def get_recommendation_preferences(
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get your current preference settings used for recommendations

    Shows all fuzzy logic parameters that affect your recommendations
    """
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )

    preference = db.query(CustomerPreference).filter(
        CustomerPreference.customer_id == customer.id
    ).first()

    if not preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found. Please set your preferences first."
        )

    return preference
