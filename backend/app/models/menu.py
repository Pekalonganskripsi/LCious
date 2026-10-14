"""
Menu and content models
"""
from sqlalchemy import Column, String, DateTime, Integer, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from app.db.session import Base
import enum
import uuid


class MenuCategory(str, enum.Enum):
    """Menu categories"""
    FOOD = "food"
    DRINK = "drink"
    DESSERT = "dessert"
    SNACK = "snack"


class Menu(Base, BaseModel):
    """
    Menu items offered by merchants
    Core content for recommendations
    """
    __tablename__ = "menus"

    id = Column(String(50), primary_key=True, default=lambda: f"menu_{uuid.uuid4().hex[:12]}")  # Auto-generate ID
    merchant_id = Column(String(50), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)

    item_name = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False, index=True)

    category = Column(String(20), nullable=False, default=MenuCategory.FOOD, index=True)

    image_url = Column(String, nullable=True)
    is_available = Column(Boolean, default=True, index=True)

    # Taste levels (0-5) for fuzzy matching
    spice_level = Column(Integer, nullable=True, default=0)
    sweetness_level = Column(Integer, nullable=True, default=0)
    savory_level = Column(Integer, nullable=True, default=0)

    # Popularity metrics
    popularity_score = Column(Integer, default=0)

    # Rating aggregations
    total_ratings = Column(Integer, default=0)
    average_rating = Column(Float, nullable=True)

    # Tags for filtering (stored as comma-separated string for SQLite)
    tags = Column(String, nullable=True)

    # Relationships
    merchant = relationship("Merchant", back_populates="menus")
    ratings = relationship("Rating", back_populates="menu", cascade="all, delete-orphan")
    recommendation_logs = relationship("RecommendationLog", back_populates="menu", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Menu(id={self.id}, item_name={self.item_name}, price={self.price})>"
