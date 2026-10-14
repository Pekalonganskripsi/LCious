"""
Merchant API endpoints

API untuk merchant mengelola menu dan melihat statistik
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import os
import uuid
from pathlib import Path

from app.api.deps import get_db, get_current_merchant
from app.models.user import User, Merchant
from app.models.menu import Menu
from app.models.rating import Rating

router = APIRouter()

# Upload directory
UPLOAD_DIR = Path("uploads/menu_images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# Schemas
class MenuCreate(BaseModel):
    """Schema for creating menu"""
    item_name: str
    description: str = ""
    price: float
    category: str = "makanan"
    spice_level: int = 0
    sweetness_level: int = 0
    savory_level: int = 0
    image_url: str = ""
    is_available: bool = True


class MenuResponse(BaseModel):
    """Schema for menu response"""
    id: str
    item_name: str
    description: str
    price: float
    category: str
    spice_level: int
    sweetness_level: int
    savory_level: int
    image_url: str
    is_available: bool
    average_rating: float
    total_ratings: int
    created_at: datetime


@router.get("/my-stats")
async def get_merchant_stats(
    current_user: User = Depends(get_current_merchant),
    db: Session = Depends(get_db)
):
    """
    Get merchant statistics

    Returns:
    - Total menus
    - Total ratings
    - Average rating
    - Total views (placeholder)
    """
    # Get merchant profile
    merchant = db.query(Merchant).filter(Merchant.user_id == current_user.id).first()

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant profile not found"
        )

    # Count menus
    total_menus = db.query(Menu).filter(Menu.merchant_id == merchant.id).count()

    # Get all menu IDs for this merchant
    menu_ids = [m.id for m in db.query(Menu.id).filter(Menu.merchant_id == merchant.id).all()]

    # Count ratings
    total_ratings = db.query(Rating).filter(Rating.menu_id.in_(menu_ids)).count()

    # Calculate average rating
    avg_rating_result = (
        db.query(func.avg(Rating.score))
        .filter(Rating.menu_id.in_(menu_ids))
        .scalar()
    )
    average_rating = float(avg_rating_result) if avg_rating_result else 0.0

    # Total views (placeholder - could be tracked separately)
    total_views = 0

    return {
        "totalMenus": total_menus,
        "totalRatings": total_ratings,
        "averageRating": average_rating,
        "totalViews": total_views,
    }


@router.get("/my-menus")
async def get_merchant_menus(
    current_user: User = Depends(get_current_merchant),
    db: Session = Depends(get_db)
):
    """
    Get all menus for this merchant

    Returns list of all menus owned by the merchant
    """
    # Get merchant profile
    merchant = db.query(Merchant).filter(Merchant.user_id == current_user.id).first()

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant profile not found"
        )

    # Get menus
    menus = (
        db.query(Menu)
        .filter(Menu.merchant_id == merchant.id)
        .order_by(Menu.created_at.desc())
        .all()
    )

    return {
        "menus": [
            {
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
                "created_at": menu.created_at,
            }
            for menu in menus
        ]
    }


@router.post("/menus")
async def create_menu(
    menu_data: MenuCreate,
    current_user: User = Depends(get_current_merchant),
    db: Session = Depends(get_db)
):
    """
    Create a new menu

    Add a new menu item to the merchant's catalog
    """
    # Get merchant profile
    merchant = db.query(Merchant).filter(Merchant.user_id == current_user.id).first()

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant profile not found"
        )

    # Create new menu
    new_menu = Menu(
        merchant_id=merchant.id,
        item_name=menu_data.item_name,
        description=menu_data.description,
        price=menu_data.price,
        category=menu_data.category,
        spice_level=menu_data.spice_level,
        sweetness_level=menu_data.sweetness_level,
        savory_level=menu_data.savory_level,
        image_url=menu_data.image_url,
        is_available=menu_data.is_available,
        popularity_score=0.0,
    )

    db.add(new_menu)
    db.commit()
    db.refresh(new_menu)

    return {
        "id": new_menu.id,
        "item_name": new_menu.item_name,
        "message": "Menu created successfully"
    }


@router.put("/menus/{menu_id}")
async def update_menu(
    menu_id: str,
    menu_data: MenuCreate,
    current_user: User = Depends(get_current_merchant),
    db: Session = Depends(get_db)
):
    """
    Update an existing menu

    Update menu details (name, description, price, etc.)
    """
    # Get merchant profile
    merchant = db.query(Merchant).filter(Merchant.user_id == current_user.id).first()

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant profile not found"
        )

    # Get menu and verify ownership
    menu = db.query(Menu).filter(
        Menu.id == menu_id,
        Menu.merchant_id == merchant.id
    ).first()

    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu not found or you don't have permission"
        )

    # Update menu fields
    menu.item_name = menu_data.item_name
    menu.description = menu_data.description
    menu.price = menu_data.price
    menu.category = menu_data.category
    menu.spice_level = menu_data.spice_level
    menu.sweetness_level = menu_data.sweetness_level
    menu.savory_level = menu_data.savory_level
    menu.image_url = menu_data.image_url
    menu.is_available = menu_data.is_available
    menu.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(menu)

    return {
        "id": menu.id,
        "item_name": menu.item_name,
        "message": "Menu updated successfully"
    }


@router.delete("/menus/{menu_id}")
async def delete_menu(
    menu_id: str,
    current_user: User = Depends(get_current_merchant),
    db: Session = Depends(get_db)
):
    """
    Delete a menu

    Permanently remove a menu from the catalog
    """
    # Get merchant profile
    merchant = db.query(Merchant).filter(Merchant.user_id == current_user.id).first()

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant profile not found"
        )

    # Get menu and verify ownership
    menu = db.query(Menu).filter(
        Menu.id == menu_id,
        Menu.merchant_id == merchant.id
    ).first()

    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu not found or you don't have permission"
        )

    # Delete menu (ratings will be cascade deleted due to FK relationship)
    db.delete(menu)
    db.commit()

    return {
        "message": "Menu deleted successfully"
    }


@router.post("/menus/{menu_id}/upload-image")
async def upload_menu_image(
    menu_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_merchant),
    db: Session = Depends(get_db)
):
    """
    Upload menu image

    Upload an image file for a menu item. Optional - menu can work without image.
    """
    # Get merchant profile
    merchant = db.query(Merchant).filter(Merchant.user_id == current_user.id).first()

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant profile not found"
        )

    # Get menu and verify ownership
    menu = db.query(Menu).filter(
        Menu.id == menu_id,
        Menu.merchant_id == merchant.id
    ).first()

    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu not found or you don't have permission"
        )

    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )

    # Generate unique filename
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    unique_filename = f"{menu_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    # Save file
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Update menu with image URL
    # For local development, use relative path
    image_url = f"/uploads/menu_images/{unique_filename}"
    menu.image_url = image_url
    menu.updated_at = datetime.utcnow()
    db.commit()

    return {
        "image_url": image_url,
        "message": "Image uploaded successfully"
    }


@router.get("/my-ratings")
async def get_merchant_ratings(
    current_user: User = Depends(get_current_merchant),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """
    Get all ratings for merchant's menus

    Returns list of all ratings with customer and menu info
    """
    # Get merchant profile
    merchant = db.query(Merchant).filter(Merchant.user_id == current_user.id).first()

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant profile not found"
        )

    # Get all menu IDs for this merchant
    from app.models.user import Customer

    menu_ids = [m.id for m in db.query(Menu.id).filter(Menu.merchant_id == merchant.id).all()]

    # Get ratings
    ratings = (
        db.query(Rating)
        .join(Menu, Rating.menu_id == Menu.id)
        .join(Customer, Rating.customer_id == Customer.id)
        .filter(Rating.menu_id.in_(menu_ids))
        .order_by(Rating.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "ratings": [
            {
                "id": rating.id,
                "menu_id": rating.menu_id,
                "menu_name": rating.menu.item_name,
                "customer_name": rating.customer.full_name,
                "score": rating.score,
                "review_text": rating.review_text,
                "created_at": rating.created_at,
            }
            for rating in ratings
        ],
        "total": len(ratings),
        "limit": limit,
        "offset": offset
    }


@router.get("/my-profile")
async def get_merchant_profile(
    current_user: User = Depends(get_current_merchant),
    db: Session = Depends(get_db)
):
    """
    Get merchant profile

    Returns current merchant profile data
    """
    merchant = db.query(Merchant).filter(Merchant.user_id == current_user.id).first()

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant profile not found"
        )

    return {
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
        "avatar_url": merchant.avatar_url,
        "is_active": merchant.is_active,
    }


@router.put("/my-profile")
async def update_merchant_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_merchant),
    db: Session = Depends(get_db)
):
    """
    Update merchant profile

    Update shop name, address, location, and other merchant info
    """
    merchant = db.query(Merchant).filter(Merchant.user_id == current_user.id).first()

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant profile not found"
        )

    # Update fields
    if 'shop_name' in profile_data:
        merchant.shop_name = profile_data['shop_name']
    if 'description' in profile_data:
        merchant.description = profile_data['description']
    if 'address' in profile_data:
        merchant.address = profile_data['address']
    if 'latitude' in profile_data:
        merchant.latitude = str(profile_data['latitude']) if profile_data['latitude'] else merchant.latitude
    if 'longitude' in profile_data:
        merchant.longitude = str(profile_data['longitude']) if profile_data['longitude'] else merchant.longitude
    if 'phone' in profile_data:
        merchant.phone = profile_data['phone']
    if 'opening_hours' in profile_data:
        merchant.opening_hours = profile_data['opening_hours']
    if 'price_range' in profile_data:
        merchant.price_range = profile_data['price_range']
    if 'cuisine_type' in profile_data:
        merchant.cuisine_type = profile_data['cuisine_type']

    merchant.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(merchant)

    return {
        "message": "Profile updated successfully",
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
    }
