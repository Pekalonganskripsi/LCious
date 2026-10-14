"""
Public Menu API endpoints

API untuk mengambil informasi menu (tanpa authentication)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db
from app.models.menu import Menu
from app.models.user import Merchant
from app.models.rating import Rating

router = APIRouter()


@router.get("/{menu_id}")
async def get_menu_detail(
    menu_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific menu

    Returns menu with merchant info and ratings
    """
    # Get menu
    menu = db.query(Menu).filter(Menu.id == menu_id).first()

    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu not found"
        )

    # Get merchant
    merchant = db.query(Merchant).filter(Merchant.id == menu.merchant_id).first()

    # Get ratings
    from app.models.user import Customer

    ratings_query = (
        db.query(Rating, Customer)
        .join(Customer, Rating.customer_id == Customer.id)
        .filter(Rating.menu_id == menu_id)
        .order_by(Rating.created_at.desc())
        .limit(10)
        .all()
    )

    ratings_data = [
        {
            "id": rating.id,
            "customer_name": customer.full_name,
            "score": rating.score,
            "review_text": rating.review_text,
            "created_at": rating.created_at,
        }
        for rating, customer in ratings_query
    ]

    return {
        "menu": {
            "id": menu.id,
            "item_name": menu.item_name,
            "description": menu.description,
            "price": menu.price,
            "category": menu.category,
            "spice_level": menu.spice_level,
            "sweetness_level": menu.sweetness_level,
            "savory_level": menu.savory_level,
            "image_url": menu.image_url,
            "is_available": menu.is_available,
            "average_rating": float(menu.average_rating) if menu.average_rating else 0.0,
            "total_ratings": int(menu.total_ratings) if menu.total_ratings else 0,
            "popularity_score": menu.popularity_score,
            "created_at": menu.created_at,
        },
        "merchant": {
            "id": merchant.id,
            "shop_name": merchant.shop_name,
            "description": merchant.description,
            "address": merchant.address,
            "latitude": merchant.latitude,
            "longitude": merchant.longitude,
            "phone": merchant.phone,
            "opening_hours": merchant.opening_hours,
            "price_range": merchant.price_range,
            "cuisine_type": merchant.cuisine_type,
            "average_rating": float(merchant.average_rating) if merchant.average_rating else 0.0,
        } if merchant else None,
        "ratings": ratings_data
    }


@router.get("")
async def list_menus(
    skip: int = 0,
    limit: int = 50,
    category: str = None,
    db: Session = Depends(get_db)
):
    """
    List all available menus

    Returns paginated list of menus
    """
    query = db.query(Menu).filter(Menu.is_available == True)

    if category:
        query = query.filter(Menu.category == category)

    menus = query.order_by(Menu.popularity_score.desc()).offset(skip).limit(limit).all()

    # Get merchant info for each menu
    menu_data = []
    for menu in menus:
        merchant = db.query(Merchant).filter(Merchant.id == menu.merchant_id).first()
        menu_data.append({
            "id": menu.id,
            "menu_id": menu.id,
            "merchant_id": menu.merchant_id,
            "item_name": menu.item_name,
            "description": menu.description,
            "price": menu.price,
            "category": menu.category,
            "spice_level": menu.spice_level,
            "sweetness_level": menu.sweetness_level,
            "savory_level": menu.savory_level,
            "image_url": menu.image_url,
            "is_available": menu.is_available,
            "average_rating": float(menu.average_rating) if menu.average_rating else 0.0,
            "total_ratings": int(menu.total_ratings) if menu.total_ratings else 0,
            "popularity_score": menu.popularity_score or 0,
            "merchant": {
                "id": merchant.id,
                "shop_name": merchant.shop_name,
                "address": merchant.address,
                "cuisine_type": merchant.cuisine_type,
            } if merchant else None,
        })

    return {
        "menus": menu_data,
        "total": len(menu_data),
        "skip": skip,
        "limit": limit
    }
