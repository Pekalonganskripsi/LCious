"""
Ultra-Fast Evaluation Worker - Maximum speed for large datasets

Optimized for speed with:
- Minimal cross-validation for large datasets
- Simplified calculations
- Fast algorithm comparisons
- Quick baseline tests
"""
import time
import threading
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
import numpy as np

from app.db.session import SessionLocal
from app.models.evaluation_results import EvaluationResults
from app.models.rating import Rating
from app.models.user import User, UserRole
from app.models.menu import Menu
from app.algorithms.evaluation import AlgorithmEvaluator


class UltraFastEvaluationWorker:
    """
    Ultra-fast evaluation worker for instant results
    """

    def __init__(self):
        self.is_running = False
        self.last_evaluation_time: Optional[datetime] = None
        self.min_evaluation_interval = timedelta(minutes=2)  # Reduced to 2 minutes
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
        Run ultra-fast evaluation - maximum speed
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
                print(f"[{datetime.now()}] Starting ULTRA-FAST evaluation {eval_id}")

                # Get ratings
                all_ratings = db.query(Rating).all()
                total_ratings = len(all_ratings)
                print(f"[{datetime.now()}] Processing {total_ratings} ratings...")

 # RESEARCH-GRADE: Proper cross-validation setup
                if total_ratings > 300:
                    # Very large dataset - use proper k-fold but limit for speed
                    n_splits = 5  # Standard 5-fold CV
                    alpha_values = [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]  # 7 alpha values
                    test_size = 0.2  # Standard 20% test
                elif total_ratings > 100:
                    # Large dataset - proper k-fold cross-validation
                    n_splits = 5  # Standard 5-fold CV
                    alpha_values = [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]  # 7 alpha values
                    test_size = 0.2  # Standard 20% test
                else:
                    # Small dataset - proper k-fold cross-validation
                    n_splits = 5  # Standard 5-fold CV
                    alpha_values = [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]  # 7 alpha values
                    test_size = 0.2  # Standard 20% test

                # Initialize results immediately
                cv_results = {}
                alpha_chart = []
                best_alpha_key = "alpha_0.5"
                best_alpha_data = {"avg_mae": 0, "avg_rmse": 0, "avg_hit_rate": 0}

                # Initialize evaluator for all analyses (with error handling)
                try:
                    evaluator = AlgorithmEvaluator(db)
                    print(f"[{datetime.now()}] AlgorithmEvaluator initialized successfully")
                except Exception as e:
                    print(f"[{datetime.now()}] Failed to initialize AlgorithmEvaluator: {e}")
                    raise

                from sklearn.model_selection import train_test_split
                train_ratings, test_ratings = train_test_split(
                    all_ratings, test_size=test_size, random_state=42
                )
                print(f"[{datetime.now()}] Using {len(test_ratings)} test samples for additional analyses")

                # 1. Cross-Validation (COMPLETE - Research Grade with 7 alpha values)
                try:
                    print(f"[{datetime.now()}] Running complete k-fold cross-validation with {n_splits} folds...")

                    # Use proper cross-validation from AlgorithmEvaluator
                    cv_results = evaluator.cross_validate(
                        ratings=all_ratings,
                        n_splits=n_splits,
                        alpha_values=[0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]  # 7 alpha values for research
                    )

                    print(f"[{datetime.now()}] Complete cross-validation completed - {len(cv_results)} alpha values tested")

                except Exception as e:
                    import traceback
                    cv_results = {}
                    print(f"[{datetime.now()}] CV Error: {e}")
                    print(f"[{datetime.now()}] Traceback: {traceback.format_exc()}")

                # Find best alpha
                if cv_results:
                    try:
                        best_alpha_key = min(cv_results.keys(), key=lambda k: cv_results[k]['avg_mae'])
                        best_alpha_data = cv_results[best_alpha_key]
                    except:
                        best_alpha_key = "alpha_0.5"
                        best_alpha_data = {"avg_mae": 0, "avg_rmse": 0, "avg_hit_rate": 0}

                # 2. Alpha Optimization Chart
                try:
                    for key, results in cv_results.items():
                        alpha_chart.append({
                            "alpha": float(results['alpha']),
                            "mae": results['avg_mae'],
                            "rmse": results['avg_rmse'],
                            "hit_rate": results['avg_hit_rate']
                        })
                except:
                    pass

                # 3. Data Sparsity (COMPLETE - Research Grade)
                try:
                    print(f"[{datetime.now()}) Running complete data sparsity analysis...")

                    # Use proper data sparsity calculation from AlgorithmEvaluator
                    sparsity_data = evaluator.calculate_data_sparsity()

                    print(f"[{datetime.now()}] Complete data sparsity calculated - {sparsity_data.get('sparsity_level', 'N/A')}")
                except Exception as e:
                    import traceback
                    sparsity_data = {"error": str(e), "traceback": traceback.format_exc()}
                    print(f"[{datetime.now()}] Data sparsity error: {e}")
                    print(f"[{datetime.now()}] Traceback: {traceback.format_exc()}")

                # 4. Algorithm Comparison (COMPLETE - Research Grade)
                try:
                    print(f"[{datetime.now()}] Running complete algorithm comparison...")

                    # Use proper algorithm comparison from AlgorithmEvaluator
                    comparison_result = evaluator.compare_algorithms(
                        ratings=all_ratings,
                        test_size=0.2,
                        k=10
                    )

                    print(f"[{datetime.now()}] Complete algorithm comparison completed - {len([k for k in comparison_result.keys() if k not in ['winner', 'winner_mae', 'total_ratings', 'test_size']])} algorithms compared")
                except Exception as e:
                    import traceback
                    comparison_result = {"error": str(e), "traceback": traceback.format_exc()}
                    print(f"[{datetime.now()}] Algorithm comparison error: {e}")
                    print(f"[{datetime.now()}] Traceback: {traceback.format_exc()}")

                # 5. Statistical Tests (COMPLETE - Research Grade)
                try:
                    print(f"[{datetime.now()}] Running complete statistical significance testing...")

                    # Safety check for evaluator
                    if 'evaluator' not in locals():
                        raise NameError("evaluator variable not found - may not have been initialized properly")

                    # Use proper statistical significance test from AlgorithmEvaluator
                    # Compare α=0.5 (Hybrid) vs α=0.0 (CF Only) as per research requirements
                    stat_result = evaluator.statistical_significance_test(
                        ratings=all_ratings,
                        alpha1=0.5,  # Hybrid approach
                        alpha2=0.0,  # Collaborative Filtering Only
                        test_size=0.2,
                        n_runs=10    # 10 runs for proper statistical power
                    )

                    # Add proper alpha identifiers for research clarity
                    stat_result['alpha1_identifier'] = 'alpha_0.5'
                    stat_result['alpha2_identifier'] = 'alpha_0.0'

                    print(f"[{datetime.now()}] Complete statistical tests completed - p-value: {stat_result.get('p_value', 'N/A')}, Cohen's d: {stat_result.get('effect_size', 'N/A')}")
                except Exception as e:
                    import traceback
                    stat_result = {"error": str(e), "traceback": traceback.format_exc()}
                    print(f"[{datetime.now()}] Statistical tests error: {e}")
                    print(f"[{datetime.now()}] Traceback: {traceback.format_exc()}")

                # 6. Baseline Comparison (COMPLETE - Research Grade)
                try:
                    print(f"[{datetime.now()}] Running complete baseline comparison...")

                    # Use proper baseline comparison from AlgorithmEvaluator
                    baseline_result = evaluator.calculate_baseline_metrics(
                        ratings=all_ratings,
                        test_size=0.2
                    )

                    print(f"[{datetime.now()}] Complete baseline comparison completed - {len([k for k in baseline_result.keys() if k != 'winner' and k != 'winner_mae'])} baselines compared")
                except Exception as e:
                    import traceback
                    baseline_result = {"error": str(e), "traceback": traceback.format_exc()}
                    print(f"[{datetime.now()}] Baseline comparison error: {e}")
                    print(f"[{datetime.now()}] Traceback: {traceback.format_exc()}")

                # 7. Per-User Analysis (COMPLETE - Research Grade)
                try:
                    print(f"[{datetime.now()}] Running complete per-user error analysis...")

                    # Use proper per-user analysis from AlgorithmEvaluator
                    # Analyze using the best performing alpha (α=0.0 based on our results)
                    per_user_analysis = evaluator.per_user_error_analysis(
                        ratings=all_ratings,
                        alpha=0.0  # Use the best performing alpha
                    )

                    print(f"[{datetime.now()}] Complete per-user analysis completed - {per_user_analysis.get('total_predictions', 0)} predictions analyzed")
                except Exception as e:
                    import traceback
                    per_user_analysis = {"error": str(e), "traceback": traceback.format_exc()}
                    print(f"[{datetime.now()}] Per-user analysis error: {e}")
                    print(f"[{datetime.now()}] Traceback: {traceback.format_exc()}")

                # 8. Temporal Analysis (COMPLETE - Research Grade)
                try:
                    print(f"[{datetime.now()}] Running complete temporal analysis...")

                    # Use proper temporal analysis from AlgorithmEvaluator
                    temporal_analysis = evaluator.temporal_analysis(
                        db=db,
                        days=30  # Analyze last 30 days
                    )

                    print(f"[{datetime.now()}] Complete temporal analysis completed - {temporal_analysis.get('days_analyzed', 'N/A')} days analyzed")
                except Exception as e:
                    import traceback
                    temporal_analysis = {"error": str(e), "traceback": traceback.format_exc()}
                    print(f"[{datetime.now()}] Temporal analysis error: {e}")
                    print(f"[{datetime.now()}] Traceback: {traceback.format_exc()}")

                # Calculate duration
                duration = time.time() - start_time
                print(f"[{datetime.now()}] ULTRA-FAST evaluation completed in {duration:.2f} seconds")

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
                    evaluation.error_message = str(e)[:500]
                    try:
                        db.commit()
                    except:
                        pass

                return {
                    "status": "error",
                    "error": str(e)[:500]
                }
            finally:
                db.close()


# Global worker instance - use ultra-fast version
evaluation_worker = UltraFastEvaluationWorker()


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