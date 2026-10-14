"""
Fuzzy logic related models
"""
from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from app.db.session import Base
import uuid


class FuzzyCriteria(Base, BaseModel):
    """
    Fuzzy criteria definitions
    Managed by superadmin for algorithm tuning
    """
    __tablename__ = "fuzzy_criteria"

    id = Column(String(50), primary_key=True, default=lambda: f"fc_{uuid.uuid4().hex[:12]}")  # Auto-generate ID

    # Criteria: 'price', 'distance', 'popularity'
    criteria_name = Column(String(50), nullable=False, index=True)

    # Sub-criteria: 'cheap', 'medium', 'expensive' for price
    sub_criteria = Column(String(50), nullable=False)

    # Triangular membership function parameters
    min_val = Column(Float, nullable=False)
    mid_val = Column(Float, nullable=True)  # Peak of triangle
    max_val = Column(Float, nullable=False)

    # Type of membership function
    membership_function = Column(String(20), default="triangular")  # 'triangular', 'trapezoidal'

    def __repr__(self):
        return f"<FuzzyCriteria(id={self.id}, criteria={self.criteria_name}, sub={self.sub_criteria})>"


class CustomerPreference(Base, BaseModel):
    """
    Customer preference profile
    Fuzzy inputs for personalized recommendations
    """
    __tablename__ = "customer_preferences"

    id = Column(String(50), primary_key=True, default=lambda: f"cp_{uuid.uuid4().hex[:12]}")  # Auto-generate ID
    customer_id = Column(String(50), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Importance weights (0-1)
    pref_price_importance = Column(Float, nullable=True)
    pref_distance_importance = Column(Float, nullable=True)
    pref_popularity_importance = Column(Float, nullable=True)

    # Price sensitivity
    pref_price_sensitivity = Column(String(20), nullable=True)  # 'cheap', 'medium', 'expensive_flexible'

    # Distance preference
    pref_max_distance_km = Column(Integer, default=10)

    # Taste preferences (0-5)
    pref_spice_level = Column(Integer, nullable=True)
    pref_sweetness_level = Column(Integer, nullable=True)
    pref_savory_level = Column(Integer, nullable=True)

    # Cuisine preferences (stored as comma-separated string for SQLite)
    pref_cuisines = Column(String, nullable=True)

    # Dietary restrictions (stored as comma-separated string for SQLite)
    pref_dietary_restrictions = Column(String, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="preferences")

    def __repr__(self):
        return f"<CustomerPreference(id={self.id}, customer_id={self.customer_id})>"
