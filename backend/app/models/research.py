"""
Research and evaluation models
Models for algorithm transparency and research metrics
"""
from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from app.db.session import Base


class UserSimilarityMatrix(Base, BaseModel):
    """
    Pre-computed user similarity matrix
    Stores Pearson correlation or cosine similarity between users
    """
    __tablename__ = "user_similarity_matrix"

    id = Column(String(50), primary_key=True)  # TEXT for SQLite compatibility

    user_id_1 = Column(String(50), nullable=False, index=True)
    user_id_2 = Column(String(50), nullable=False, index=True)

    # Similarity score (-1 to 1 for Pearson, 0 to 1 for Cosine)
    similarity_score = Column(Float, nullable=False, index=True)

    # Method used: 'pearson', 'cosine'
    similarity_method = Column(String(20), default="pearson")

    # Number of items both users rated
    common_items_rated = Column(Integer, default=0)

    # Unique constraint with ordering (user_id_1 < user_id_2)
    __table_args__ = (
        UniqueConstraint('user_id_1', 'user_id_2', name='unique_user_pair'),
    )

    def __repr__(self):
        return f"<UserSimilarityMatrix(user1={self.user_id_1}, user2={self.user_id_2}, score={self.similarity_score})>"


class RecommendationLog(Base, BaseModel):
    """
    Log of all recommendations made to customers
    Core data for research analysis and algorithm evaluation
    """
    __tablename__ = "recommendation_logs"

    id = Column(String(50), primary_key=True)  # TEXT for SQLite compatibility

    customer_id = Column(String(50), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    menu_id = Column(String(50), ForeignKey("menus.id", ondelete="CASCADE"), nullable=False)

    # Algorithm scores
    fuzzy_score = Column(Float, nullable=False)  # Sf(u,i): Preference match score
    cf_score = Column(Float, nullable=True)  # Pcf(u,i)/Rmax: Collaborative filtering score (normalized)

    # Final hybrid score
    hybrid_final_score = Column(Float, nullable=False, index=True)  # Hscore(u,i)

    # Alpha weight used in calculation
    alpha_weight = Column(Float, nullable=False)

    # Ranking position
    rank_position = Column(Integer, nullable=False)

    # Algorithm version tracking
    algorithm_version = Column(String(20), default="hybrid_v1")

    # Relationships
    customer = relationship("Customer", back_populates="recommendation_logs")
    menu = relationship("Menu", back_populates="recommendation_logs")

    def __repr__(self):
        return f"<RecommendationLog(id={self.id}, customer={self.customer_id}, menu={self.menu_id}, score={self.hybrid_final_score})>"


class AlgorithmEvaluation(Base, BaseModel):
    """
    Algorithm performance evaluation metrics
    Stores results of cross-validation and testing
    """
    __tablename__ = "algorithm_evaluation"

    id = Column(String(50), primary_key=True)  # TEXT for SQLite compatibility

    test_date = Column(DateTime, nullable=False, index=True)

    # Method variant identifier
    method_variant = Column(String(50), nullable=False, index=True)  # 'hybrid_alpha_0.5', 'fuzzy_only', etc.

    # Alpha weight used (for hybrid methods)
    alpha_weight = Column(Float, nullable=True)

    # Error metrics
    mae_score = Column(Float, nullable=False)  # Mean Absolute Error
    rmse_score = Column(Float, nullable=False)  # Root Mean Square Error

    # Classification metrics
    hit_rate = Column(Float, nullable=True)  # Percentage of successful recommendations
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)

    # Coverage metric
    coverage = Column(Float, nullable=True)  # Percentage of items recommended

    # Data info
    total_data_points = Column(Integer, nullable=False)

    # Performance metrics
    training_time_ms = Column(Integer, nullable=True)  # Algorithm execution time in milliseconds

    # Test configuration
    test_split = Column(String(20), nullable=True)  # '80-20', '70-30', etc.

    def __repr__(self):
        return f"<AlgorithmEvaluation(id={self.id}, variant={self.method_variant}, mae={self.mae_score}, rmse={self.rmse_score})>"
