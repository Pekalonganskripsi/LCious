"""
User models for authentication and authorization
"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from app.db.session import Base
import enum
import uuid


class UserRole(str, enum.Enum):
    """User roles"""
    CUSTOMER = "customer"
    MERCHANT = "merchant"
    SUPERADMIN = "superadmin"


class User(Base, BaseModel):
    """
    Main user table for authentication
    All users (customer, merchant, superadmin) inherit from this
    """
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, default=lambda: f"u_{uuid.uuid4().hex[:12]}")  # Auto-generate ID
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default=UserRole.CUSTOMER)

    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    last_login = Column(DateTime, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="user", uselist=False, cascade="all, delete-orphan")
    merchant = relationship("Merchant", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"


class Customer(Base, BaseModel):
    """
    Customer profile
    Extended profile for end-users who order food
    """
    __tablename__ = "customers"

    id = Column(String(50), primary_key=True, default=lambda: f"c_{uuid.uuid4().hex[:12]}")  # Auto-generate ID
    user_id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(String, nullable=True)

    # Geolocation for distance calculation
    latitude = Column(String(20), nullable=True)  # Stored as string to avoid precision issues
    longitude = Column(String(20), nullable=True)

    avatar_url = Column(String, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="customer")
    preferences = relationship("CustomerPreference", back_populates="customer", uselist=False, cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="customer", cascade="all, delete-orphan")
    recommendation_logs = relationship("RecommendationLog", back_populates="customer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Customer(id={self.id}, full_name={self.full_name})>"


class Merchant(Base, BaseModel):
    """
    Merchant (UMKM Culinary) profile
    Business owners who sell food
    """
    __tablename__ = "merchants"

    id = Column(String(50), primary_key=True, default=lambda: f"m_{uuid.uuid4().hex[:12]}")  # Auto-generate ID
    user_id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    shop_name = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    address = Column(String, nullable=False)

    # Geolocation
    latitude = Column(String(20), nullable=False)
    longitude = Column(String(20), nullable=False)

    phone = Column(String(20), nullable=True)
    opening_hours = Column(String, nullable=True)  # JSON stored as string
    price_range = Column(String(10), nullable=True)  # '$', '$$', '$$$'
    cuisine_type = Column(String(50), nullable=True, index=True)

    avatar_url = Column(String, nullable=True)
    cover_image_url = Column(String, nullable=True)
    qr_code_url = Column(String, nullable=True)

    is_active = Column(Boolean, default=True, index=True)

    # Rating aggregations
    average_rating = Column(String(10), nullable=True)  # Stored as string
    total_reviews = Column(String, nullable=True)

    # Relationships
    user = relationship("User", back_populates="merchant")
    menus = relationship("Menu", back_populates="merchant", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Merchant(id={self.id}, shop_name={self.shop_name})>"
