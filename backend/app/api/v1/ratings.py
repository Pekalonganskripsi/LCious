"""
Rating API endpoints

API untuk submit dan manage rating menu oleh customer
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.api.deps import get_db, get_current_customer
from app.schemas.rating import (
    RatingCreate,
    RatingResponse,
    RatingListResponse
)
from app.models.user import User, Customer
from app.models.rating import Rating
from app.models.menu import Menu

router = APIRouter()


@router.post("/submit", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
async def submit_rating(
    rating_data: RatingCreate,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Submit rating untuk sebuah menu

    ## Rating System

    Submit rating (1-5) untuk menu yang sudah dicoba.
    Rating ini akan mempengaruhi:
    - Collaborative Filtering calculations
    - Rekomendasi untuk user lain
    - Menu popularity score

    ## Parameters

    - **menu_id**: ID menu yang ingin dinilai
    - **score**: Rating 1-5
    - **review_text**: Review opsional (optional)

    ## Response

    Returns rating yang baru dibuat dengan:
    - Rating ID
    - Score dan review
    - Menu details
    - Submission timestamp
    """
    # Get customer
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

    # Check if user already rated this menu
    existing_rating = db.query(Rating).filter(
        Rating.customer_id == customer.id,
        Rating.menu_id == rating_data.menu_id
    ).first()

    if existing_rating:
        # Update existing rating
        existing_rating.score = rating_data.score
        existing_rating.review_text = rating_data.review_text
        existing_rating.is_verified_purchase = True
        existing_rating.updated_at = datetime.utcnow()

        db.commit()

        # Update menu average rating
        ratings = db.query(Rating).filter(Rating.menu_id == rating_data.menu_id).all()
        if ratings:
            avg_score = sum(r.score for r in ratings) / len(ratings)
            menu.average_rating = avg_score
            menu.total_ratings = len(ratings)

        # Update merchant average rating (calculate from ALL merchant's menus)
        if menu.merchant:
            from app.models.menu import Menu as MenuItem
            # Get all menus for this merchant
            merchant_menu_ids = db.query(MenuItem.id).filter(MenuItem.merchant_id == menu.merchant.id).all()
            merchant_menu_ids = [m[0] for m in merchant_menu_ids]

            if merchant_menu_ids:
                # Get ALL ratings for ALL menus from this merchant
                all_merchant_ratings = db.query(Rating).filter(Rating.menu_id.in_(merchant_menu_ids)).all()
                if all_merchant_ratings:
                    merchant_avg = sum(r.score for r in all_merchant_ratings) / len(all_merchant_ratings)
                    menu.merchant.average_rating = str(merchant_avg)  # Store as string per model definition
                    menu.merchant.total_reviews = str(len(all_merchant_ratings))

        db.commit()
        db.refresh(existing_rating)

        return {
            "id": str(existing_rating.id),
            "customer_id": str(existing_rating.customer_id),
            "menu_id": str(existing_rating.menu_id),
            "score": existing_rating.score,
            "review_text": existing_rating.review_text,
            "is_verified_purchase": existing_rating.is_verified_purchase,
            "created_at": existing_rating.created_at,
            "updated_at": existing_rating.updated_at,
            "menu_name": menu.item_name,
            "merchant_name": menu.merchant.shop_name if menu.merchant else None,
        }

    # Create new rating
    new_rating = Rating(
        customer_id=customer.id,
        menu_id=rating_data.menu_id,
        score=rating_data.score,
        review_text=rating_data.review_text,
        is_verified_purchase=True
    )

    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)

    # Update menu average rating
    ratings = db.query(Rating).filter(Rating.menu_id == rating_data.menu_id).all()
    if ratings:
        avg_score = sum(r.score for r in ratings) / len(ratings)
        menu.average_rating = avg_score
        menu.total_ratings = len(ratings)

    # Update merchant average rating (calculate from ALL merchant's menus)
    if menu.merchant:
        from app.models.menu import Menu as MenuItem
        # Get all menus for this merchant
        merchant_menu_ids = db.query(MenuItem.id).filter(MenuItem.merchant_id == menu.merchant.id).all()
        merchant_menu_ids = [m[0] for m in merchant_menu_ids]

        if merchant_menu_ids:
            # Get ALL ratings for ALL menus from this merchant
            all_merchant_ratings = db.query(Rating).filter(Rating.menu_id.in_(merchant_menu_ids)).all()
            if all_merchant_ratings:
                merchant_avg = sum(r.score for r in all_merchant_ratings) / len(all_merchant_ratings)
                menu.merchant.average_rating = str(merchant_avg)  # Store as string per model definition
                menu.merchant.total_reviews = str(len(all_merchant_ratings))

    db.commit()

    return {
        "id": str(new_rating.id),
        "customer_id": str(new_rating.customer_id),
        "menu_id": str(new_rating.menu_id),
        "score": new_rating.score,
        "review_text": new_rating.review_text,
        "is_verified_purchase": new_rating.is_verified_purchase,
        "created_at": new_rating.created_at,
        "updated_at": new_rating.updated_at,
        "menu_name": menu.item_name,
        "merchant_name": menu.merchant.shop_name if menu.merchant else None,
    }


@router.get("/my-ratings", response_model=RatingListResponse)
async def get_my_ratings(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get semua rating yang pernah Anda berikan

    Menampilkan history rating untuk melihat apa saja yang sudah Anda nilai.
    """
    # Get customer
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )

    # Get ratings with menu and merchant info
    ratings_query = db.query(Rating, Menu, Customer).join(
        Menu, Rating.menu_id == Menu.id
    ).join(
        Customer, Rating.customer_id == Customer.id
    ).filter(
        Rating.customer_id == customer.id
    ).order_by(Rating.created_at.desc())

    total = ratings_query.count()
    ratings = ratings_query.limit(limit).offset(offset).all()

    rating_list = []
    for rating, menu, cust in ratings:
        rating_list.append({
            "id": str(rating.id),
            "menu_id": str(rating.menu_id),
            "score": rating.score,
            "review_text": rating.review_text,
            "created_at": rating.created_at,
            "menu_name": menu.item_name,
            "merchant_name": menu.merchant.shop_name if menu.merchant else None,
            "price": menu.price,
            "image_url": menu.image_url,
        })

    return {
        "ratings": rating_list,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/menu/{menu_id}/my-rating", response_model=RatingResponse)
async def get_my_rating_for_menu(
    menu_id: str,
    current_user: User = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get rating Anda untuk sebuah menu tertentu

    Cek apakah Anda sudah pernah memberi rating untuk menu ini.
    """
    # Get customer
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )

    # Get rating
    rating = db.query(Rating).filter(
        Rating.customer_id == customer.id,
        Rating.menu_id == menu_id
    ).first()

    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )

    # Get menu details
    menu = db.query(Menu).filter(Menu.id == rating.menu_id).first()

    return {
        "id": str(rating.id),
        "customer_id": str(rating.customer_id),
        "menu_id": str(rating.menu_id),
        "score": rating.score,
        "review_text": rating.review_text,
        "is_verified_purchase": rating.is_verified_purchase,
        "created_at": rating.created_at,
        "updated_at": rating.updated_at,
        "menu_name": menu.item_name if menu else None,
        "merchant_name": menu.merchant.shop_name if menu and menu.merchant else None,
    }


@router.get("/menu/{menu_id}", response_model=RatingListResponse)
async def get_menu_ratings(
    menu_id: str,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get semua rating untuk sebuah menu

    Menampilkan review dari semua user untuk menu tertentu.
    """
    # Get ratings
    ratings_query = db.query(Rating, Customer).join(
        Customer, Rating.customer_id == Customer.id
    ).filter(
        Rating.menu_id == menu_id
    ).order_by(Rating.created_at.desc())

    total = ratings_query.count()
    ratings = ratings_query.limit(limit).offset(offset).all()

    # Get menu details
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu not found"
        )

    rating_list = []
    for rating, customer in ratings:
        rating_list.append({
            "id": str(rating.id),
            "customer_id": str(rating.customer_id),
            "menu_id": str(rating.menu_id),
            "score": rating.score,
            "review_text": rating.review_text,
            "created_at": rating.created_at,
            "customer_name": customer.full_name if customer.user else None,
            "menu_name": menu.item_name,
            "merchant_name": menu.merchant.shop_name if menu.merchant else None,
        })

    return {
        "ratings": rating_list,
        "total": total,
        "limit": limit,
        "offset": offset
    }
