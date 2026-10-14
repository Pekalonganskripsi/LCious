"""
Menu-related Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.menu import MenuCategory


# =====================
# Menu Schemas
# =====================

class MenuBase(BaseModel):
    """Base menu schema"""
    item_name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0, le=1000000)
    category: MenuCategory = MenuCategory.FOOD


class MenuCreate(MenuBase):
    """Schema for creating menu"""
    image_url: Optional[str] = None
    spice_level: Optional[int] = Field(None, ge=0, le=5)
    sweetness_level: Optional[int] = Field(None, ge=0, le=5)
    savory_level: Optional[int] = Field(None, ge=0, le=5)
    tags: Optional[list[str]] = None


class MenuUpdate(BaseModel):
    """Schema for updating menu"""
    item_name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0, le=1000000)
    category: Optional[MenuCategory] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None
    spice_level: Optional[int] = Field(None, ge=0, le=5)
    sweetness_level: Optional[int] = Field(None, ge=0, le=5)
    savory_level: Optional[int] = Field(None, ge=0, le=5)
    tags: Optional[list[str]] = None


class MenuResponse(MenuBase):
    """Schema for menu response"""
    id: str
    merchant_id: str
    image_url: Optional[str] = None
    is_available: bool
    spice_level: Optional[int] = None
    sweetness_level: Optional[int] = None
    savory_level: Optional[int] = None
    popularity_score: int
    total_ratings: int
    average_rating: Optional[float] = None
    tags: Optional[list[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MenuWithMerchant(MenuResponse):
    """Menu with merchant info"""
    merchant_shop_name: str
    merchant_address: str
    merchant_latitude: float
    merchant_longitude: float
    merchant_cuisine_type: Optional[str] = None


# =====================
# Rating Schemas
# =====================

class RatingBase(BaseModel):
    """Base rating schema"""
    score: float = Field(..., ge=1, le=5)
    review_text: Optional[str] = Field(None, max_length=1000)


class RatingCreate(RatingBase):
    """Schema for creating rating"""
    menu_id: str


class RatingUpdate(BaseModel):
    """Schema for updating rating"""
    score: Optional[float] = Field(None, ge=1, le=5)
    review_text: Optional[str] = Field(None, max_length=1000)


class RatingResponse(RatingBase):
    """Schema for rating response"""
    id: str
    customer_id: str
    menu_id: str
    is_verified_purchase: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RatingWithDetails(RatingResponse):
    """Rating with menu and customer details"""
    menu_item_name: str
    menu_price: float
    customer_full_name: str


# =====================
# Fuzzy Criteria Schemas
# =====================

class FuzzyCriteriaBase(BaseModel):
    """Base fuzzy criteria schema"""
    criteria_name: str = Field(..., pattern="^(price|distance|popularity)$")
    sub_criteria: str = Field(..., min_length=2, max_length=50)
    min_val: float = Field(..., ge=0)
    mid_val: Optional[float] = Field(None, ge=0)
    max_val: float = Field(..., ge=0)
    membership_function: str = Field(default="triangular", pattern="^(triangular|trapezoidal)$")


class FuzzyCriteriaCreate(FuzzyCriteriaBase):
    """Schema for creating fuzzy criteria"""
    pass


class FuzzyCriteriaUpdate(BaseModel):
    """Schema for updating fuzzy criteria"""
    min_val: Optional[float] = Field(None, ge=0)
    mid_val: Optional[float] = Field(None, ge=0)
    max_val: Optional[float] = Field(None, ge=0)
    membership_function: Optional[str] = Field(None, pattern="^(triangular|trapezoidal)$")


class FuzzyCriteriaResponse(FuzzyCriteriaBase):
    """Schema for fuzzy criteria response"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
