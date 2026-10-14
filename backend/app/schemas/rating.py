"""
Rating-related Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RatingCreate(BaseModel):
    """Schema for creating a rating"""
    menu_id: str = Field(..., description="ID of menu to rate")
    score: int = Field(..., ge=1, le=5, description="Rating score from 1 to 5 (whole numbers only)")
    review_text: Optional[str] = Field(None, max_length=500, description="Optional review text")


class RatingResponse(BaseModel):
    """Schema for rating response"""
    id: str
    customer_id: str
    menu_id: str
    score: int
    review_text: Optional[str] = None
    is_verified_purchase: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    menu_name: Optional[str] = None
    merchant_name: Optional[str] = None


class RatingListItem(BaseModel):
    """Schema for rating in list"""
    id: str
    menu_id: str
    score: int
    review_text: Optional[str] = None
    created_at: datetime
    menu_name: str
    merchant_name: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    customer_name: Optional[str] = None


class RatingListResponse(BaseModel):
    """Schema for list of ratings"""
    ratings: List[RatingListItem]
    total: int
    limit: int
    offset: int
