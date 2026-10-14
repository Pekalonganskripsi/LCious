"""
Evaluation Results Model

Stores cached evaluation results for instant retrieval
"""
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.session import Base


class EvaluationResults(Base):
    """
    Cached evaluation results untuk admin dashboard

    Menyimpan hasil evaluasi lengkap:
    - Cross-validation metrics (MAE, RMSE, Precision, Recall, NDCG)
    - Alpha optimization results
    - Algorithm comparison
    - Statistical tests
    - Baseline comparisons
    - Per-user analysis
    - Temporal trends
    """
    __tablename__ = "evaluation_results"

    id = Column(String, primary_key=True, index=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    total_ratings = Column(Integer, nullable=False)
    total_customers = Column(Integer, nullable=False)
    total_menus = Column(Integer, nullable=False)

    # Cross-Validation Results (JSON for flexibility)
    cv_results = Column(JSON, nullable=True)
    # Format: {"alpha_0.0": {"alpha": 0.0, "mae": 0.44, "rmse": 0.56, ...}, ...}

    # Best Alpha
    best_alpha = Column(JSON, nullable=True)
    # Format: {"value": "alpha_0.0", "mae": 0.44, "rmse": 0.56, "hit_rate": 0.65}

    # Alpha Optimization Chart Data
    alpha_optimization_chart = Column(JSON, nullable=True)
    # Format: [{"alpha": 0.0, "mae": 0.44, "rmse": 0.56}, ...]

    # Data Sparsity Analysis
    data_sparsity = Column(JSON, nullable=True)
    # Format: {"total_users": 5, "total_menus": 14, "sparsity_percentage": 72.9, ...}

    # Algorithm Comparison
    algorithm_comparison = Column(JSON, nullable=True)
    # Format: {"winner": "Hybrid", "comparison": {...}, "interpretation": "..."}

    # Statistical Test Results
    statistical_test = Column(JSON, nullable=True)
    # Format: {"is_significant": true, "p_value": 0.02, "t_statistic": 2.3, ...}

    # Baseline Comparison
    baseline_comparison = Column(JSON, nullable=True)
    # Format: {"winner": "Hybrid", "comparison": {...}, "winner_mae": 0.44}

    # Per-User Analysis
    per_user_analysis = Column(JSON, nullable=True)
    # Format: {"user_segments": {...}, "worst_predictions": [...], "best_predictions": [...]}

    # Temporal Analysis
    temporal_analysis = Column(JSON, nullable=True)
    # Format: {"trend": "improving", "improvement_percentage": 5.2, "daily_metrics": [...]}

    # Export Data (for Excel download)
    export_data = Column(JSON, nullable=True)
    # Format: {"timestamp": "...", "cv_results": {...}, "comparison": {...}, ...}

    # Status
    is_complete = Column(Boolean, default=False)
    evaluation_status = Column(String, default="pending")  # pending, running, completed, failed
    error_message = Column(String, nullable=True)

    # Performance metrics
    evaluation_duration_seconds = Column(Float, nullable=True)

    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "total_ratings": self.total_ratings,
            "total_customers": self.total_customers,
            "total_menus": self.total_menus,
            "cv_results": self.cv_results,
            "best_alpha": self.best_alpha,
            "alpha_optimization_chart": self.alpha_optimization_chart,
            "data_sparsity": self.data_sparsity,
            "algorithm_comparison": self.algorithm_comparison,
            "statistical_test": self.statistical_test,
            "baseline_comparison": self.baseline_comparison,
            "per_user_analysis": self.per_user_analysis,
            "temporal_analysis": self.temporal_analysis,
            "export_data": self.export_data,
            "is_complete": self.is_complete,
            "evaluation_status": self.evaluation_status,
            "error_message": self.error_message,
            "evaluation_duration_seconds": self.evaluation_duration_seconds,
        }