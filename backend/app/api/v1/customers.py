"""
Customer API endpoints
Profile, preferences, and ratings management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.api.deps import get_db, get_current_user, get_current_customer
from app.schemas.user import (
    CustomerUpdate,
    CustomerResponse,
    CustomerWithUser,
    CustomerPreferenceCreate,
    CustomerPreferenceUpdate,
    CustomerPreferenceResponse
)
from app.schemas.menu import RatingCreate, RatingUpdate, RatingResponse, RatingWithDetails
from app.models.user import User, Customer
from app.models.fuzzy import CustomerPreference
from app.models.rating import Rating
from app.models.menu import Menu

router = APIRouter()


# =====================
# Customer Profile Endpoints
# =====================

@router.get("/me")
async def get_customer_profile(
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get current customer profile with preferences

    Returns complete customer profile including taste preferences
    """
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )

    # Get preferences
    preference = db.query(CustomerPreference).filter(
        CustomerPreference.customer_id == customer.id
    ).first()

    return {
        "customer": {
            "id": customer.id,
            "full_name": customer.full_name,
            "phone": customer.phone,
            "address": customer.address,
            "latitude": customer.latitude,
            "longitude": customer.longitude,
            "avatar_url": customer.avatar_url,
            "date_of_birth": customer.date_of_birth,
        },
        "preferences": {
            "pref_price_sensitivity": preference.pref_price_sensitivity if preference else "medium",
            "pref_max_distance_km": preference.pref_max_distance_km if preference else 10,
            "pref_spice_level": preference.pref_spice_level if preference else 0,
            "pref_sweetness_level": preference.pref_sweetness_level if preference else 0,
            "pref_savory_level": preference.pref_savory_level if preference else 0,
        } if preference else None
    }


@router.put("/me")
async def update_customer_profile_full(
    profile_data: dict,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Update customer profile and preferences

    Update both personal info and taste preferences in one call
    """
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )

    # Update customer fields
    if 'full_name' in profile_data:
        customer.full_name = profile_data['full_name']
    if 'phone' in profile_data:
        customer.phone = profile_data['phone']
    if 'address' in profile_data:
        customer.address = profile_data['address']
    if 'latitude' in profile_data:
        customer.latitude = str(profile_data['latitude']) if profile_data['latitude'] else None
    if 'longitude' in profile_data:
        customer.longitude = str(profile_data['longitude']) if profile_data['longitude'] else None

    db.commit()

    # Update preferences if provided
    if 'preferences' in profile_data:
        prefs = profile_data['preferences']
        preference = db.query(CustomerPreference).filter(
            CustomerPreference.customer_id == customer.id
        ).first()

        if preference:
            if 'pref_price_sensitivity' in prefs:
                preference.pref_price_sensitivity = prefs['pref_price_sensitivity']
            if 'pref_max_distance_km' in prefs:
                preference.pref_max_distance_km = prefs['pref_max_distance_km']
            if 'pref_spice_level' in prefs:
                preference.pref_spice_level = prefs['pref_spice_level']
            if 'pref_sweetness_level' in prefs:
                preference.pref_sweetness_level = prefs['pref_sweetness_level']
            if 'pref_savory_level' in prefs:
                preference.pref_savory_level = prefs['pref_savory_level']

            preference.updated_at = datetime.utcnow()
        else:
            # Create new preferences
            new_pref = CustomerPreference(
                customer_id=customer.id,
                pref_price_sensitivity=prefs.get('pref_price_sensitivity', 'medium'),
                pref_max_distance_km=prefs.get('pref_max_distance_km', 10),
                pref_spice_level=prefs.get('pref_spice_level', 0),
                pref_sweetness_level=prefs.get('pref_sweetness_level', 0),
                pref_savory_level=prefs.get('pref_savory_level', 0),
            )
            db.add(new_pref)

        db.commit()

    return {
        "message": "Profile updated successfully",
        "customer": {
            "id": customer.id,
            "full_name": customer.full_name,
            "phone": customer.phone,
            "address": customer.address,
            "latitude": customer.latitude,
            "longitude": customer.longitude,
        }
    }


@router.put("/profile", response_model=CustomerResponse)
async def update_customer_profile(
    profile_data: CustomerUpdate,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Update customer profile

    - **full_name**: Full name
    - **phone**: Phone number
    - **address**: Address
    - **latitude, longitude**: Location coordinates
    - **avatar_url**: Profile picture URL
    - **date_of_birth**: Date of birth
    """
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )

    # Update fields
    update_data = profile_data.model_dump(exclude_unset=True)

    # Convert float to string for coordinates
    if 'latitude' in update_data and update_data['latitude'] is not None:
        update_data['latitude'] = str(update_data['latitude'])
    if 'longitude' in update_data and update_data['longitude'] is not None:
        update_data['longitude'] = str(update_data['longitude'])

    for field, value in update_data.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)

    return customer


# =====================
# Customer Preferences Endpoints
# =====================

@router.get("/preferences", response_model=CustomerPreferenceResponse)
async def get_customer_preferences(
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get customer taste preferences

    Returns all fuzzy preference parameters
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
        # Create default preferences
        preference = CustomerPreference(
            customer_id=customer.id,
            pref_price_importance=0.5,
            pref_price_sensitivity='medium',
            pref_distance_importance=0.3,
            pref_max_distance_km=10,
            pref_popularity_importance=0.2,
            pref_spice_level=0,
            pref_sweetness_level=0,
            pref_savory_level=0
        )
        db.add(preference)
        db.commit()
        db.refresh(preference)

    return preference


@router.put("/preferences", response_model=CustomerPreferenceResponse)
async def update_customer_preferences(
    pref_data: CustomerPreferenceUpdate,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Update customer taste preferences

    These preferences are used for Fuzzy Logic calculations:

    - **pref_price_importance**: How important price is (0-1)
    - **pref_price_sensitivity**: Price preference ('cheap', 'medium', 'expensive_flexible')
    - **pref_distance_importance**: How important distance is (0-1)
    - **pref_max_distance_km**: Maximum distance willing to travel (1-100 km)
    - **pref_popularity_importance**: How important popularity is (0-1)
    - **pref_spice_level**: Preferred spice level (0-5, 0=no preference)
    - **pref_sweetness_level**: Preferred sweetness level (0-5)
    - **pref_savory_level**: Preferred savory/umami level (0-5)
    - **pref_cuisines**: List of preferred cuisine types
    - **pref_dietary_restrictions**: List of dietary restrictions
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
        # Create new preferences
        preference = CustomerPreference(
            customer_id=customer.id,
            **pref_data.model_dump(exclude_unset=True)
        )
        db.add(preference)
    else:
        # Update existing preferences
        update_data = pref_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(preference, field, value)

    db.commit()
    db.refresh(preference)

    return preference


# =====================
# Rating Endpoints
# =====================

@router.post("/ratings", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
async def create_rating(
    rating_data: RatingCreate,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Submit a rating for a menu item

    - **menu_id**: ID of menu being rated
    - **score**: Rating from 1 to 5
    - **review_text**: Optional review text (max 1000 chars)

    Note: One rating per menu per customer (will update if exists)
    """
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )

    # Check if menu exists
    menu = db.query(Menu).filter(Menu.id == rating_data.menu_id).first()
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu not found"
        )

    # Check if rating already exists
    existing_rating = db.query(Rating).filter(
        Rating.customer_id == customer.id,
        Rating.menu_id == rating_data.menu_id
    ).first()

    if existing_rating:
        # Update existing rating
        update_data = rating_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field != 'menu_id':  # Don't update menu_id
                setattr(existing_rating, field, value)
        db.commit()
        db.refresh(existing_rating)
        return existing_rating

    # Create new rating
    rating = Rating(
        customer_id=customer.id,
        **rating_data.model_dump()
    )
    db.add(rating)
    db.commit()
    db.refresh(rating)

    return rating


@router.get("/ratings", response_model=List[RatingResponse])
async def get_my_ratings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get all ratings from current customer

    Returns paginated list of customer's ratings
    """
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )

    ratings = db.query(Rating).filter(
        Rating.customer_id == customer.id
    ).order_by(Rating.created_at.desc()).offset(skip).limit(limit).all()

    return ratings


@router.get("/ratings/{rating_id}", response_model=RatingWithDetails)
async def get_rating_detail(
    rating_id: str,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get specific rating detail with menu info

    Only returns ratings belonging to current customer
    """
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()

    rating = db.query(Rating).filter(
        Rating.id == rating_id,
        Rating.customer_id == customer.id
    ).first()

    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )

    # Get menu details
    menu = db.query(Menu).filter(Menu.id == rating.menu_id).first()

    rating.menu_item_name = menu.item_name
    rating.menu_price = float(menu.price)
    rating.customer_full_name = customer.full_name

    return rating


@router.put("/ratings/{rating_id}", response_model=RatingResponse)
async def update_rating(
    rating_id: str,
    rating_data: RatingUpdate,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Update existing rating

    Can update score and/or review_text
    """
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()

    rating = db.query(Rating).filter(
        Rating.id == rating_id,
        Rating.customer_id == customer.id
    ).first()

    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )

    # Update fields
    update_data = rating_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rating, field, value)

    db.commit()
    db.refresh(rating)

    return rating


@router.delete("/ratings/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rating(
    rating_id: str,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Delete a rating

    Permanently removes customer's rating for a menu
    """
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()

    rating = db.query(Rating).filter(
        Rating.id == rating_id,
        Rating.customer_id == customer.id
    ).first()

    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )

    db.delete(rating)
    db.commit()

    return None
