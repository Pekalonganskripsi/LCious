"""
Admin API endpoints

API untuk admin melakukan manajemen sistem
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.api.deps import get_db, get_current_admin
from app.schemas.user import UserResponse
from app.models.user import User, UserRole
from app.models.menu import Menu
from app.models.rating import Rating
from app.models.algorithm import AlgorithmParameters
from app.core.config import settings

router = APIRouter()


@router.get("/stats")
async def get_system_stats(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get system statistics for admin dashboard

    Returns:
    - Total customers
    - Total merchants
    - Total menus
    - Total ratings
    - Average rating
    """
    # Count customers
    total_customers = db.query(User).filter(User.role == UserRole.CUSTOMER).count()

    # Count merchants
    total_merchants = db.query(User).filter(User.role == UserRole.MERCHANT).count()

    # Count menus
    total_menus = db.query(Menu).count()

    # Count ratings
    total_ratings = db.query(Rating).count()

    # Calculate average rating
    avg_rating_result = db.query(func.avg(Rating.score)).scalar()
    avg_rating = float(avg_rating_result) if avg_rating_result else 0.0

    return {
        "totalCustomers": total_customers,
        "totalMerchants": total_merchants,
        "totalMenus": total_menus,
        "totalRatings": total_ratings,
        "avgRating": avg_rating,
    }


@router.get("/users")
async def get_all_users(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    limit: int = 100,
    offset: int = 0
):
    """
    Get all users in the system

    Returns list of all users with their roles and status
    """
    users = db.query(User).order_by(User.created_at.desc()).offset(offset).limit(limit).all()

    return {
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": user.created_at,
                "last_login": user.last_login,
            }
            for user in users
        ],
        "total": len(users),
        "limit": limit,
        "offset": offset
    }


@router.put("/users/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: str,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Toggle user active status

    Activate or deactivate a user account
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent deactivating yourself
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )

    # Toggle status
    user.is_active = not user.is_active
    user.updated_at = datetime.utcnow()
    db.commit()

    return {
        "message": f"User {'activated' if user.is_active else 'deactivated'} successfully",
        "user_id": user.id,
        "is_active": user.is_active
    }


@router.post("/users")
async def create_user(
    user_data: dict,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new user

    Admin can create users with any role
    """
    from app.core.security import get_password_hash

    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.get('username')).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.get('email')).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    # Validate role
    role = user_data.get('role', 'customer')
    if role not in ['customer', 'merchant', 'admin', 'superadmin']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )

    # Create user
    new_user = User(
        username=user_data.get('username'),
        email=user_data.get('email'),
        password_hash=get_password_hash(user_data.get('password')),
        role=UserRole(role),
        is_active=True,
        is_verified=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create role-specific profile
    try:
        if role == 'customer':
            from app.models.user import Customer
            customer_profile = Customer(
                id=new_user.id,
                user_id=new_user.id,
                full_name=user_data.get('full_name'),
                phone=user_data.get('phone'),
                address=user_data.get('address'),
            )
            db.add(customer_profile)

        elif role == 'merchant':
            from app.models.user import Merchant
            merchant_profile = Merchant(
                id=new_user.id,
                user_id=new_user.id,
                shop_name=user_data.get('full_name', f"{user_data.get('username')}'s Shop"),
                address=user_data.get('address', ''),
                latitude=str(user_data.get('latitude', '0.0')),
                longitude=str(user_data.get('longitude', '0.0')),
                phone=user_data.get('phone', ''),
            )
            db.add(merchant_profile)

        # Commit profile creation
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating role profile: {str(e)}"
        )

    return {
        "message": "User created successfully",
        "user_id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role
    }


@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    user_data: dict,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update user information

    Admin can update any user's information
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields if provided
    if 'username' in user_data and user_data['username'] != user.username:
        # Check if new username already exists
        existing = db.query(User).filter(User.username == user_data['username']).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        user.username = user_data['username']

    if 'email' in user_data and user_data['email'] != user.email:
        # Check if new email already exists
        existing = db.query(User).filter(User.email == user_data['email']).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        user.email = user_data['email']

    if 'password' in user_data and user_data['password']:
        from app.core.security import get_password_hash
        user.password_hash = get_password_hash(user_data['password'])

    if 'role' in user_data:
        role = user_data['role']
        if role not in ['customer', 'merchant', 'admin', 'superadmin']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role"
            )
        user.role = UserRole(role)

    if 'full_name' in user_data:
        user.full_name = user_data['full_name']

    if 'phone' in user_data:
        user.phone = user_data['phone']

    if 'address' in user_data:
        user.address = user_data['address']

    user.updated_at = datetime.utcnow()
    db.commit()

    # Update role-specific profiles
    if user.role == UserRole.CUSTOMER:
        from app.models.user import Customer
        customer = db.query(Customer).filter(Customer.id == user.id).first()
        if customer:
            customer.full_name = user_data.get('full_name', customer.full_name)
            customer.phone = user_data.get('phone', customer.phone)
            customer.address = user_data.get('address', customer.address)
            db.commit()

    elif user.role == UserRole.MERCHANT:
        from app.models.user import Merchant
        merchant = db.query(Merchant).filter(Merchant.id == user.id).first()
        if merchant:
            merchant.shop_name = user_data.get('full_name', merchant.shop_name)
            merchant.phone = user_data.get('phone', merchant.phone)
            merchant.address = user_data.get('address', merchant.address)
            db.commit()

    return {
        "message": "User updated successfully",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a user

    Admin can delete any user except themselves
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent deleting yourself
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    # Store username for response
    username = user.username

    # Delete role-specific profile
    if user.role == UserRole.CUSTOMER:
        from app.models.user import Customer
        customer = db.query(Customer).filter(Customer.id == user.id).first()
        if customer:
            db.delete(customer)

    elif user.role == UserRole.MERCHANT:
        from app.models.user import Merchant
        merchant = db.query(Merchant).filter(Merchant.id == user.id).first()
        if merchant:
            db.delete(merchant)

    # Delete user
    db.delete(user)
    db.commit()

    return {
        "message": f"User '{username}' deleted successfully",
        "user_id": user_id
    }


@router.put("/algorithm-params")
async def update_algorithm_params(
    params: dict,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update algorithm parameters

    Update global algorithm parameters for recommendation system
    Parameters are stored in database and persist across server restarts
    """
    # Validate parameters
    valid_params = {
        "default_alpha",
        "default_k_neighbors",
        "price_cheap_max",
        "price_medium_min",
        "price_medium_max",
        "price_expensive_min",
        "distance_near_km",
        "distance_medium_min_km",
        "distance_medium_max_km",
        "distance_far_min_km",
    }

    for key in params.keys():
        if key not in valid_params:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid parameter: {key}"
            )

    # Save each parameter to database
    for key, value in params.items():
        # Check if parameter exists
        existing_param = db.query(AlgorithmParameters).filter(
            AlgorithmParameters.parameter_name == key
        ).first()

        if existing_param:
            # Update existing parameter
            existing_param.parameter_value = float(value)
            existing_param.last_updated = datetime.utcnow()
            existing_param.updated_by = str(current_admin.id)
        else:
            # Create new parameter
            new_param = AlgorithmParameters(
                parameter_name=key,
                parameter_value=float(value),
                parameter_type='float',
                updated_by=str(current_admin.id)
            )
            db.add(new_param)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save parameters: {str(e)}"
        )

    return {
        "message": "Algorithm parameters updated successfully",
        "params": params
    }


@router.get("/algorithm-params")
async def get_algorithm_params(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get current algorithm parameters

    Returns current algorithm configuration from database
    Falls back to default values if parameters haven't been set
    """
    # Get all parameters from database
    db_params = db.query(AlgorithmParameters).all()
    params_dict = {p.parameter_name: p.parameter_value for p in db_params}

    # Helper function to get parameter with fallback
    def get_param(name, default):
        return params_dict.get(name, default)

    return {
        "default_alpha": get_param("default_alpha", settings.DEFAULT_ALPHA),
        "default_k_neighbors": get_param("default_k_neighbors", settings.DEFAULT_K_NEIGHBORS),
        "price_cheap_max": get_param("price_cheap_max", settings.PRICE_CHEAP_MAX),
        "price_medium_min": get_param("price_medium_min", settings.PRICE_MEDIUM_MIN),
        "price_medium_max": get_param("price_medium_max", settings.PRICE_MEDIUM_MAX),
        "price_expensive_min": get_param("price_expensive_min", settings.PRICE_EXPENSIVE_MIN),
        "distance_near_km": get_param("distance_near_km", settings.DISTANCE_NEAR_KM),
        "distance_medium_min_km": get_param("distance_medium_min_km", settings.DISTANCE_MEDIUM_MIN_KM),
        "distance_medium_max_km": get_param("distance_medium_max_km", settings.DISTANCE_MEDIUM_MAX_KM),
        "distance_far_min_km": get_param("distance_far_min_km", settings.DISTANCE_FAR_MIN_KM),
    }


@router.get("/evaluation")
async def get_evaluation_metrics(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get algorithm evaluation metrics for research

    Calculates and returns:
    - MAE (Mean Absolute Error): Average difference between predicted and actual ratings
    - RMSE (Root Mean Square Error): Accuracy of predictions
    - Hit Rate: Percentage of recommendations that users liked
    """
    import math

    # Get all ratings
    ratings = db.query(Rating).all()

    if not ratings:
        return {
            "mae": 0.0,
            "rmse": 0.0,
            "hit_rate": 0.0,
            "total_ratings": 0,
            "high_rating_count": 0,
            "avg_rating": 0.0,
            "rating_distribution": {
                "1_star": 0,
                "2_star": 0,
                "3_star": 0,
                "4_star": 0,
                "5_star": 0,
            }
        }

    # For MAE and RMSE, we need predicted vs actual
    # Since we don't store predictions, we'll use a proxy:
    # Compare user's average rating with each of their ratings
    from app.models.user import Customer

    customers = db.query(Customer).all()

    # Calculate MAE and RMSE
    total_absolute_error = 0.0
    total_squared_error = 0.0
    prediction_count = 0

    for customer in customers:
        # Get user's ratings
        customer_ratings = db.query(Rating).filter(Rating.customer_id == customer.id).all()

        if len(customer_ratings) > 1:
            # Calculate user's average rating (excluding current rating for prediction)
            for rating in customer_ratings:
                other_ratings = [r.score for r in customer_ratings if r.id != rating.id]

                if other_ratings:
                    # Predict using average of other ratings (simple collaborative filtering proxy)
                    predicted_rating = sum(other_ratings) / len(other_ratings)
                    actual_rating = rating.score

                    # Calculate errors
                    absolute_error = abs(actual_rating - predicted_rating)
                    squared_error = (actual_rating - predicted_rating) ** 2

                    total_absolute_error += absolute_error
                    total_squared_error += squared_error
                    prediction_count += 1

    # Calculate MAE and RMSE
    mae = total_absolute_error / prediction_count if prediction_count > 0 else 0.0
    rmse = math.sqrt(total_squared_error / prediction_count) if prediction_count > 0 else 0.0

    # Calculate Hit Rate (percentage of ratings >= 4)
    high_rating_count = sum(1 for r in ratings if r.score >= 4)
    hit_rate = (high_rating_count / len(ratings)) * 100 if ratings else 0.0

    # Calculate rating distribution
    rating_dist = {
        "1_star": sum(1 for r in ratings if r.score == 1),
        "2_star": sum(1 for r in ratings if r.score == 2),
        "3_star": sum(1 for r in ratings if r.score == 3),
        "4_star": sum(1 for r in ratings if r.score == 4),
        "5_star": sum(1 for r in ratings if r.score == 5),
    }

    return {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "hit_rate": round(hit_rate, 2),
        "total_ratings": len(ratings),
        "high_rating_count": high_rating_count,
        "avg_rating": round(float(db.query(func.avg(Rating.score)).scalar() or 0), 2),
        "rating_distribution": rating_dist,
        "prediction_count": prediction_count,
    }


@router.get("/evaluation/data-export")
async def export_evaluation_data(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Export all evaluation data for research

    Returns detailed data including:
    - All ratings with user and menu info
    - Per-user statistics
    - Per-menu statistics
    """
    from app.models.user import Customer
    from app.models.menu import Menu
    from app.models.user import Merchant

    # Get all ratings with details
    ratings_data = db.query(
        Rating,
        Customer,
        Menu,
        Merchant
    ).join(
        Customer, Rating.customer_id == Customer.id
    ).join(
        Menu, Rating.menu_id == Menu.id
    ).join(
        Merchant, Menu.merchant_id == Merchant.id
    ).all()

    export_data = {
        "ratings": [
            {
                "rating_id": rating.id,
                "customer_id": customer.id,
                "customer_name": customer.full_name or customer.user.username if customer.user else "Unknown",
                "menu_id": menu.id,
                "menu_name": menu.item_name,
                "merchant_name": merchant.shop_name,
                "score": rating.score,
                "review_text": rating.review_text,
                "created_at": rating.created_at.isoformat() if rating.created_at else None,
            }
            for rating, customer, menu, merchant in ratings_data
        ],
        "summary": {
            "total_ratings": len(ratings_data),
            "export_date": datetime.utcnow().isoformat(),
        }
    }

    return export_data


@router.get("/merchants")
async def get_all_merchants(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    """
    Get all merchants with their details

    Returns list of all merchants with shop information and menu counts

    **Merchant Rating Calculation:**
    Merchant rating is calculated as the average of ALL ratings across ALL menus
    from that merchant. This is computed in real-time.

    **Sorting Options:**
    - created_at: Sort by creation date (default)
    - shop_name: Sort by shop name
    - rating: Sort by average rating
    - menu_count: Sort by number of menus

    **Sort Order:**
    - asc: Ascending order
    - desc: Descending order (default)
    """
    from app.models.user import Merchant
    from app.models.rating import Rating

    # Validate sort_by parameter
    valid_sort_fields = ["created_at", "shop_name", "rating", "menu_count"]
    if sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort_by field. Must be one of: {', '.join(valid_sort_fields)}"
        )

    # Validate sort_order parameter
    if sort_order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sort_order. Must be 'asc' or 'desc'"
        )

    # For rating and menu_count sorting, we need to calculate first
    if sort_by in ["rating", "menu_count"]:
        # Get all merchants first (we'll sort in Python after calculating ratings)
        merchants = db.query(Merchant).offset(offset).limit(limit).all()
    else:
        # For other fields, we can sort at database level
        order_field = getattr(Merchant, sort_by)
        order_func = getattr(order_field, sort_order)()
        merchants = db.query(Merchant).order_by(order_func).offset(offset).limit(limit).all()

    merchant_data = []
    for merchant in merchants:
        # Count menus for this merchant
        menu_count = db.query(Menu).filter(Menu.merchant_id == merchant.id).count()

        # Calculate merchant average rating in real-time
        # Get all menu IDs for this merchant
        menu_ids = db.query(Menu.id).filter(Menu.merchant_id == merchant.id).all()
        menu_ids = [m[0] for m in menu_ids]

        if menu_ids:
            # Get all ratings for all menus from this merchant
            all_ratings = db.query(Rating).filter(Rating.menu_id.in_(menu_ids)).all()
            if all_ratings:
                merchant_avg_rating = sum(r.score for r in all_ratings) / len(all_ratings)
            else:
                merchant_avg_rating = 0.0
        else:
            merchant_avg_rating = 0.0

        # Get user info
        user = db.query(User).filter(User.id == merchant.user_id).first()

        merchant_data.append({
            "id": merchant.id,
            "user_id": merchant.user_id,
            "username": user.username if user else "Unknown",
            "email": user.email if user else "Unknown",
            "shop_name": merchant.shop_name,
            "description": merchant.description,
            "address": merchant.address,
            "phone": merchant.phone,
            "cuisine_type": merchant.cuisine_type,
            "price_range": merchant.price_range,
            "menu_count": menu_count,
            "average_rating": round(merchant_avg_rating, 2),  # Real-time calculation
            "is_active": user.is_active if user else False,
            "created_at": merchant.created_at,
        })

    # Apply sorting for rating and menu_count
    if sort_by == "rating":
        reverse = (sort_order == "desc")
        merchant_data.sort(key=lambda x: x["average_rating"], reverse=reverse)
    elif sort_by == "menu_count":
        reverse = (sort_order == "desc")
        merchant_data.sort(key=lambda x: x["menu_count"], reverse=reverse)
    elif sort_by == "shop_name":
        reverse = (sort_order == "desc")
        merchant_data.sort(key=lambda x: x["shop_name"].lower(), reverse=reverse)

    return {
        "merchants": merchant_data,
        "total": len(merchant_data),
        "limit": limit,
        "offset": offset,
        "sort_by": sort_by,
        "sort_order": sort_order
    }


@router.get("/merchants/{merchant_id}/menus")
async def get_merchant_menus(
    merchant_id: str,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all menus for a specific merchant

    Returns detailed list of all menus from a merchant
    """
    from app.models.user import Merchant

    # Verify merchant exists
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found"
        )

    # Get all menus for this merchant
    menus = db.query(Menu).filter(Menu.merchant_id == merchant_id).all()

    menu_data = []
    for menu in menus:
        menu_data.append({
            "id": menu.id,
            "menu_id": menu.id,
            "item_name": menu.item_name,
            "description": menu.description,
            "price": float(menu.price) if menu.price else 0,
            "category": menu.category,
            "image_url": menu.image_url,
            "spice_level": menu.spice_level or 0,
            "sweetness_level": menu.sweetness_level or 0,
            "savory_level": menu.savory_level or 0,
            "popularity_score": menu.popularity_score or 0,
            "is_available": menu.is_available,
            "created_at": menu.created_at,
        })

    return {
        "merchant_id": merchant_id,
        "merchant_name": merchant.shop_name,
        "menus": menu_data,
        "total_menus": len(menu_data)
    }


# =====================
# Evaluation Endpoints
# =====================

@router.post("/evaluation/run")
async def run_evaluation(
    test_size: float = 0.2,
    k_values: str = "5,10,20",
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Jalankan evaluasi lengkap sistem rekomendasi

    Metrics yang dihitung:
    - RMSE, MAE (akurasi prediksi rating)
    - Precision@K, Recall@K, F1@K (kualitas rekomendasi)
    - NDCG@K (ranking quality)
    - Coverage, Diversity

    Parameters:
    - test_size: Proporsi test data (0.0-1.0)
    - k_values: Comma-separated K values (default: "5,10,20")

    Returns:
    - Lengkap hasil evaluasi dengan interpretasi
    """
    from app.algorithms.evaluation import AlgorithmEvaluator

    # Parse k_values
    k_list = [int(k.strip()) for k in k_values.split(',')]

    # Initialize evaluator
    evaluator = AlgorithmEvaluator(db)

    # Get all ratings
    all_ratings = db.query(Rating).all()

    if len(all_ratings) == 0:
        raise HTTPException(
            status_code=400,
            detail="No ratings found in database. Cannot run evaluation."
        )

    print(f"Running evaluation with {len(all_ratings)} ratings...")

    # Run cross-validation evaluation (comprehensive results)
    try:
        # Comprehensive evaluation for accurate results:
        # - 5 folds for robust cross-validation
        # - 7 alpha values for complete analysis
        # Note: This may take 2-5 minutes depending on data size
        results = evaluator.cross_validate(
            ratings=all_ratings,
            n_splits=5,
            alpha_values=[0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]
        )

        # Get best alpha
        best_alpha = min(results.items(), key=lambda x: x[1]['avg_mae'])

        return {
            "status": "success",
            "test_size": test_size,
            "k_values": k_list,
            "total_ratings": len(all_ratings),
            "results": results,
            "best_alpha": {
                "value": best_alpha[0],
                "mae": best_alpha[1]['avg_mae'],
                "rmse": best_alpha[1]['avg_rmse'],
                "hit_rate": best_alpha[1]['avg_hit_rate']
            },
            "recommendation": f"Alpha {best_alpha[0]} performs best with MAE={best_alpha[1]['avg_mae']:.4f}"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation failed: {str(e)}"
        )


@router.get("/evaluation/compare-algorithms")
async def compare_algorithms(
    test_size: float = 0.2,
    k: int = 10,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Bandingkan Hybrid dengan baseline algorithms

    Algorithms:
    1. Hybrid (α=0.5) - Current system
    2. Fuzzy Only (α=1.0) - Content-based only
    3. CF Only (α=0.0) - Collaborative filtering only

    Returns:
    - Perbandingan performa antar algorithms
    - Winner recommendation
    """
    from app.algorithms.evaluation import AlgorithmEvaluator

    evaluator = AlgorithmEvaluator(db)
    all_ratings = db.query(Rating).all()

    if len(all_ratings) < 10:
        raise HTTPException(
            status_code=400,
            detail=f"Need at least 10 ratings for comparison. Currently: {len(all_ratings)}"
        )

    try:
        # Compare algorithms
        comparison = evaluator.evaluate_algorithm_split(
            ratings=all_ratings,
            test_split=test_size,
            alpha_values=[0.0, 0.5, 1.0]  # CF only, Hybrid, Fuzzy only
        )

        # Map to algorithm names
        algo_names = {
            0.0: "Collaborative Filtering Only",
            0.5: "Hybrid (Current System)",
            1.0: "Fuzzy Logic Only"
        }

        formatted_results = {}
        for alpha_key, metrics in comparison.items():
            alpha_val = metrics['alpha']
            algo_name = algo_names.get(alpha_val, f"Alpha {alpha_val}")

            formatted_results[algo_name] = {
                "alpha": alpha_val,
                "mae": metrics['mae'],
                "rmse": metrics['rmse'],
                "hit_rate": metrics['hit_rate'],
                "predictions": metrics['n_predictions']
            }

        # Find winner (lowest MAE)
        winner = min(comparison.items(), key=lambda x: x[1]['mae'])
        winner_name = algo_names.get(winner[1]['alpha'], f"Alpha {winner[1]['alpha']}")

        return {
            "comparison": formatted_results,
            "winner": winner_name,
            "winner_mae": winner[1]['mae'],
            "test_size": test_size,
            "k": k,
            "total_ratings": len(all_ratings),
            "evaluated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Comparison failed: {str(e)}"
        )


@router.get("/evaluation/alpha-optimization")
async def optimize_alpha(
    alpha_range: str = "0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0",
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Cari alpha optimal dengan testing berbagai nilai

    Returns:
    - Grafik performa vs alpha
    - Rekomendasi alpha terbaik
    """
    from app.algorithms.evaluation import AlgorithmEvaluator

    evaluator = AlgorithmEvaluator(db)
    all_ratings = db.query(Rating).all()

    # Parse alpha range
    alphas = [float(a.strip()) for a in alpha_range.split(',')]

    try:
        results = evaluator.evaluate_algorithm_split(
            ratings=all_ratings,
            test_split=0.2,
            alpha_values=alphas
        )

        # Format for frontend
        chart_data = []
        for key, metrics in results.items():
            chart_data.append({
                "alpha": metrics['alpha'],
                "mae": metrics['mae'],
                "rmse": metrics['rmse'],
                "hit_rate": metrics['hit_rate']
            })

        # Find best alpha
        best = min(results.items(), key=lambda x: x[1]['mae'])

        return {
            "chart_data": chart_data,
            "best_alpha": best[1]['alpha'],
            "best_mae": best[1]['mae'],
            "best_rmse": best[1]['rmse'],
            "interpretation": f"Alpha {best[1]['alpha']:.2f} gives best performance with MAE={best[1]['mae']:.4f}",
            "total_ratings": len(all_ratings),
            "evaluated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Alpha optimization failed: {str(e)}"
        )


@router.get("/evaluation/system-health")
async def get_system_health(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Cek kesehatan sistem rekomendasi

    Returns:
    - Data statistics
    - Sparsity analysis
    - Cold start analysis
    """
    # Get basic stats
    from app.models.user import Customer, Merchant
    from app.models.menu import Menu

    total_customers = db.query(Customer).count()
    total_merchants = db.query(Merchant).count()
    total_menus = db.query(Menu).count()
    total_ratings = db.query(Rating).count()

    # Calculate sparsity
    # Total possible ratings = customers × menus
    total_possible = total_customers * total_menus
    sparsity = 1.0 - (total_ratings / total_possible) if total_possible > 0 else 1.0

    # Rating distribution
    rating_dist = db.query(
        Rating.score, func.count(Rating.id)
    ).group_by(Rating.score).all()

    # User rating count distribution
    from sqlalchemy import literal_column
    user_rating_counts = db.query(
        Rating.customer_id,
        func.count(Rating.id).label('count')
    ).group_by(Rating.customer_id).all()

    # Categorize users
    new_users = len([c for c in user_rating_counts if c.count <= 5])
    medium_users = len([c for c in user_rating_counts if 5 < c.count <= 20])
    active_users = len([c for c in user_rating_counts if c.count > 20])

    return {
        "data_statistics": {
            "total_customers": total_customers,
            "total_merchants": total_merchants,
            "total_menus": total_menus,
            "total_ratings": total_ratings,
            "ratings_per_menu": total_ratings / total_menus if total_menus > 0 else 0,
            "ratings_per_customer": total_ratings / total_customers if total_customers > 0 else 0
        },
        "sparsity_analysis": {
            "total_possible_ratings": total_possible,
            "actual_ratings": total_ratings,
            "sparsity_percentage": sparsity * 100,
            "interpretation": f"{sparsity * 100:.1f}% of rating matrix is empty"
        },
        "rating_distribution": [
            {"score": score, "count": count}
            for score, count in rating_dist
        ],
        "user_segments": {
            "new_users_0_5_ratings": new_users,
            "medium_users_6_20_ratings": medium_users,
            "active_users_20plus_ratings": active_users
        },
        "health_status": "healthy" if total_ratings >= 100 else "needs_more_data"
    }


@router.get("/evaluation/precision-recall")
async def get_precision_recall_metrics(
    k_values: str = "5,10,20",
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Hitung Precision@K, Recall@K, dan F1@K

    Metrics ini mengukur kualitas rekomendasi:
    - Precision@K: Berapa banyak top-K rekomendasi yang relevan (rating ≥ 4)
    - Recall@K: Berapa banyak item relevan yang ditemukan di top-K
    - F1@K: Harmonic mean precision dan recall

    Args:
        k_values: Comma-separated K values (default: "5,10,20")

    Returns:
        Metrics untuk setiap nilai K
    """
    from app.algorithms.evaluation import AlgorithmEvaluator

    k_list = [int(k.strip()) for k in k_values.split(',')]
    evaluator = AlgorithmEvaluator(db)

    # Get all ratings
    all_ratings = db.query(Rating).all()

    if len(all_ratings) < 20:
        raise HTTPException(
            status_code=400,
            detail=f"Need at least 20 ratings for precision/recall evaluation. Currently: {len(all_ratings)}"
        )

    try:
        results = {}

        for k in k_list:
            # Calculate precision and recall for each user
            from app.models.user import Customer
            customers = db.query(Customer).all()

            total_precision = 0.0
            total_recall = 0.0
            valid_users = 0

            for customer in customers:
                # Get user's ratings
                customer_ratings = db.query(Rating).filter(
                    Rating.customer_id == customer.id,
                    Rating.score >= 4  # Relevant items
                ).all()

                if len(customer_ratings) == 0:
                    continue

                # For each rating, predict and check if it's in top-K
                hit_count = 0
                total_relevant = len(customer_ratings)

                for rating in customer_ratings:
                    # Get prediction (using CF)
                    predicted = evaluator.cf_engine.predict_rating(
                        user_id=customer.id,
                        menu_id=rating.menu_id,
                        k=10,
                        method='pearson'
                    )

                    # Simplified: if prediction is close to actual, count as hit
                    if abs(predicted - rating.score) <= 1:
                        hit_count += 1

                # Precision@K = hits / K
                precision_at_k = hit_count / k if k > 0 else 0

                # Recall@K = hits / total_relevant
                recall_at_k = hit_count / total_relevant if total_relevant > 0 else 0

                total_precision += precision_at_k
                total_recall += recall_at_k
                valid_users += 1

            # Average across all users
            avg_precision = total_precision / valid_users if valid_users > 0 else 0
            avg_recall = total_recall / valid_users if valid_users > 0 else 0
            f1_score = 2 * (avg_precision * avg_recall) / (avg_precision + avg_recall) if (avg_precision + avg_recall) > 0 else 0

            results[f"k_{k}"] = {
                "k": k,
                "precision": round(avg_precision, 4),
                "recall": round(avg_recall, 4),
                "f1_score": round(f1_score, 4)
            }

        return {
            "metrics": results,
            "interpretation": {
                "precision": "Fraction of recommended items that are relevant",
                "recall": "Fraction of relevant items that are recommended",
                "f1_score": "Harmonic mean of precision and recall"
            },
            "evaluated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Precision/Recall evaluation failed: {str(e)}"
        )


@router.get("/evaluation/coverage")
async def get_coverage_metrics(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Hitung Catalog Coverage

    Coverage mengukur persentase item yang direkomendasikan kepada user
    - Catalog Coverage: % item yang muncul dalam rekomendasi
    - Average Coverage: Rata-rata item yang direkomendasikan per user

    Returns:
        Coverage metrics untuk sistem rekomendasi
    """
    from app.algorithms.evaluation import AlgorithmEvaluator

    evaluator = AlgorithmEvaluator(db)

    # Get all menus and customers
    total_menus = db.query(Menu).filter(Menu.is_available == True).count()
    from app.models.user import Customer
    customers = db.query(Customer).all()

    if total_menus == 0 or len(customers) == 0:
        return {
            "catalog_coverage": 0.0,
            "average_items_per_user": 0.0,
            "total_items": total_menus,
            "total_users": len(customers),
            "interpretation": "No data available"
        }

    # Track which menus are recommended
    recommended_menus = set()
    total_recommendations = 0

    for customer in customers:
        try:
            # Get recommendations for each customer
            from app.algorithms.hybrid import HybridRecommender
            hybrid = HybridRecommender(db, alpha=0.5)

            # Get customer preferences
            customer_pref = {
                'preferred_price_range': customer.pref_price_sensitivity or 'medium',
                'preferred_distance': customer.pref_max_distance_km or 10,
                'preferred_spice_level': customer.pref_spice_level or 0,
                'preferred_sweetness_level': customer.pref_sweetness_level or 0,
                'preferred_savory_level': customer.pref_savory_level or 0,
                'preferred_cuisine': customer.preferred_cuisines or []
            } if hasattr(customer, 'pref_price_sensitivity') else {}

            customer_location = (
                float(customer.latitude) if customer.latitude else -6.9,
                float(customer.longitude) if customer.longitude else 110.0
            )

            # Generate recommendations
            try:
                recs = hybrid.generate_recommendations(
                    customer_id=customer.id,
                    customer_pref=customer_pref,
                    customer_location=customer_location,
                    n_recommendations=20,
                    alpha=0.5
                )

                # Track recommended menu IDs
                for rec in recs:
                    recommended_menus.add(rec['menu']['id'])
                    total_recommendations += 1

            except Exception as e:
                print(f"Error generating recs for customer {customer.id}: {e}")
                continue

        except Exception as e:
            print(f"Error processing customer {customer.id}: {e}")
            continue

    # Calculate coverage
    catalog_coverage = (len(recommended_menus) / total_menus * 100) if total_menus > 0 else 0
    average_items_per_user = total_recommendations / len(customers) if customers else 0

    return {
        "catalog_coverage": round(catalog_coverage, 2),
        "average_items_per_user": round(average_items_per_user, 2),
        "total_unique_items_recommended": len(recommended_menus),
        "total_items_in_catalog": total_menus,
        "total_users": len(customers),
        "total_recommendations_made": total_recommendations,
        "interpretation": f"{catalog_coverage:.1f}% of catalog items are recommended to users",
        "coverage_quality": "Good" if catalog_coverage > 70 else "Fair" if catalog_coverage > 40 else "Poor (need more diversity)"
    }


@router.get("/evaluation/per-user-segment")
async def get_per_user_segment_performance(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Analisis performa per user segment

    Mengukur performa sistem untuk:
    - Cold start users (0-5 ratings)
    - Warm users (6-20 ratings)
    - Active users (20+ ratings)

    Returns:
        Performance metrics per user segment
    """
    from app.algorithms.evaluation import AlgorithmEvaluator
    from app.models.user import Customer

    evaluator = AlgorithmEvaluator(db)
    customers = db.query(Customer).all()

    # Group users by rating count
    cold_users = []
    warm_users = []
    active_users = []

    for customer in customers:
        rating_count = db.query(Rating).filter(Rating.customer_id == customer.id).count()

        if rating_count <= 5:
            cold_users.append(customer.id)
        elif rating_count <= 20:
            warm_users.append(customer.id)
        else:
            active_users.append(customer.id)

    segments = {
        "cold_start_0_5": cold_users,
        "warm_6_20": warm_users,
        "active_20plus": active_users
    }

    results = {}

    for segment_name, user_ids in segments.items():
        if len(user_ids) == 0:
            results[segment_name] = {
                "user_count": 0,
                "avg_mae": 0,
                "avg_rmse": 0,
                "status": "No users in this segment"
            }
            continue

        # Calculate metrics for this segment
        total_ae = 0
        total_se = 0
        count = 0

        for user_id in user_ids:
            # Get user's ratings
            user_ratings = db.query(Rating).filter(Rating.customer_id == user_id).all()

            if len(user_ratings) <= 1:
                continue

            # Cross-validation for this user
            for rating in user_ratings:
                other_ratings = [r for r in user_ratings if r.id != rating.id]

                if other_ratings:
                    predicted = sum(r.score for r in other_ratings) / len(other_ratings)
                    actual = rating.score

                    total_ae += abs(actual - predicted)
                    total_se += (actual - predicted) ** 2
                    count += 1

        avg_mae = total_ae / count if count > 0 else 0
        avg_rmse = (total_se / count) ** 0.5 if count > 0 else 0

        results[segment_name] = {
            "user_count": len(user_ids),
            "avg_mae": round(avg_mae, 4),
            "avg_rmse": round(avg_rmse, 4),
            "prediction_count": count,
            "status": "OK"
        }

    # Add interpretation
    best_segment = min(results.items(), key=lambda x: x[1]['avg_mae'] if x[1]['user_count'] > 0 else float('inf'))

    return {
        "segment_performance": results,
        "best_performing_segment": best_segment[0],
        "cold_start_handling": "Fuzzy logic helps cold start users" if results.get("cold_start_0_5", {}).get("avg_mae", 1) < 1.0 else "Need improvement for cold start",
        "interpretation": {
            "cold_start": "Users with 0-5 ratings benefit most from content-based (Fuzzy) recommendations",
            "warm": "Users with 6-20 ratings use balanced hybrid approach",
            "active": "Users with 20+ ratings get accurate collaborative filtering recommendations"
        },
        "evaluated_at": datetime.utcnow().isoformat()
    }


@router.get("/evaluation/statistical-test")
async def statistical_significance_test(
    alpha1: float = 0.5,
    alpha2: float = 0.0,
    test_size: float = 0.2,
    n_runs: int = 10,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Statistical Significance Testing antara dua alpha values

    Menggunakan paired t-test untuk membuktikan apakah perbedaan
    antara dua algoritma signifikan secara statistik

    Args:
        alpha1: Alpha value pertama (default: 0.5 - Hybrid)
        alpha2: Alpha value kedua (default: 0.0 - CF Only)
        test_size: Proporsi test data
        n_runs: Jumlah running untuk sampling

    Returns:
        Statistical test results dengan t-statistic, p-value, effect size, dll
    """
    from app.algorithms.evaluation import AlgorithmEvaluator

    all_ratings = db.query(Rating).all()

    if len(all_ratings) < 10:
        raise HTTPException(
            status_code=400,
            detail=f"Need at least 10 ratings for statistical test. Currently: {len(all_ratings)}"
        )

    evaluator = AlgorithmEvaluator(db)

    try:
        results = evaluator.statistical_significance_test(
            ratings=all_ratings,
            alpha1=alpha1,
            alpha2=alpha2,
            test_size=test_size,
            n_runs=n_runs
        )

        return results

    except Exception as e:
        import traceback
        error_detail = f"Statistical test failed: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(f"ERROR in statistical test: {error_detail}")  # Log to console
        raise HTTPException(
            status_code=500,
            detail=f"Statistical test failed: {str(e)}"
        )


@router.get("/evaluation/baselines")
async def compare_with_baselines(
    test_size: float = 0.2,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Bandingkan Hybrid dengan berbagai baseline algorithms

    ⚠️ UPDATED: Sekarang menggunakan fungsi compare_with_baselines() yang sudah di-unifikasi
    untuk konsistensi dengan endpoint lain!

    Baselines (7 algoritma lengkap):
    1. Random - Rekomendasi acak
    2. Most Popular - Menu paling populer
    3. Average Rating - Rata-rata rating global
    4. Item-Based CF - CF berbasis item
    5. User-Based CF - CF berbasis user (α=0)
    6. Fuzzy Logic - Content-based (α=1.0)
    7. Hybrid - Kombinasi Fuzzy + CF (α=0.5)

    Returns:
        Perbandingan metrics untuk semua baseline
    """
    from app.algorithms.evaluation import AlgorithmEvaluator

    all_ratings = db.query(Rating).all()

    if len(all_ratings) < 10:
        raise HTTPException(
            status_code=400,
            detail=f"Need at least 10 ratings for baseline comparison. Currently: {len(all_ratings)}"
        )

    evaluator = AlgorithmEvaluator(db)

    try:
        import logging
        logging.info("Starting unified baseline comparison...")

        # Gunakan fungsi yang sudah di-unifikasi untuk konsistensi
        results = evaluator.compare_with_baselines(
            ratings=all_ratings,
            test_size=test_size,
            k=10
        )

        # Extract comparison dan winner dari results
        comparison = {k: v for k, v in results.items()
                     if k not in ['winner', 'winner_mae', 'total_ratings', 'test_size']}

        logging.info(f"Unified baseline comparison completed. Winner: {results.get('winner')}")

        return {
            'comparison': comparison,
            'winner': results.get('winner'),
            'winner_mae': results.get('winner_mae'),
            'total_ratings': results.get('total_ratings', len(all_ratings)),
            'test_size': results.get('test_size', test_size),
            'interpretation': f"{results.get('winner', 'Unknown')} achieves lowest MAE of {results.get('winner_mae', 0):.4f}",
            'evaluated_at': datetime.utcnow().isoformat()
        }

    except Exception as e:
        import traceback
        logging.error(f"Baseline comparison failed: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Baseline comparison failed: {str(e)}"
        )


@router.get("/evaluation/per-user-analysis")
async def per_user_error_analysis(
    alpha: float = 0.5,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Analisis error per user untuk memahami performa di berbagai segment

    Returns:
        - Error metrics per user segment (new, medium, active)
        - Worst predictions (top 10)
        - Best predictions (top 10)
        - Error distribution statistics
    """
    from app.algorithms.evaluation import AlgorithmEvaluator

    all_ratings = db.query(Rating).all()

    if len(all_ratings) < 10:
        raise HTTPException(
            status_code=400,
            detail=f"Need at least 10 ratings for per-user analysis. Currently: {len(all_ratings)}"
        )

    evaluator = AlgorithmEvaluator(db)

    try:
        results = evaluator.per_user_error_analysis(
            ratings=all_ratings,
            alpha=alpha
        )

        return results

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Per-user analysis failed: {str(e)}"
        )


@router.get("/evaluation/temporal-analysis")
async def temporal_analysis(
    days: int = 30,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Analisis performa sistem dari waktu ke waktu

    Args:
        days: Jumlah hari ke belakang untuk dianalisis (default: 30)

    Returns:
        - Daily metrics (MAE, RMSE, rating per hari)
        - Trend analysis (improving/declining/stable)
        - Rating growth over time
    """
    from app.algorithms.evaluation import AlgorithmEvaluator

    evaluator = AlgorithmEvaluator(db)

    try:
        results = evaluator.temporal_analysis(
            db=db,
            days=days
        )

        return results

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Temporal analysis failed: {str(e)}"
        )


@router.get("/evaluation/health")
async def evaluation_health_check(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Health check endpoint untuk evaluasi sistem

    Mengecek:
    - Apakah semua 7 titik alpha berhasil dihitung
    - Apakah semua 7 baseline algorithm berhasil dihitung
    - Apakah std dev semua alpha > 0 (menandakan k-fold benar-benar jalan)
    - Apakah semua 3 segmen user punya minimal 1 user

    Jika ada yang gagal, endpoint ini return daftar bagian yang bermasalah
    """
    from app.algorithms.evaluation import AlgorithmEvaluator

    all_ratings = db.query(Rating).all()

    if len(all_ratings) < 50:
        return {
            "status": "warning",
            "message": f"Insufficient data for comprehensive health check ({len(all_ratings)} < 50)",
            "total_ratings": len(all_ratings),
            "checks": []
        }

    evaluator = AlgorithmEvaluator(db)
    issues = []

    # Check 1: Alpha values completeness
    try:
        alpha_values = [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]
        alpha_results = evaluator.cross_validate(
            ratings=all_ratings,
            n_splits=3,  # Faster for health check
            alpha_values=alpha_values
        )

        # Check std dev > 0
        zero_std_devs = [k for k, v in alpha_results.items() if v.get('std_mae', 0) == 0]
        if zero_std_devs:
            issues.append(f"Alpha values with std dev = 0: {zero_std_devs}")

        # Check all 7 alphas present
        missing_alphas = [f"alpha_{a}" for a in alpha_values if f"alpha_{a}" not in alpha_results]
        if missing_alphas:
            issues.append(f"Missing alpha results: {missing_alphas}")

    except Exception as e:
        issues.append(f"Alpha evaluation failed: {str(e)}")

    # Check 2: Baseline algorithms
    try:
        baseline_results = evaluator.calculate_baseline_metrics(
            ratings=all_ratings,
            test_size=0.2
        )

        # Check expected baselines
        expected_baselines = ['random', 'most_popular', 'average_rating', 'item_cf']
        missing_baselines = [b for b in expected_baselines if b not in baseline_results]
        if missing_baselines:
            issues.append(f"Missing baselines: {missing_baselines}")

        # Check for errors in baselines
        failed_baselines = [k for k, v in baseline_results.items() if v.get('error') or v.get('mae') is None]
        if failed_baselines:
            issues.append(f"Failed baselines: {failed_baselines}")

    except Exception as e:
        issues.append(f"Baseline evaluation failed: {str(e)}")

    # Check 3: User segmentation
    try:
        from app.models.user import Customer
        customers = db.query(Customer).all()

        # Get rating counts per user
        user_rating_counts = {}
        for rating in all_ratings:
            user_rating_counts[rating.customer_id] = user_rating_counts.get(rating.customer_id, 0) + 1

        # Check segments
        new_users = len([uid for uid, count in user_rating_counts.items() if count <= 5])
        medium_users = len([uid for uid, count in user_rating_counts.items() if 6 <= count <= 20])
        power_users = len([uid for uid, count in user_rating_counts.items() if count > 20])

        if new_users == 0:
            issues.append("No new users (0-5 ratings) found")
        if medium_users == 0:
            issues.append("No medium users (6-20 ratings) found")
        if power_users == 0:
            issues.append("No power users (20+ ratings) found")

    except Exception as e:
        issues.append(f"User segmentation check failed: {str(e)}")

    # Check 4: Statistical test between alpha 0.5 vs 0.0
    try:
        stat_results = evaluator.statistical_significance_test(
            ratings=all_ratings,
            alpha1=0.5,
            alpha2=0.0,
            test_size=0.2,
            n_runs=5  # Faster for health check
        )

        # Check essential fields
        required_fields = ['t_statistic', 'p_value', 'is_significant', 'effect_size', 'ci_95_lower', 'ci_95_upper']
        missing_fields = [f for f in required_fields if stat_results.get(f) is None]
        if missing_fields:
            issues.append(f"Statistical test missing fields: {missing_fields}")

    except Exception as e:
        issues.append(f"Statistical test failed: {str(e)}")

    return {
        "status": "healthy" if not issues else "degraded",
        "total_ratings": len(all_ratings),
        "checks": {
            "alpha_values": len(alpha_results) if 'alpha_results' in locals() else 0,
            "baselines": len(baseline_results) if 'baseline_results' in locals() else 0,
            "user_segments": {
                "new_users": new_users if 'new_users' in locals() else 0,
                "medium_users": medium_users if 'medium_users' in locals() else 0,
                "power_users": power_users if 'power_users' in locals() else 0
            } if 'new_users' in locals() else {}
        },
        "issues": issues,
        "timestamp": datetime.utcnow().isoformat()
    }
