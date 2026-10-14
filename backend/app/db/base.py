"""
Base database model with common fields
"""
from datetime import datetime
from sqlalchemy import Column, DateTime


class BaseModel:
    """
    Base model with common fields
    All models should inherit from this instead of Base
    """
    __abstract__ = True

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
