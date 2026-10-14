"""
Fast Evaluation Worker - Optimized for speed and reliability

Runs comprehensive evaluations quickly with:
- Reduced cross-validation folds for large datasets
- Optimized alpha value testing
- Faster baseline comparisons
- Better error handling and progress tracking
"""
import time
import threading
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
import random

from app.db.session import SessionLocal
from app.models.evaluation_results import EvaluationResults
from app.models.rating import Rating
from app.models.user import User, UserRole
from app.models.menu import Menu
from app.algorithms.evaluation import AlgorithmEvaluator


class FastEvaluationWorker:
    """
    Optimized evaluation worker for fast, reliable results
    """

    def __init__(self):
        self.is_running = False
        self.last_evaluation_time: Optional[datetime] = None
        self.min_evaluation_interval = timedelta(minutes=5)
        self.evaluation_lock = threading.Lock()

    def should_run_evaluation(self, db: Session) -> bool:
        """Check if evaluation should run"""
        # Check if evaluation is currently running
        running_eval = db.query(EvaluationResults).filter(
            EvaluationResults.evaluation_status == "running"
        ).first()

        if running_eval:
            return False

        # Check minimum interval
        if self.last_evaluation_time:
            time_since_last = datetime.now() - self.last_evaluation_time
            if time_since_last < self.min_evaluation_interval:
                return False

        # Check if we have enough data
        total_ratings = db.query(Rating).count()
        if total_ratings < 10:
            return False

        return True

    def run_evaluation(self, trigger: str = "manual") -> dict:
        """
        Run fast evaluation - optimized for speed
        """
        with self.evaluation_lock:
            db = SessionLocal()
            try:
                if not self.should_run_evaluation(db):
                    return {"status": "skipped", "reason": "Conditions not met"}

                # Create evaluation record
                eval_id = f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{trigger}"
                evaluation = EvaluationResults(
                    id=eval_id,
                    evaluation_status="running",
                    total_ratings=db.query(Rating).count(),
                    total_customers=db.query(User).filter(User.role == UserRole.CUSTOMER).count(),
                    total_menus=db.query(Menu).count()
                )
                db.add(evaluation)
                db.commit()

                start_time = time.time()
                print(f"[{datetime.now()}] Starting FAST evaluation {eval_id}")

                # Get ratings
                all_ratings = db.query(Rating).all()
                total_ratings = len(all_ratings)
                print(f"[{datetime.now()}] Processing {total_ratings} ratings...")

                # OPTIMIZED: Adjust complexity based on dataset size
                if total_ratings > 200:
                    # Large dataset - minimal testing
                    n_splits = 2
                    alpha_values = [0.0, 0.5, 1.0]
                    test_size = 0.4
                elif total_ratings > 100:
                    # Medium dataset - balanced testing
                    n_splits = 3
                    alpha_values = [0.0, 0.3, 0.5, 0.7, 1.0]
                    test_size = 0.3
                else:
                    # Small dataset - comprehensive testing
                    n_splits = 5
                    alpha_values = [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]
                    test_size = 0.2

                # 1. Cross-Validation Results (OPTIMIZED)
                try:
                    evaluator = AlgorithmEvaluator(db)
                    cv_results = evaluator.cross_validate(
                        ratings=all_ratings,
                        n_splits=n_splits,
                        alpha_values=alpha_values
                    )
                    print(f"[{datetime.now()}] Cross-validation completed")
                except Exception as e:
                    print(f"[{datetime.now()}] CV Error: {e}")
                    cv_results = {"error": str(e)}

                # Find best alpha
                if cv_results and not isinstance(cv_results, dict):
                    cv_results = {}
                if cv_results and not cv_results.get("error"):
                    try:
                        best_alpha_key = min(cv_results.keys(), key=lambda k: cv_results[k]['avg_mae'])
                        best_alpha_data = cv_results[best_alpha_key]
                    except:
                        best_alpha_key = "alpha_0.5"
                        best_alpha_data = {"avg_mae": 0, "avg_rmse": 0, "avg_hit_rate": 0}
                else:
                    best_alpha_key = "alpha_0.5"
                    best_alpha_data = {"avg_mae": 0, "avg_rmse": 0, "avg_hit_rate": 0}

                # 2. Alpha Optimization Chart
                alpha_chart = []
                try:
                    for key, results in cv_results.items():
                        if not isinstance(results, dict) or "avg_mae" not in results:
                            continue
                        alpha_chart.append({
                            "alpha": float(key.split('_')[1]),
                            "mae": results['avg_mae'],
                            "rmse": results['avg_rmse'],
                            "hit_rate": results['avg_hit_rate']
                        })
                except Exception as e:
                    print(f"[{datetime.now()}] Alpha chart error: {e}")

                # 3. Data Sparsity
                try:
                    sparsity_data = evaluator.calculate_data_sparsity()
                    print(f"[{datetime.now()}] Data sparsity completed")
                except Exception as e:
                    sparsity_data = {"error": str(e)}
                    print(f"[{datetime.now()}] Sparsity error: {e}")

                # 4. Algorithm Comparison (OPTIMIZED)
                try:
                    comparison_result = evaluator.compare_algorithms(
                        ratings=all_ratings,
                        test_size=test_size,
                        k=10
                    )
                    print(f"[{datetime.now()}] Algorithm comparison completed")
                except Exception as e:
                    comparison_result = {"error": str(e)}
                    print(f"[{datetime.now()}] Algorithm comparison error: {e}")

                # 5. Statistical Tests (OPTIMIZED)
                try:
                    from app.algorithms.evaluation import StatisticalTests
                    stats_tests = StatisticalTests(db)

                    if cv_results and len(cv_results) >= 2:
                        best_alpha_key = min(cv_results.keys(), key=lambda k: cv_results[k]['avg_mae'])
                        worst_alpha_key = max(cv_results.keys(), key=lambda k: cv_results[k]['avg_mae'])

                        stat_result = stats_tests.pairwise_comparison(
                            mae1=cv_results[best_alpha_key]['avg_mae'],
                            mae2=cv_results[worst_alpha_key]['avg_mae'],
                            n=min(total_ratings, 30)  # OPTIMIZED: smaller sample
                        )
                        stat_result['alpha1'] = best_alpha_key
                        stat_result['alpha2'] = worst_alpha_key
                        print(f"[{datetime.now()}] Statistical tests completed")
                    else:
                        stat_result = {"error": "Insufficient data for statistical tests"}
                except Exception as e:
                    stat_result = {"error": str(e)}
                    print(f"[{datetime.now()}] Statistical tests error: {e}")

                # 6. Baseline Comparison (OPTIMIZED)
                try:
                    baseline_result = evaluator.compare_with_baselines(
                        ratings=all_ratings,
                        test_size=test_size,
                        k=10
                    )
                    print(f"[{datetime.now()}] Baseline comparison completed")
                except Exception as e:
                    baseline_result = {"error": str(e)}
                    print(f"[{datetime.now()}] Baseline comparison error: {e}")

                # 7. Per-User Analysis (SIMPLIFIED)
                try:
                    per_user_result = evaluator.per_user_error_analysis(
                        ratings=all_ratings,
                        alpha=0.5
                    )

                    # Simplified per-user analysis
                    detailed_predictions = {
                        'user_segments': per_user_result.get('user_segments', {}),
                        'total_analyzed': per_user_result.get('total_predictions', 0),
                        'overall_mae': per_user_result.get('overall_mae', 0),
                        'worst_predictions': per_user_result.get('worst_predictions', [])[:5],  # Limit to 5
                        'best_predictions': per_user_result.get('best_predictions', [])[:5]     # Limit to 5
                    }

                    per_user_analysis = detailed_predictions
                    print(f"[{datetime.now()}] Per-user analysis completed")
                except Exception as e:
                    per_user_analysis = {"error": str(e)}
                    print(f"[{datetime.now()}] Per-user analysis error: {e}")

                # 8. Temporal Analysis (SIMPLIFIED)
                try:
                    temporal_analysis = self._analyze_temporal_trends(db)
                    print(f"[{datetime.now()}] Temporal analysis completed")
                except Exception as e:
                    temporal_analysis = {"error": str(e)}
                    print(f"[{datetime.now()}] Temporal analysis error: {e}")

                # Calculate duration
                duration = time.time() - start_time
                print(f"[{datetime.now()}] Evaluation completed in {duration:.2f} seconds")

                # Update evaluation record
                evaluation.cv_results = cv_results
                evaluation.best_alpha = {
                    "value": best_alpha_key,
                    "mae": best_alpha_data['avg_mae'],
                    "rmse": best_alpha_data['avg_rmse'],
                    "hit_rate": best_alpha_data['avg_hit_rate']
                }
                evaluation.alpha_optimization_chart = alpha_chart
                evaluation.data_sparsity = sparsity_data
                evaluation.algorithm_comparison = comparison_result
                evaluation.statistical_test = stat_result
                evaluation.baseline_comparison = baseline_result
                evaluation.per_user_analysis = per_user_analysis
                evaluation.temporal_analysis = temporal_analysis

                # Prepare export data
                evaluation.export_data = {
                    "timestamp": datetime.now().isoformat(),
                    "trigger": trigger,
                    "cv_results": cv_results,
                    "best_alpha": evaluation.best_alpha,
                    "data_sparsity": sparsity_data,
                    "comparison": comparison_result,
                    "statistical_test": stat_result,
                    "baseline": baseline_result,
                    "per_user": per_user_analysis,
                    "temporal": temporal_analysis
                }

                evaluation.evaluation_status = "completed"
                evaluation.is_complete = True
                evaluation.evaluation_duration_seconds = duration

                db.commit()

                self.last_evaluation_time = datetime.now()

                return {
                    "status": "success",
                    "evaluation_id": eval_id,
                    "duration_seconds": duration,
                    "trigger": trigger,
                    "best_alpha": best_alpha_key
                }

            except Exception as e:
                db.rollback()
                print(f"[{datetime.now()}] Evaluation failed: {str(e)}")

                # Update evaluation with error
                if 'evaluation' in locals():
                    evaluation.evaluation_status = "failed"
                    evaluation.error_message = str(e)[:500]  # Limit error message length
                    try:
                        db.commit()
                    except:
                        pass

                return {
                    "status": "error",
                    "error": str(e)[:500]  # Limit error message length
                }
            finally:
                db.close()

    def _analyze_temporal_trends(self, db):
        """Analyze temporal trends in ratings (simplified)"""
        try:
            from sqlalchemy import extract, func
            from datetime import datetime, timedelta

            # Get ratings from last 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            ratings = db.query(Rating).filter(
                Rating.created_at >= cutoff_date
            ).order_by(Rating.created_at).all()

            if len(ratings) == 0:
                return {
                    "trend": "insufficient_data",
                    "improvement_percentage": 0,
                    "daily_metrics": []
                }

            # Group by date - simplified
            from collections import defaultdict
            daily_ratings = defaultdict(list)
            for r in ratings:
                date_key = r.created_at.strftime('%Y-%m-%d')
                daily_ratings[date_key].append(r.score)

            # Calculate metrics per day - simplified
            daily_metrics = []
            for date_str in sorted(daily_ratings.keys()):
                scores = daily_ratings[date_str]
                daily_metrics.append({
                    "date": date_str,
                    "total_ratings": len(scores),
                    "avg_rating": float(sum(scores) / len(scores))
                })

            # Calculate trend - simplified
            if len(daily_metrics) >= 2:
                first_avg = daily_metrics[0]['avg_rating']
                last_avg = daily_metrics[-1]['avg_rating']
                improvement = ((last_avg - first_avg) / first_avg) * 100 if first_avg > 0 else 0

                if improvement > 5:
                    trend = "improving"
                elif improvement < -5:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                improvement = 0
                trend = "insufficient_data"

            return {
                "days_analyzed": 30,
                "total_ratings": len(ratings),
                "daily_metrics": daily_metrics,
                "trend": trend,
                "improvement_percentage": float(improvement),
                "first_period_avg": daily_metrics[0]['avg_rating'] if daily_metrics else 0,
                "second_period_avg": daily_metrics[-1]['avg_rating'] if len(daily_metrics) > 1 else 0
            }
        except Exception as e:
            return {"error": str(e)}


# Global worker instance - use the fast version
evaluation_worker = FastEvaluationWorker()


def run_scheduled_evaluation():
    """Run scheduled evaluation (called by cron job)"""
    print(f"[{datetime.now()}] Running scheduled evaluation...")
    result = evaluation_worker.run_evaluation(trigger="scheduled")
    print(f"[{datetime.now()}] Scheduled evaluation completed: {result}")


def run_event_driven_evaluation():
    """Run evaluation triggered by new data (called by webhook/signal)"""
    print(f"[{datetime.now()}] Running event-driven evaluation...")
    result = evaluation_worker.run_evaluation(trigger="new_data")
    print(f"[{datetime.now()}] Event-driven evaluation completed: {result}")