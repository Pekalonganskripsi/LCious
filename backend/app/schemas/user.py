"""
User-related Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


# =====================
# Base Schemas
# =====================

class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=6, max_length=100)
    role: UserRole = UserRole.CUSTOMER


class UserUpdate(BaseModel):
    """Schema for updating user"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)


class UserInDB(UserBase):
    """Schema for user in database"""
    id: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    """Schema for user response (safe data)"""
    pass


# =====================
# Auth Schemas
# =====================

class LoginRequest(BaseModel):
    """Schema for login request"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenPayload(BaseModel):
    """Schema for token payload"""
    sub: str  # user_id
    role: UserRole
    exp: Optional[int] = None


# =====================
# Customer Schemas
# =====================

class CustomerBase(BaseModel):
    """Base customer schema"""
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None


class CustomerCreate(CustomerBase):
    """Schema for creating customer"""
    username: str = Field(..., min_length=3, max_length=50, description="Username for login")
    password: str = Field(..., min_length=6)
    email: EmailStr
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    date_of_birth: Optional[datetime] = None
    preferences: Optional["CustomerPreferenceCreate"] = None


class CustomerUpdate(BaseModel):
    """Schema for updating customer"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    avatar_url: Optional[str] = None
    date_of_birth: Optional[datetime] = None


class CustomerResponse(CustomerBase):
    """Schema for customer response"""
    id: str
    user_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CustomerWithUser(CustomerResponse):
    """Customer with user info"""
    email: EmailStr
    username: str
    is_verified: bool


# =====================
# Customer Preference Schemas
# =====================

class CustomerPreferenceBase(BaseModel):
    """Base customer preference schema"""
    pref_price_importance: Optional[float] = Field(None, ge=0, le=1)
    pref_price_sensitivity: Optional[str] = Field(None, pattern="^(cheap|medium|expensive_flexible)$")
    pref_distance_importance: Optional[float] = Field(None, ge=0, le=1)
    pref_max_distance_km: Optional[int] = Field(None, ge=1, le=100)
    pref_popularity_importance: Optional[float] = Field(None, ge=0, le=1)
    pref_spice_level: Optional[int] = Field(None, ge=0, le=5)
    pref_sweetness_level: Optional[int] = Field(None, ge=0, le=5)
    pref_savory_level: Optional[int] = Field(None, ge=0, le=5)
    pref_cuisines: Optional[str] = Field(None, max_length=200)  # Changed from list to string
    pref_dietary_restrictions: Optional[str] = Field(None, max_length=500)  # Changed from list to string


class CustomerPreferenceCreate(CustomerPreferenceBase):
    """Schema for creating customer preference"""
    pass


class CustomerPreferenceUpdate(CustomerPreferenceBase):
    """Schema for updating customer preference"""
    pass


class CustomerPreferenceResponse(CustomerPreferenceBase):
    """Schema for customer preference response"""
    id: str
    customer_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================
# Merchant Schemas
# =====================

class MerchantBase(BaseModel):
    """Base merchant schema"""
    shop_name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    address: str
    phone: Optional[str] = Field(None, max_length=20)
    price_range: Optional[str] = Field(None, pattern="^\\$\\${0,2}$")  # $, $$, or $$$
    cuisine_type: Optional[str] = Field(None, max_length=50)


class MerchantCreate(MerchantBase):
    """Schema for creating merchant"""
    password: str = Field(..., min_length=6)
    email: EmailStr
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    opening_hours: Optional[dict] = None


class MerchantUpdate(BaseModel):
    """Schema for updating merchant"""
    shop_name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    opening_hours: Optional[dict] = None
    price_range: Optional[str] = Field(None, pattern="^\\$\\${0,2}$")
    cuisine_type: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[str] = None
    cover_image_url: Optional[str] = None


class MerchantResponse(MerchantBase):
    """Schema for merchant response"""
    id: str
    user_id: str
    latitude: float
    longitude: float
    opening_hours: Optional[dict] = None
    avatar_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    qr_code_url: Optional[str] = None
    is_active: bool
    average_rating: Optional[float] = None
    total_reviews: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MerchantWithUser(MerchantResponse):
    """Merchant with user info"""
    email: EmailStr
    username: str
    is_verified: bool
