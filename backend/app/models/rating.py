"""
Rating and interaction models
Core data for collaborative filtering
"""
from sqlalchemy import Column, String, Float, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from app.db.session import Base
import uuid


class Rating(Base, BaseModel):
    """
    Customer ratings on menu items
    Core data source for collaborative filtering
    """
    __tablename__ = "ratings"

    id = Column(String(50), primary_key=True, default=lambda: f"r_{uuid.uuid4().hex[:12]}")  # Auto-generate ID
    customer_id = Column(String(50), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    menu_id = Column(String(50), ForeignKey("menus.id", ondelete="CASCADE"), nullable=False, index=True)

    # Rating score (1-5)
    score = Column(Float, nullable=False, index=True)

    # Optional review text
    review_text = Column(String, nullable=True)

    # Verified purchase flag
    is_verified_purchase = Column(Boolean, default=True)

    # Unique constraint: one rating per customer per menu
    __table_args__ = (
        UniqueConstraint('customer_id', 'menu_id', name='unique_customer_menu_rating'),
    )

    # Relationships
    customer = relationship("Customer", back_populates="ratings")
    menu = relationship("Menu", back_populates="ratings")

    def __repr__(self):
        return f"<Rating(id={self.id}, customer_id={self.customer_id}, menu_id={self.menu_id}, score={self.score})>"
