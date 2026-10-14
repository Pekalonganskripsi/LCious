"""
Algorithm parameters model
For storing configurable algorithm parameters like alpha, k_neighbors, etc.
"""
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime
from app.db.base import BaseModel
from app.db.session import Base
import uuid
from datetime import datetime


class AlgorithmParameters(Base, BaseModel):
    """
    Algorithm parameters that can be configured by admin
    These parameters control the behavior of the recommendation system
    """
    __tablename__ = "algorithm_parameters"

    id = Column(String(50), primary_key=True, default=lambda: f"ap_{uuid.uuid4().hex[:12]}")

    # Parameter name: 'default_alpha', 'k_neighbors', 'max_distance', etc.
    parameter_name = Column(String(100), nullable=False, unique=True, index=True)

    # Parameter value (can be float, int, or boolean)
    parameter_value = Column(Float, nullable=False)

    # Optional: parameter description
    parameter_description = Column(String(500), nullable=True)

    # Optional: data type for validation
    parameter_type = Column(String(20), nullable=False, default='float')  # 'float', 'int', 'bool'

    # When this parameter was last updated
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Who updated this parameter (optional)
    updated_by = Column(String(50), nullable=True)
