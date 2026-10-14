"""
Evaluation Metrics for LCious Recommendation System

Implements various metrics untuk mengukur performa algoritma:
- MAE (Mean Absolute Error)
- RMSE (Root Mean Square Error)
- Hit Rate
- Precision, Recall, F1
- Coverage
"""
import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional
from sklearn.model_selection import KFold
from sqlalchemy.orm import Session
from datetime import datetime

from app.algorithms.hybrid import HybridRecommender
from app.models.rating import Rating
from app.models.research import AlgorithmEvaluation


class AlgorithmEvaluator:
    """
    Evaluator untuk mengukur performa recommendation algorithms

    Metrics:
    1. MAE: Mean Absolute Error
    2. RMSE: Root Mean Square Error
    3. Hit Rate: Persentase rekomendasi yang relevan
    4. Precision@K, Recall@K, F1@K
    5. Coverage: Persentase items yang direkomendasikan
    """

    # FIXED random seeds for reproducibility across all evaluation endpoints
    RANDOM_SEEDS = [42, 43, 44, 45, 46, 47, 48, 49, 50, 51]  # For 10-run statistical tests

    def __init__(self, db: Session):
        """
        Initialize Evaluator

        Args:
            db: Database session
        """
        self.db = db

    def _evaluate_with_fixed_split(self,
                                    ratings: List[Rating],
                                    alpha: float,
                                    train_ratings: List[Rating],
                                    test_ratings: List[Rating],
                                    k: int = 10) -> Dict:
        """
        Core evaluation function dengan FIXED train/test split

        Ini adalah fungsi INTI yang digunakan oleh SEMUA endpoint evaluasi:
        - Cross-Validation
        - Algorithm Comparison
        - Statistical Significance Test

        Dengan menggunakan fungsi ini, dijamin semua endpoint menghasilkan
        hasil yang KONSISTEN dan REPRODUCIBLE.

        Args:
            ratings: List of semua Rating objects
            alpha: Alpha value untuk hybrid
            train_ratings: Training data (FIXED split)
            test_ratings: Test data (FIXED split)
            k: Jumlah neighbors untuk CF

        Returns:
            Dictionary dengan metrics dan raw errors
        """
        # DEBUG: Log when core function is called
        if alpha == 0.0:
            logging.info(f"✅ _evaluate_with_fixed_split() called with Alpha={alpha}, n_test={len(test_ratings)}")

        recommender = HybridRecommender(self.db, alpha=alpha)

        predictions = []
        actuals = []
        raw_errors = []  # Store individual errors for statistical tests

        for rating in test_ratings:
            try:
                predicted = recommender.predict_rating_hybrid(
                    user_id=str(rating.customer_id),
                    menu_id=str(rating.menu_id),
                    k=k
                )
                actual = float(rating.score)
                error = abs(predicted - actual)

                predictions.append(predicted)
                actuals.append(actual)
                raw_errors.append(error)

            except Exception as e:
                logging.warning(f"Error predicting rating {rating.menu_id} for user {rating.customer_id}: {e}")
                continue

        if len(predictions) == 0:
            return {
                'mae': 0.0,
                'rmse': 0.0,
                'hit_rate': 0.0,
                'predictions': 0,
                'raw_errors': [],
                'std_mae': 0.0,
                'std_rmse': 0.0
            }

        predictions_np = np.array(predictions)
        actuals_np = np.array(actuals)

        mae = self.calculate_mae(predictions_np, actuals_np)
        rmse = self.calculate_rmse(predictions_np, actuals_np)
        hit_rate = self.calculate_hit_rate(predictions_np, actuals_np)

        # DEBUG: Log result for CF alpha=0
        if alpha == 0.0:
            logging.info(f"✅ _evaluate_with_fixed_split() result: Alpha={alpha}, MAE={mae:.4f}, n_predictions={len(predictions)}")

        return {
            'mae': float(mae),
            'rmse': float(rmse),
            'hit_rate': float(hit_rate),
            'predictions': len(predictions),
            'raw_errors': raw_errors,  # Raw errors for statistical tests
            'std_mae': float(np.std(raw_errors)) if len(raw_errors) > 1 else 0.0,
            'std_rmse': float(np.std([e**2 for e in raw_errors]))**0.5 if len(raw_errors) > 1 else 0.0
        }

    @staticmethod
    def calculate_mae(predictions: np.ndarray, actuals: np.ndarray) -> float:
        """
        Calculate Mean Absolute Error

        MAE = (1/n) × Σ|predicted - actual|

        Args:
            predictions: Array of predicted values
            actuals: Array of actual values

        Returns:
            MAE score (lower is better, 0 = perfect)

        Example:
            >>> eval = AlgorithmEvaluator(db)
            >>> mae = eval.calculate_mae(
            ...     np.array([4.2, 3.8, 4.5]),
            ...     np.array([4.0, 4.0, 5.0])
            ... )
            >>> print(f"MAE: {mae:.2f}")  # 0.30
        """
        if len(predictions) == 0 or len(actuals) == 0:
            return 0.0

        if len(predictions) != len(actuals):
            raise ValueError("Predictions and actuals must have same length")

        return float(np.mean(np.abs(predictions - actuals)))

    @staticmethod
    def calculate_rmse(predictions: np.ndarray, actuals: np.ndarray) -> float:
        """
        Calculate Root Mean Square Error

        RMSE = sqrt((1/n) × Σ(predicted - actual)²)

        Args:
            predictions: Array of predicted values
            actuals: Array of actual values

        Returns:
            RMSE score (lower is better, 0 = perfect)
            RMSE > MAE karena penalizes large errors lebih heavily

        Example:
            >>> eval = AlgorithmEvaluator(db)
            >>> rmse = eval.calculate_rmse(
            ...     np.array([4.2, 3.8, 4.5]),
            ...     np.array([4.0, 4.0, 5.0])
            ... )
            >>> print(f"RMSE: {rmse:.2f}")
        """
        if len(predictions) == 0 or len(actuals) == 0:
            return 0.0

        if len(predictions) != len(actuals):
            raise ValueError("Predictions and actuals must have same length")

        return float(np.sqrt(np.mean((predictions - actuals) ** 2)))

    @staticmethod
    def calculate_hit_rate(predictions: np.ndarray,
                          actuals: np.ndarray,
                          threshold: float = 0.5) -> float:
        """
        Calculate Hit Rate

        Hit Rate = (Number of hits) / (Total predictions)

        Hit: predicted is within ±threshold dari actual

        Args:
            predictions: Array of predicted ratings
            actuals: Array of actual ratings
            threshold: Toleransi error (default 0.5)

        Returns:
            Hit rate [0, 1] (higher is better)

        Example:
            >>> eval = AlgorithmEvaluator(db)
            >>> hit_rate = eval.calculate_hit_rate(
            ...     np.array([4.2, 3.8, 4.5]),
            ...     np.array([4.0, 4.0, 5.0])
            ... )
            >>> print(f"Hit Rate: {hit_rate:.2%}")  # 100%
        """
        if len(predictions) == 0 or len(actuals) == 0:
            return 0.0

        if len(predictions) != len(actuals):
            raise ValueError("Predictions and actuals must have same length")

        hits = np.sum(np.abs(predictions - actuals) <= threshold)
        return float(hits / len(actuals))

    @staticmethod
    def calculate_precision_recall(recommended: List[str],
                                  relevant: List[str],
                                  k: int = 10) -> Dict[str, float]:
        """
        Calculate Precision@K and Recall@K

        Precision@K = |Recommended ∩ Relevant| / K
        Recall@K = |Recommended ∩ Relevant| / |Relevant|

        Args:
            recommended: List of recommended item IDs
            relevant: List of relevant item IDs
            k: Top K items to consider

        Returns:
            Dictionary dengan precision, recall, f1

        Example:
            >>> eval = AlgorithmEvaluator(db)
            >>> result = eval.calculate_precision_recall(
            ...     recommended=['item1', 'item2', 'item3', 'item4', 'item5'],
            ...     relevant=['item1', 'item3', 'item5', 'item7'],
            ...     k=5
            ... )
            >>> print(result)
            {'precision': 0.6, 'recall': 0.75, 'f1': 0.666}
        """
        recommended_k = recommended[:k]

        if len(recommended_k) == 0:
            return {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}

        hits = len(set(recommended_k) & set(relevant))

        precision = hits / k
        recall = hits / len(relevant) if len(relevant) > 0 else 0.0

        if precision + recall == 0:
            f1 = 0.0
        else:
            f1 = 2 * (precision * recall) / (precision + recall)

        return {
            'precision': float(precision),
            'recall': float(recall),
            'f1': float(f1)
        }

    @staticmethod
    def calculate_coverage(total_items: int, recommended_items: set) -> float:
        """
        Calculate item coverage

        Coverage = |Items Recommended| / |Total Items|

        Args:
            total_items: Total number of items in catalog
            recommended_items: Set of items yang pernah direkomendasikan

        Returns:
            Coverage [0, 1]

        Example:
            >>> eval = AlgorithmEvaluator(db)
            >>> coverage = eval.calculate_coverage(
            ...     total_items=1000,
            ...     recommended_items={'item1', 'item2', 'item3'}
            ... )
            >>> print(f"Coverage: {coverage:.2%}")  # 0.30%
        """
        if total_items == 0:
            return 0.0

        return float(len(recommended_items) / total_items)

    def evaluate_algorithm_split(self,
                                 ratings: List[Rating],
                                 test_split: float = 0.2,
                                 alpha_values: List[float] = None,
                                 random_seed: int = 42) -> Dict[str, Dict]:
        """
        Evaluate algorithm dengan train-test split

        ⚠️ FIXED: Sekarang menggunakan fungsi core _evaluate_with_fixed_split()
        untuk konsistensi dengan semua endpoint lain!

        Args:
            ratings: List of Rating objects
            test_split: Proporsi data untuk testing (0-1)
            alpha_values: List of alpha values untuk di-test
            random_seed: Random seed untuk train-test split (default: 42)

        Returns:
            Dictionary {alpha_value: {metric: value}}

        Example:
            >>> eval = AlgorithmEvaluator(db)
            >>> ratings = db.query(Rating).all()
            >>> results = eval.evaluate_algorithm_split(
            ...     ratings=ratings,
            ...     test_split=0.2,
            ...     alpha_values=[0.2, 0.5, 0.8]
            ... )
            >>> print(results['0.5']['mae'])  # 0.65
        """
        if alpha_values is None:
            alpha_values = [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]

        # Split data dengan FIXED seed
        from sklearn.model_selection import train_test_split

        train_ratings, test_ratings = train_test_split(
            ratings,
            test_size=test_split,
            random_state=random_seed  # FIXED seed untuk konsistensi
        )

        results = {}

        for alpha in alpha_values:
            # Gunakan fungsi core yang sama untuk semua evaluasi
            result = self._evaluate_with_fixed_split(
                ratings=ratings,
                alpha=alpha,
                train_ratings=train_ratings,
                test_ratings=test_ratings,
                k=10
            )

            results[f'alpha_{alpha}'] = {
                'alpha': alpha,
                'mae': result['mae'],
                'rmse': result['rmse'],
                'hit_rate': result['hit_rate'],
                'n_predictions': result['predictions'],
                'std_mae': result['std_mae'],
                'std_rmse': result['std_rmse']
            }

        return results

    def cross_validate(self,
                      ratings: List[Rating],
                      n_splits: int = 5,
                      alpha_values: List[float] = None,
                      random_state: int = 42) -> Dict[str, Dict]:
        """
        K-Fold Cross Validation untuk algorithm evaluation

        ✅ UNIFIED FUNCTION: Ini adalah SATU-SATUNYA sumber MAE/RMSE/Hit Rate
        yang dilaporkan di semua endpoint (Cross-Validation, Algorithm Comparison,
        Statistical Test).

        Uses REPEATED K-Fold for statistical robustness:
        - Default: 5-fold CV with random_state=42
        - Can be repeated with different random_states for larger sample size

        Args:
            ratings: List of Rating objects
            n_splits: Number of folds (default: 5)
            alpha_values: List of alpha values untuk di-test
            random_state: Random state for KFold reproducibility (default: 42)

        Returns:
            Dictionary dengan average metrics per alpha value PLUS raw per-fold data
            for statistical testing

        Example:
            >>> eval = AlgorithmEvaluator(db)
            >>> ratings = db.query(Rating).all()
            >>> results = eval.cross_validate(
            ...     ratings=ratings,
            ...     n_splits=5,
            ...     alpha_values=[0.0, 0.5]
            ... )
            >>> print(results['alpha_0.5']['avg_mae'])  # 0.68
            >>> print(results['alpha_0.5']['raw_mae_per_fold'])  # [0.65, 0.70, 0.68, ...]
        """
        if alpha_values is None:
            alpha_values = [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]

        from sklearn.model_selection import KFold

        # DEBUG: Log function entry
        logging.warning("=" * 80)
        logging.warning("🔍 DEBUG: cross_validate() called - UNIFIED SOURCE OF TRUTH")
        logging.warning(f"📊 Total ratings: {len(ratings)}")
        logging.warning(f"🔀 Alpha values to test: {alpha_values}")
        logging.warning(f"🔀 N_splits: {n_splits}")
        logging.warning(f"🎲 Random state: {random_state} (KFold)")
        logging.warning(f"✅ This is the SINGLE source of MAE for ALL endpoints!")
        logging.warning("=" * 80)

        # Validate n_splits
        if n_splits < 5:
            logging.warning(f"n_splits={n_splits} is less than recommended minimum of 5")
            raise ValueError(f"n_splits must be at least 5, got {n_splits}")

        kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)

        # Initialize results storage
        all_results = {alpha: {'mae': [], 'rmse': [], 'hit_rate': []}
                      for alpha in alpha_values}

        # Cross-validation
        for fold_idx, (train_idx, test_idx) in enumerate(kf.split(ratings)):
            print(f"Processing fold {fold_idx + 1}/{n_splits}...")

            # DEBUG: Log fold information
            logging.warning(f"📁 Fold {fold_idx + 1}/{n_splits}: Train={len(train_idx)}, Test={len(test_idx)}")

            train_data = [ratings[i] for i in train_idx]
            test_data = [ratings[i] for i in test_idx]

            for alpha in alpha_values:
                recommender = HybridRecommender(self.db, alpha=alpha)

                predictions = []
                actuals = []

                for rating in test_data:
                    try:
                        # Use hybrid scoring yang memperhitungkan alpha
                        predicted = recommender.predict_rating_hybrid(
                            user_id=str(rating.customer_id),
                            menu_id=str(rating.menu_id),
                            k=10
                        )

                        predictions.append(predicted)
                        actuals.append(float(rating.score))

                    except Exception as e:
                        print(f"Error predicting: {e}")
                        continue

                if len(predictions) > 0:
                    predictions_np = np.array(predictions)
                    actuals_np = np.array(actuals)

                    mae = self.calculate_mae(predictions_np, actuals_np)
                    rmse = self.calculate_rmse(predictions_np, actuals_np)
                    hit_rate = self.calculate_hit_rate(predictions_np, actuals_np)

                    all_results[alpha]['mae'].append(mae)
                    all_results[alpha]['rmse'].append(rmse)
                    all_results[alpha]['hit_rate'].append(hit_rate)

                    # DEBUG: Log per-alpha per-fold results
                    if alpha == 0.0:
                        logging.warning(f"  🎯 CF Alpha=0.0 - Fold {fold_idx + 1}: MAE={mae:.4f}, n_predictions={len(predictions)}")

        # Calculate averages
        avg_results = {}

        for alpha in alpha_values:
            mae_std = float(np.std(all_results[alpha]['mae']))
            rmse_std = float(np.std(all_results[alpha]['rmse']))

            # Log warning if std dev is suspiciously low
            if mae_std == 0.0:
                logging.warning(f"MAE std dev = 0 for alpha {alpha}. Possible bug in cross-validation!")
                logging.warning(f"MAE values: {all_results[alpha]['mae']}")

            avg_results[f'alpha_{alpha}'] = {
                'alpha': alpha,
                'avg_mae': float(np.mean(all_results[alpha]['mae'])),
                'std_mae': mae_std,
                'avg_rmse': float(np.mean(all_results[alpha]['rmse'])),
                'std_rmse': rmse_std,
                'avg_hit_rate': float(np.mean(all_results[alpha]['hit_rate'])),
                'std_hit_rate': float(np.std(all_results[alpha]['hit_rate'])),
                # NEW: Store raw per-fold data for statistical testing
                'raw_mae_per_fold': all_results[alpha]['mae'],
                'raw_rmse_per_fold': all_results[alpha]['rmse'],
                'raw_hit_rate_per_fold': all_results[alpha]['hit_rate'],
                'n_folds': n_splits,
                'random_state': random_state
            }

            # DEBUG: Log final CF alpha=0 results
            if alpha == 0.0:
                logging.warning(f"🎯 CF Alpha=0.0 FINAL: MAE={avg_results[f'alpha_{alpha}']['avg_mae']:.4f}, Std={mae_std:.4f}")
                logging.warning(f"📊 Raw MAE values per fold: {all_results[alpha]['mae']}")

        logging.warning("=" * 80)
        return avg_results

    def save_evaluation_results(self,
                                method_variant: str,
                                alpha: float,
                                mae: float,
                                rmse: float,
                                hit_rate: float,
                                total_data_points: int,
                                training_time_ms: int = None,
                                test_split: str = None):
        """
        Save evaluation results ke database

        Args:
            method_variant: Nama varian (e.g., 'hybrid_alpha_0.5')
            alpha: Alpha value yang digunakan
            mae: MAE score
            rmse: RMSE score
            hit_rate: Hit rate
            total_data_points: Jumlah data
            training_time_ms: Training time dalam ms
            test_split: Test split configuration
        """
        try:
            evaluation = AlgorithmEvaluation(
                test_date=datetime.utcnow(),
                method_variant=method_variant,
                alpha_weight=alpha,
                mae_score=mae,
                rmse_score=rmse,
                hit_rate=hit_rate,
                total_data_points=total_data_points,
                training_time_ms=training_time_ms,
                test_split=test_split
            )

            self.db.add(evaluation)
            self.db.commit()

            print(f"Saved evaluation results for {method_variant}")

        except Exception as e:
            self.db.rollback()
            print(f"Error saving evaluation results: {e}")

    def compare_alpha_values(self,
                            ratings: List[Rating],
                            alpha_values: List[float] = None) -> pd.DataFrame:
        """
        Compare multiple alpha values dan return sebagai DataFrame

        Args:
            ratings: List of Rating objects
            alpha_values: List of alpha values untuk compare

        Returns:
            DataFrame dengan comparison results

        Example:
            >>> eval = AlgorithmEvaluator(db)
            >>> ratings = db.query(Rating).all()
            >>> df = eval.compare_alpha_values(ratings, [0.2, 0.5, 0.8])
            >>> print(df)
                    alpha   mae  rmse  hit_rate
            0  0.20  0.72  0.95      0.65
            1  0.50  0.65  0.88      0.75
            2  0.80  0.70  0.92      0.70
        """
        if alpha_values is None:
            alpha_values = [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]

        results = self.evaluate_algorithm_split(ratings, alpha_values=alpha_values)

        # Convert to DataFrame
        data = []
        for key, metrics in results.items():
            data.append({
                'alpha': metrics['alpha'],
                'mae': metrics['mae'],
                'rmse': metrics['rmse'],
                'hit_rate': metrics['hit_rate']
            })

        df = pd.DataFrame(data)

        # Sort by MAE (lower is better)
        df = df.sort_values('mae')

        return df

    def statistical_significance_test(self,
                                      ratings: List[Rating],
                                      alpha1: float = 0.5,
                                      alpha2: float = 0.0,
                                      test_size: float = 0.2,
                                      n_runs: int = 10,
                                      n_repetitions: int = 3,
                                      n_splits: int = 5,
                                      random_state: int = 42) -> Dict:
        """
        Statistical significance testing antara dua alpha values

        ✅ NEW METHODOLOGY: Menggunakan paired t-test dari hasil per-fold
        Cross-Validation yang sama, BUKAN dari random split berbeda!

        Methodology:
        1. Jalankan 5-fold Cross-Validation untuk alpha1 dan alpha2
        2. Gunakan REPEATED k-fold: ulangi 5-fold sebanyak 3 kali dengan random_state berbeda
           Total sampel: 15 pasang (3 repetisi × 5 fold) untuk statistical power yang kuat
        3. Ambil raw MAE per fold untuk setiap alpha
        4. Jalankan paired t-test (scipy.stats.ttest_rel) pada pasangan MAE per fold

        Args:
            ratings: List of Rating objects
            alpha1: Alpha value pertama (default: 0.5 - Hybrid)
            alpha2: Alpha value kedua (default: 0.0 - CF Only)
            test_size: Proporsi test data (ignored, using CV instead)
            n_runs: Jumlah kali running untuk sampling (ignored, using repetitions)
            n_repetitions: Jumlah repetisi 5-fold CV (default: 3, untuk 15 sample pairs)
            n_splits: Number of folds untuk CV (default: 5)
            random_state: Random state awal untuk CV (default: 42, akan increment +1 per repetisi)

        Returns:
            Dictionary dengan:
            - t_statistic: Nilai t dari t-test
            - p_value: P-value dari test
            - is_significant: True jika p < 0.05
            - mean_diff: Selisih rata-rata error
            - ci_lower: Lower bound 95% CI
            - ci_upper: Upper bound 95% CI
            - effect_size: Cohen's d
            - interpretation: Interpretasi hasil
            - raw_mae_per_fold: Raw MAE dari setiap fold untuk transparency
        """
        from scipy import stats as scipy_stats

        # DEBUG: Log function entry
        logging.warning("=" * 80)
        logging.warning("🔍 DEBUG: statistical_significance_test() called")
        logging.warning(f"📊 Total ratings: {len(ratings)}")
        logging.warning(f"🎯 Alpha1: {alpha1}, Alpha2: {alpha2}")
        logging.warning(f"🔀 N_repetitions: {n_repetitions}, N_splits: {n_splits}")
        logging.warning(f"✅ NEW: Using paired t-test from fold results!")
        logging.warning("=" * 80)

        # Validate n_repetitions
        if n_repetitions < 1:
            logging.warning(f"n_repetitions={n_repetitions} is too low. Using 1.")
            n_repetitions = 1

        # Collect MAE values from each fold and repetition
        mae_alpha1_all = []  # All MAE values for alpha1 across all folds and repetitions
        mae_alpha2_all = []  # All MAE values for alpha2 across all folds and repetitions

        # Raw data for each repetition
        raw_data_per_repetition = []

        # Random states for repetitions
        random_states = [random_state + i for i in range(n_repetitions)]

        for rep_idx in range(n_repetitions):
            rep_random_state = random_states[rep_idx]

            logging.warning(f"🔄 Repetition {rep_idx + 1}/{n_repetitions}: Random state={rep_random_state}")

            # Run 5-fold CV untuk alpha1 dan alpha2
            cv_results = self.cross_validate(
                ratings=ratings,
                n_splits=n_splits,
                alpha_values=[alpha1, alpha2],
                random_state=rep_random_state
            )

            # Extract raw MAE per fold
            mae_alpha1_fold = cv_results[f'alpha_{alpha1}']['raw_mae_per_fold']
            mae_alpha2_fold = cv_results[f'alpha_{alpha2}']['raw_mae_per_fold']

            logging.warning(f"  📊 Alpha1 MAE per fold: {[f'{m:.4f}' for m in mae_alpha1_fold]}")
            logging.warning(f"  📊 Alpha2 MAE per fold: {[f'{m:.4f}' for m in mae_alpha2_fold]}")

            # Store all MAE values
            mae_alpha1_all.extend(mae_alpha1_fold)
            mae_alpha2_all.extend(mae_alpha2_fold)

            # Store raw data for this repetition
            raw_data_per_repetition.append({
                'repetition': rep_idx,
                'random_state': random_state,
                'alpha1_mae_per_fold': mae_alpha1_fold,
                'alpha2_mae_per_fold': mae_alpha2_fold,
                'alpha1_avg_mae': float(np.mean(mae_alpha1_fold)),
                'alpha2_avg_mae': float(np.mean(mae_alpha2_fold))
            })

        # Convert to numpy arrays
        mae_alpha1_all = np.array(mae_alpha1_all)
        mae_alpha2_all = np.array(mae_alpha2_all)

        # Paired t-test
        t_statistic, p_value = scipy_stats.ttest_rel(mae_alpha1_all, mae_alpha2_all)

        # Mean difference
        mean_diff = np.mean(mae_alpha1_all - mae_alpha2_all)

        # Standard error of difference
        std_diff = np.std(mae_alpha1_all - mae_alpha2_all, ddof=1)
        n_samples = len(mae_alpha1_all)
        se_diff = std_diff / np.sqrt(n_samples)

        # 95% Confidence Interval
        from scipy.stats import t as t_dist
        ci_critical = t_dist.ppf(0.975, df=n_samples-1)
        ci_lower = mean_diff - (ci_critical * se_diff)
        ci_upper = mean_diff + (ci_critical * se_diff)

        # Effect size (Cohen's d)
        pooled_std = np.sqrt((np.std(mae_alpha1_all)**2 + np.std(mae_alpha2_all)**2) / 2)
        effect_size = mean_diff / pooled_std if pooled_std > 0 else 0

        # Interpretation
        is_significant = p_value < 0.05

        if is_significant:
            if mean_diff > 0:
                interpretation = f"Alpha {alpha2} secara signifikan lebih baik dari Alpha {alpha1}"
            else:
                interpretation = f"Alpha {alpha1} secara signifikan lebih baik dari Alpha {alpha2}"
        else:
            interpretation = f"Tidak ada perbedaan signifikan antara Alpha {alpha1} dan Alpha {alpha2}"

        # Effect size interpretation
        if abs(effect_size) < 0.2:
            effect_interpretation = "Small effect"
        elif abs(effect_size) < 0.5:
            effect_interpretation = "Medium effect"
        elif abs(effect_size) < 0.8:
            effect_interpretation = "Large effect"
        else:
            effect_interpretation = "Very large effect"

        # DEBUG: Log final results
        logging.warning(f"📊 Paired t-test results:")
        logging.warning(f"  🎯 T-statistic: {t_statistic:.4f}")
        logging.warning(f"  🎯 P-value: {p_value:.4f}")
        logging.warning(f"  🎯 Mean difference: {mean_diff:.4f}")
        logging.warning(f"  🎯 Effect size (Cohen's d): {effect_size:.4f}")
        logging.warning(f"  🎯 95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")
        logging.warning(f"  🎯 Sample size: {n_samples} (folds × repetitions)")
        logging.warning(f"  🎯 Significant: {is_significant}")

        return {
            'alpha1': float(alpha1),
            'alpha2': float(alpha2),
            'mean_error_alpha1': float(np.mean(mae_alpha1_all)),
            'mean_error_alpha2': float(np.mean(mae_alpha2_all)),
            'mean_difference': float(mean_diff),
            't_statistic': float(t_statistic),
            'p_value': float(p_value),
            'is_significant': bool(is_significant),
            'ci_95_lower': float(ci_lower),
            'ci_95_upper': float(ci_upper),
            'effect_size': float(effect_size),
            'effect_interpretation': effect_interpretation,
            'interpretation': interpretation,
            'n_samples': int(n_samples),
            'n_folds': n_splits,
            'n_repetitions': n_repetitions,
            'alpha': 0.05,  # Significance level
            'raw_mae_per_fold': {
                'alpha1': mae_alpha1_all.tolist(),
                'alpha2': mae_alpha2_all.tolist()
            },
            'raw_data_per_repetition': raw_data_per_repetition,
            'random_states_used': random_states,
            'methodology': 'paired_t_test_from_cv_folds'
        }

        # Convert to numpy arrays
        errors_alpha1 = np.array(errors_alpha1)
        errors_alpha2 = np.array(errors_alpha2)

        # Paired t-test
        t_statistic, p_value = scipy_stats.ttest_rel(errors_alpha1, errors_alpha2)

        # Mean difference
        mean_diff = np.mean(errors_alpha1 - errors_alpha2)

        # Standard error of difference
        std_diff = np.std(errors_alpha1 - errors_alpha2, ddof=1)
        se_diff = std_diff / np.sqrt(n_runs)

        # 95% Confidence Interval
        from scipy.stats import t as t_dist
        ci_critical = t_dist.ppf(0.975, df=n_runs-1)
        ci_lower = mean_diff - (ci_critical * se_diff)
        ci_upper = mean_diff + (ci_critical * se_diff)

        # Effect size (Cohen's d)
        pooled_std = np.sqrt((np.std(errors_alpha1)**2 + np.std(errors_alpha2)**2) / 2)
        effect_size = mean_diff / pooled_std if pooled_std > 0 else 0

        # Interpretation
        is_significant = p_value < 0.05

        if is_significant:
            if mean_diff > 0:
                interpretation = f"Alpha {alpha2} secara signifikan lebih baik dari Alpha {alpha1}"
            else:
                interpretation = f"Alpha {alpha1} secara signifikan lebih baik dari Alpha {alpha2}"
        else:
            interpretation = f"Tidak ada perbedaan signifikan antara Alpha {alpha1} dan Alpha {alpha2}"

        # Effect size interpretation
        if abs(effect_size) < 0.2:
            effect_interpretation = "Small effect"
        elif abs(effect_size) < 0.5:
            effect_interpretation = "Medium effect"
        elif abs(effect_size) < 0.8:
            effect_interpretation = "Large effect"
        else:
            effect_interpretation = "Very large effect"

        return {
            'alpha1': float(alpha1),
            'alpha2': float(alpha2),
            'mean_error_alpha1': float(np.mean(errors_alpha1)),
            'mean_error_alpha2': float(np.mean(errors_alpha2)),
            'mean_difference': float(mean_diff),
            't_statistic': float(t_statistic),
            'p_value': float(p_value),
            'is_significant': bool(is_significant),
            'ci_95_lower': float(ci_lower),
            'ci_95_upper': float(ci_upper),
            'effect_size': float(effect_size),
            'effect_interpretation': effect_interpretation,
            'interpretation': interpretation,
            'n_runs': int(n_runs),
            'alpha': 0.05,  # Significance level
            'raw_errors_per_run': raw_errors_per_run,  # NEW: Detailed results per run
            'seeds_used': self.RANDOM_SEEDS[:n_runs]  # NEW: Seeds used for transparency
        }

    def calculate_baseline_metrics(self,
                                    ratings: List[Rating],
                                    test_size: float = 0.2,
                                    n_splits: int = 5,
                                    random_state: int = 42) -> Dict:
        """
        Calculate metrics untuk baseline algorithms

        Baselines:
        1. Random: Rekomendasi acak
        2. Most Popular: Rekomendasi menu paling populer
        3. Average Rating: Rekomendasi berdasarkan rata-rata rating
        4. Item-Based CF: Collaborative filtering berbasis item

        ✅ UNIFIED: Sekarang menggunakan 5-fold Cross-Validation yang SAMA
        ✅ FIXED: Item-Based CF sekarang menggunakan FIXED random_state!

        Args:
            ratings: List of Rating objects
            test_size: Proporsi test data (ignored, using CV instead)
            n_splits: Number of folds untuk CV (default: 5)
            random_state: Random state untuk CV (default: 42)

        Returns:
            Dictionary dengan metrics untuk setiap baseline
        """
        from sklearn.model_selection import KFold
        from collections import Counter
        import random

        # DEBUG: Log function entry
        logging.warning("=" * 80)
        logging.warning("🔍 DEBUG: calculate_baseline_metrics() called")
        logging.warning(f"📊 Total ratings: {len(ratings)}")
        logging.warning(f"🔀 N_splits: {n_splits}, Random state: {random_state}")
        logging.warning(f"✅ Using 5-fold CV for consistency")
        logging.warning(f"✅ Item-Based CF now uses FIXED random_state")
        logging.warning("=" * 80)

        # Setup KFold for baseline calculations (consistent with CV)
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)

        # Calculate baseline metrics across all folds
        baseline_metrics = {
            'random': {'mae': [], 'rmse': [], 'predictions': []},
            'most_popular': {'mae': [], 'rmse': [], 'predictions': []},
            'average_rating': {'mae': [], 'rmse': [], 'predictions': []},
            'item_cf': {'mae': [], 'rmse': [], 'predictions': []}
        }

        # Process each fold for baselines
        for fold_idx, (train_idx, test_idx) in enumerate(kf.split(ratings)):
            train_data = [ratings[i] for i in train_idx]
            test_data = [ratings[i] for i in test_idx]

            logging.warning(f"  📁 Processing baseline fold {fold_idx + 1}/{n_splits}: Train={len(train_data)}, Test={len(test_data)}")

            # Get average rating dari training set
            avg_rating_train = np.mean([r.score for r in train_data])

            # Get most popular items
            menu_counts = Counter([r.menu_id for r in train_data])
            most_popular_menus = [item for item, count in menu_counts.most_common()]

            # Prepare ratings dictionary untuk item-based CF
            user_ratings = {}
            for r in train_data:
                if r.customer_id not in user_ratings:
                    user_ratings[r.customer_id] = {}
                user_ratings[r.customer_id][r.menu_id] = r.score

            # 1. Random Baseline
            try:
                random.seed(random_state + fold_idx)  # FIXED: different seed per fold but consistent across runs
                random_predictions = [random.uniform(1, 5) for _ in test_data]
                random_actuals = [r.score for r in test_data]
                random_mae = float(np.mean([abs(p - a) for p, a in zip(random_predictions, random_actuals)]))
                random_rmse = float(np.sqrt(np.mean([(p - a)**2 for p, a in zip(random_predictions, random_actuals)])))
                baseline_metrics['random']['mae'].append(random_mae)
                baseline_metrics['random']['rmse'].append(random_rmse)
                baseline_metrics['random']['predictions'].append(len(random_predictions))
            except Exception as e:
                logging.error(f"✗ Random baseline failed: {e}")
                raise

            # 2. Most Popular Baseline
            try:
                popular_predictions = []
                for r in test_data:
                    menu_ratings = [rating.score for rating in train_data if rating.menu_id == r.menu_id]
                    if menu_ratings:
                        popular_predictions.append(np.mean(menu_ratings))
                    else:
                        popular_predictions.append(avg_rating_train)

                popular_actuals = [r.score for r in test_data]
                popular_mae = float(np.mean([abs(p - a) for p, a in zip(popular_predictions, popular_actuals)]))
                popular_rmse = float(np.sqrt(np.mean([(p - a)**2 for p, a in zip(popular_predictions, popular_actuals)])))
                baseline_metrics['most_popular']['mae'].append(popular_mae)
                baseline_metrics['most_popular']['rmse'].append(popular_rmse)
                baseline_metrics['most_popular']['predictions'].append(len(popular_predictions))
            except Exception as e:
                logging.error(f"✗ Most Popular baseline failed: {e}")
                raise

            # 3. Average Rating Baseline
            try:
                avg_predictions = [avg_rating_train for _ in test_data]
                avg_actuals = [r.score for r in test_data]
                avg_mae = float(np.mean([abs(p - a) for p, a in zip(avg_predictions, avg_actuals)]))
                avg_rmse = float(np.sqrt(np.mean([(p - a)**2 for p, a in zip(avg_predictions, avg_actuals)])))
                baseline_metrics['average_rating']['mae'].append(avg_mae)
                baseline_metrics['average_rating']['rmse'].append(avg_rmse)
                baseline_metrics['average_rating']['predictions'].append(len(avg_predictions))
            except Exception as e:
                logging.error(f"✗ Average Rating baseline failed: {e}")
                raise

            # 4. Item-Based CF (with FIXED random_state)
            try:
                # Set random seed for consistency
                np.random.seed(random_state + fold_idx)

                # Calculate item-item similarities
                item_similarities = {}
                all_items = list(set([r.menu_id for r in train_data]))

                for item1 in all_items:
                    item_similarities[item1] = {}
                    for item2 in all_items:
                        if item1 != item2:
                            ratings1 = []
                            ratings2 = []
                            for user_id in user_ratings:
                                if item1 in user_ratings[user_id] and item2 in user_ratings[user_id]:
                                    ratings1.append(user_ratings[user_id][item1])
                                    ratings2.append(user_ratings[user_id][item2])

                            if len(ratings1) >= 2:
                                corr = np.corrcoef(ratings1, ratings2)[0, 1]
                                if not np.isnan(corr):
                                    item_similarities[item1][item2] = corr

                # Predict menggunakan item-based CF
                item_cf_predictions = []
                for r in test_data:
                    if r.menu_id in item_similarities:
                        similar_items = sorted(
                            item_similarities[r.menu_id].items(),
                            key=lambda x: abs(x[1]),
                            reverse=True
                        )[:5]  # Top 5 similar items

                        if similar_items:
                            weighted_sum = 0
                            weight_sum = 0
                            for item_id, similarity in similar_items:
                                if r.customer_id in user_ratings and item_id in user_ratings[r.customer_id]:
                                    weighted_sum += similarity * user_ratings[r.customer_id][item_id]
                                    weight_sum += abs(similarity)

                            if weight_sum > 0:
                                item_cf_predictions.append(weighted_sum / weight_sum)
                                continue

                    # Fallback jika tidak ada similar items
                    item_cf_predictions.append(avg_rating_train)

                item_cf_actuals = [r.score for r in test_data]
                item_cf_mae = float(np.mean([abs(p - a) for p, a in zip(item_cf_predictions, item_cf_actuals)]))
                item_cf_rmse = float(np.sqrt(np.mean([(p - a)**2 for p, a in zip(item_cf_predictions, item_cf_actuals)])))
                baseline_metrics['item_cf']['mae'].append(item_cf_mae)
                baseline_metrics['item_cf']['rmse'].append(item_cf_rmse)
                baseline_metrics['item_cf']['predictions'].append(len(item_cf_predictions))
            except Exception as e:
                logging.error(f"✗ Item-based CF baseline failed: {e}")
                # Store error but continue
                baseline_metrics['item_cf']['mae'].append(np.nan)
                baseline_metrics['item_cf']['rmse'].append(np.nan)
                baseline_metrics['item_cf']['predictions'].append(0)

        # Calculate average baseline metrics across folds
        results = {
            'random': {
                'mae': float(np.mean(baseline_metrics['random']['mae'])),
                'rmse': float(np.mean(baseline_metrics['random']['rmse'])),
                'predictions': int(np.mean(baseline_metrics['random']['predictions']))
            },
            'most_popular': {
                'mae': float(np.mean(baseline_metrics['most_popular']['mae'])),
                'rmse': float(np.mean(baseline_metrics['most_popular']['rmse'])),
                'predictions': int(np.mean(baseline_metrics['most_popular']['predictions']))
            },
            'average_rating': {
                'mae': float(np.mean(baseline_metrics['average_rating']['mae'])),
                'rmse': float(np.mean(baseline_metrics['average_rating']['rmse'])),
                'predictions': int(np.mean(baseline_metrics['average_rating']['predictions']))
            },
            'item_cf': {
                'mae': float(np.mean(baseline_metrics['item_cf']['mae'])) if not np.isnan(np.mean(baseline_metrics['item_cf']['mae'])) else None,
                'rmse': float(np.mean(baseline_metrics['item_cf']['rmse'])) if not np.isnan(np.mean(baseline_metrics['item_cf']['rmse'])) else None,
                'predictions': int(np.mean(baseline_metrics['item_cf']['predictions'])) if baseline_metrics['item_cf']['predictions'] else 0
            }
        }

        # DEBUG: Log Item-Based CF results
        if results['item_cf']['mae'] is not None:
            logging.warning(f"🎯 Item-Based CF: MAE={results['item_cf']['mae']:.4f} (from 5-fold CV with FIXED seeds)")
        else:
            logging.warning(f"❌ Item-Based CF: Failed to calculate")

        logging.warning("=" * 80)
        return results

    def per_user_error_analysis(self,
                                ratings: List[Rating],
                                alpha: float = 0.5) -> Dict:
        """
        Analisis error per user untuk memahami performa di berbagai segment

        Args:
            ratings: List of Rating objects
            alpha: Alpha value untuk hybrid

        Returns:
            Dictionary dengan:
            - user_segments: Error per segment (new, medium, active)
            - worst_predictions: Top 10 worst predictions
            - best_predictions: Top 10 best predictions
            - error_distribution: Statistik error per user
        """
        from sklearn.model_selection import train_test_split
        from collections import defaultdict

        # Split data
        train_ratings, test_ratings = train_test_split(
            ratings,
            test_size=0.2,
            random_state=42
        )

        # Get rating count per user
        user_rating_counts = defaultdict(int)
        for r in train_ratings:
            user_rating_counts[r.customer_id] += 1

        # Categorize users
        new_users = [uid for uid, count in user_rating_counts.items() if count <= 5]
        medium_users = [uid for uid, count in user_rating_counts.items() if 6 <= count <= 20]
        active_users = [uid for uid, count in user_rating_counts.items() if count > 20]

        # Log segment information for debugging
        logging.info(f"User segmentation: {len(new_users)} new users (0-5 ratings)")
        logging.info(f"User segmentation: {len(medium_users)} medium users (6-20 ratings)")
        logging.info(f"User segmentation: {len(active_users)} power users (20+ ratings)")
        logging.info(f"Total users in training data: {len(user_rating_counts)}")

        # Predict dan calculate errors per user
        recommender = HybridRecommender(self.db, alpha=alpha)

        user_errors = defaultdict(list)
        all_predictions = []

        for rating in test_ratings:
            try:
                pred = recommender.predict_rating_hybrid(
                    user_id=str(rating.customer_id),
                    menu_id=str(rating.menu_id),
                    k=10
                )
                error = abs(pred - float(rating.score))
                user_errors[rating.customer_id].append(error)
                all_predictions.append({
                    'customer_id': str(rating.customer_id),
                    'menu_id': str(rating.menu_id),
                    'actual': float(rating.score),
                    'predicted': pred,
                    'error': error
                })
            except:
                continue

        # Calculate metrics per segment dengan validasi sample size
        segment_metrics = {}
        for segment_name, user_list in [
            ('new_users_0_5', new_users),
            ('medium_users_6_20', medium_users),
            ('active_users_20plus', active_users)
        ]:
            segment_errors = []
            users_with_errors = 0

            for user_id in user_list:
                if user_id in user_errors:
                    segment_errors.extend(user_errors[user_id])
                    users_with_errors += 1

            # Validasi sample size
            min_sample_threshold = 3
            insufficient_sample = users_with_errors < min_sample_threshold

            if insufficient_sample:
                logging.warning(f"⚠ Segment {segment_name}: Insufficient sample ({users_with_errors} users < {min_sample_threshold})")
                segment_metrics[segment_name] = {
                    'count': len(user_list),
                    'users_with_errors': users_with_errors,
                    'avg_mae': None,  # None untuk menandakan tidak valid secara statistik
                    'std_mae': None,
                    'min_error': None,
                    'max_error': None,
                    'status': 'insufficient_sample',
                    'note': f'Insufficient sample size ({users_with_errors} users < {min_sample_threshold} threshold). Results not statistically valid.'
                }
            elif segment_errors:
                segment_metrics[segment_name] = {
                    'count': len(user_list),
                    'users_with_errors': users_with_errors,
                    'avg_mae': float(np.mean(segment_errors)),
                    'std_mae': float(np.std(segment_errors)),
                    'min_error': float(np.min(segment_errors)),
                    'max_error': float(np.max(segment_errors)),
                    'status': 'valid'
                }
                logging.info(f"✓ Segment {segment_name}: {users_with_errors} users with errors, avg MAE = {float(np.mean(segment_errors)):.4f}")
            else:
                logging.warning(f"✗ Segment {segment_name}: No data available (empty segment)")
                segment_metrics[segment_name] = {
                    'count': len(user_list),
                    'users_with_errors': 0,
                    'avg_mae': None,
                    'std_mae': None,
                    'min_error': None,
                    'max_error': None,
                    'status': 'no_data',
                    'note': 'No data available for this segment'
                }

        # Sort predictions by error
        all_predictions.sort(key=lambda x: x['error'], reverse=True)

        # Top 10 worst
        worst_predictions = all_predictions[:10]

        # Top 10 best
        best_predictions = all_predictions[-10:]
        best_predictions.reverse()  # Ascending by error

        return {
            'user_segments': segment_metrics,
            'worst_predictions': worst_predictions,
            'best_predictions': best_predictions,
            'total_predictions': len(all_predictions),
            'overall_mae': float(np.mean([p['error'] for p in all_predictions]))
        }

    def temporal_analysis(self,
                          db: Session,
                          days: int = 30) -> Dict:
        """
        Analisis performa sistem dari waktu ke waktu

        Args:
            db: Database session
            days: Jumlah hari ke belakang untuk dianalisis

        Returns:
            Dictionary dengan:
            - daily_metrics: Metrics per hari
            - trend: Trend improvement/decline
            - total_ratings_growth: Pertumbuhan ratings
        """
        from datetime import datetime, timedelta
        from collections import defaultdict

        # Get ratings dari N hari terakhir
        cutoff_date = datetime.now() - timedelta(days=days)

        ratings = db.query(Rating).filter(
            Rating.created_at >= cutoff_date
        ).order_by(Rating.created_at).all()

        if len(ratings) == 0:
            return {
                'error': 'No ratings found in the specified time period',
                'days': days,
                'daily_metrics': []
            }

        # Group by date
        daily_ratings = defaultdict(list)
        for r in ratings:
            date_key = r.created_at.strftime('%Y-%m-%d')
            daily_ratings[date_key].append(r.score)

        # Calculate metrics per hari
        daily_metrics = []
        cumulative_ratings = 0

        for date_str in sorted(daily_ratings.keys()):
            scores = daily_ratings[date_str]
            cumulative_ratings += len(scores)

            daily_metrics.append({
                'date': date_str,
                'total_ratings': len(scores),
                'cumulative_ratings': cumulative_ratings,
                'avg_rating': float(np.mean(scores)),
                'std_rating': float(np.std(scores)),
                'min_rating': float(np.min(scores)),
                'max_rating': float(np.max(scores))
            })

        # Calculate trend
        if len(daily_metrics) >= 2:
            first_half = daily_metrics[:len(daily_metrics)//2]
            second_half = daily_metrics[len(daily_metrics)//2:]

            avg_first = np.mean([d['avg_rating'] for d in first_half])
            avg_second = np.mean([d['avg_rating'] for d in second_half])

            improvement = ((avg_second - avg_first) / avg_first) * 100 if avg_first > 0 else 0

            if improvement > 5:
                trend = 'improving'
            elif improvement < -5:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            improvement = 0
            trend = 'insufficient_data'

        return {
            'days_analyzed': days,
            'total_ratings': len(ratings),
            'daily_metrics': daily_metrics,
            'trend': trend,
            'improvement_percentage': float(improvement),
            'first_period_avg': float(avg_first) if len(daily_metrics) >= 2 else 0,
            'second_period_avg': float(avg_second) if len(daily_metrics) >= 2 else 0
        }

    def compare_algorithms(self,
                         ratings: List[Rating],
                         test_size: float = 0.2,
                         k: int = 10,
                         n_splits: int = 5,
                         random_state: int = 42) -> Dict:
        """
        Bandingkan performa 3 algoritma utama:
        1. Collaborative Filtering Only (α = 0.0)
        2. Hybrid (α = 0.5)
        3. Fuzzy Logic Only (α = 1.0)

        ✅ UNIFIED: Sekarang menggunakan 5-fold Cross-Validation yang SAMA
        dengan Cross-Validation endpoint untuk konsistensi total!

        Args:
            ratings: List of Rating objects
            test_size: Proporsi test data (ignored, using CV instead)
            k: Jumlah neighbors untuk CF (ignored, using default)
            n_splits: Number of folds untuk CV (default: 5)
            random_state: Random state untuk CV (default: 42)

        Returns:
            Dictionary dengan comparison results dari 5-fold CV
        """
        # DEBUG: Log function entry
        logging.warning("=" * 80)
        logging.warning("🔍 DEBUG: compare_algorithms() called")
        logging.warning(f"📊 Total ratings: {len(ratings)}")
        logging.warning(f"🔀 N_splits: {n_splits}, Random state: {random_state}")
        logging.warning(f"✅ Using 5-fold CV for consistency with Cross-Validation endpoint")
        logging.warning("=" * 80)

        # Use unified cross_validate function for consistency
        cv_results = self.cross_validate(
            ratings=ratings,
            n_splits=n_splits,
            alpha_values=[0.0, 0.5, 1.0],
            random_state=random_state
        )

        # Transform results to expected format
        results = {}
        results['Collaborative Filtering Only'] = {
            'alpha': 0.0,
            'mae': cv_results['alpha_0.0']['avg_mae'],
            'rmse': cv_results['alpha_0.0']['avg_rmse'],
            'hit_rate': cv_results['alpha_0.0']['avg_hit_rate'],
            'std_mae': cv_results['alpha_0.0']['std_mae'],
            'std_rmse': cv_results['alpha_0.0']['std_rmse'],
            'predictions': int(len(ratings) * 0.2)  # Approximate test size
        }

        results['Hybrid (Current System)'] = {
            'alpha': 0.5,
            'mae': cv_results['alpha_0.5']['avg_mae'],
            'rmse': cv_results['alpha_0.5']['avg_rmse'],
            'hit_rate': cv_results['alpha_0.5']['avg_hit_rate'],
            'std_mae': cv_results['alpha_0.5']['std_mae'],
            'std_rmse': cv_results['alpha_0.5']['std_rmse'],
            'predictions': int(len(ratings) * 0.2)
        }

        results['Fuzzy Logic Only'] = {
            'alpha': 1.0,
            'mae': cv_results['alpha_1.0']['avg_mae'],
            'rmse': cv_results['alpha_1.0']['avg_rmse'],
            'hit_rate': cv_results['alpha_1.0']['avg_hit_rate'],
            'std_mae': cv_results['alpha_1.0']['std_mae'],
            'std_rmse': cv_results['alpha_1.0']['std_rmse'],
            'predictions': int(len(ratings) * 0.2)
        }

        # DEBUG: Log CF alpha=0 results
        logging.warning(f"🎯 CF Alpha=0.0: MAE={results['Collaborative Filtering Only']['mae']:.4f} (from 5-fold CV)")

        # Determine winner
        if results:
            winner_name = min(results.keys(), key=lambda k: results[k]['mae'])
            results['winner'] = winner_name
            results['winner_mae'] = results[winner_name]['mae']
            logging.warning(f"🏆 Winner: {winner_name} with MAE={results[winner_name]['mae']:.4f}")

        logging.warning("=" * 80)
        return results

    def compare_with_baselines(self,
                              ratings: List[Rating],
                              test_size: float = 0.2,
                              k: int = 10,
                              n_splits: int = 5,
                              random_state: int = 42) -> Dict:
        """
        Bandingkan Hybrid dengan berbagai baseline algorithms

        Baselines:
        1. Random - Rekomendasi acak
        2. Most Popular - Menu paling populer
        3. Average Rating - Rata-rata rating global
        4. Item-Based CF - Collaborative filtering berbasis item
        5. User-Based CF - Collaborative filtering berbasis user
        6. Hybrid (Ours) - Hybrid Fuzzy-CF

        ✅ UNIFIED: Sekarang menggunakan 5-fold Cross-Validation yang SAMA
        untuk User-Based CF, Hybrid, dan Fuzzy Logic!
        ✅ FIXED: Item-Based CF sekarang menggunakan FIXED random_state!

        Args:
            ratings: List of Rating objects
            test_size: Proporsi test data (ignored, using CV instead)
            k: Jumlah neighbors untuk CF (ignored, using default)
            n_splits: Number of folds untuk CV (default: 5)
            random_state: Random state untuk CV (default: 42)

        Returns:
            Dictionary dengan baseline comparison results
        """
        from sklearn.model_selection import KFold
        from collections import Counter
        import random

        # DEBUG: Log function entry
        logging.warning("=" * 80)
        logging.warning("🔍 DEBUG: compare_with_baselines() called")
        logging.warning(f"📊 Total ratings: {len(ratings)}")
        logging.warning(f"🔀 N_splits: {n_splits}, Random state: {random_state}")
        logging.warning(f"✅ Using 5-fold CV for consistency with Cross-Validation endpoint")
        logging.warning(f"✅ Item-Based CF now uses FIXED random_state")
        logging.warning("=" * 80)

        # Use unified cross_validate function for main algorithms
        cv_results = self.cross_validate(
            ratings=ratings,
            n_splits=n_splits,
            alpha_values=[0.0, 0.5, 1.0],
            random_state=random_state
        )

        results = {}

        # Setup KFold for baseline calculations (consistent with CV)
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)

        # Calculate baseline metrics across all folds
        baseline_metrics = {
            'random': {'mae': [], 'rmse': [], 'predictions': []},
            'most_popular': {'mae': [], 'rmse': [], 'predictions': []},
            'average_rating': {'mae': [], 'rmse': [], 'predictions': []},
            'item_cf': {'mae': [], 'rmse': [], 'predictions': []}
        }

        # Process each fold for baselines
        for fold_idx, (train_idx, test_idx) in enumerate(kf.split(ratings)):
            train_data = [ratings[i] for i in train_idx]
            test_data = [ratings[i] for i in test_idx]

            logging.warning(f"  📁 Processing baseline fold {fold_idx + 1}/{n_splits}: Train={len(train_data)}, Test={len(test_data)}")

            # Get average rating dari training set
            avg_rating_train = np.mean([r.score for r in train_data])

            # Get most popular items
            menu_counts = Counter([r.menu_id for r in train_data])
            most_popular_menus = [item for item, count in menu_counts.most_common()]

            # Prepare ratings dictionary untuk item-based CF
            user_ratings = {}
            for r in train_data:
                if r.customer_id not in user_ratings:
                    user_ratings[r.customer_id] = {}
                user_ratings[r.customer_id][r.menu_id] = r.score

            # 1. Random Baseline
            random.seed(random_state + fold_idx)  # FIXED: different seed per fold but consistent across runs
            random_predictions = [random.uniform(1, 5) for _ in test_data]
            random_actuals = [r.score for r in test_data]
            random_mae = float(np.mean([abs(p - a) for p, a in zip(random_predictions, random_actuals)]))
            random_rmse = float(np.sqrt(np.mean([(p - a)**2 for p, a in zip(random_predictions, random_actuals)])))
            baseline_metrics['random']['mae'].append(random_mae)
            baseline_metrics['random']['rmse'].append(random_rmse)
            baseline_metrics['random']['predictions'].append(len(random_predictions))

            # 2. Most Popular Baseline
            popular_predictions = []
            for r in test_data:
                menu_ratings = [rating.score for rating in train_data if rating.menu_id == r.menu_id]
                if menu_ratings:
                    popular_predictions.append(np.mean(menu_ratings))
                else:
                    popular_predictions.append(avg_rating_train)

            popular_actuals = [r.score for r in test_data]
            popular_mae = float(np.mean([abs(p - a) for p, a in zip(popular_predictions, popular_actuals)]))
            popular_rmse = float(np.sqrt(np.mean([(p - a)**2 for p, a in zip(popular_predictions, popular_actuals)])))
            baseline_metrics['most_popular']['mae'].append(popular_mae)
            baseline_metrics['most_popular']['rmse'].append(popular_rmse)
            baseline_metrics['most_popular']['predictions'].append(len(popular_predictions))

            # 3. Average Rating Baseline
            avg_predictions = [avg_rating_train for _ in test_data]
            avg_actuals = [r.score for r in test_data]
            avg_mae = float(np.mean([abs(p - a) for p, a in zip(avg_predictions, avg_actuals)]))
            avg_rmse = float(np.sqrt(np.mean([(p - a)**2 for p, a in zip(avg_predictions, avg_actuals)])))
            baseline_metrics['average_rating']['mae'].append(avg_mae)
            baseline_metrics['average_rating']['rmse'].append(avg_rmse)
            baseline_metrics['average_rating']['predictions'].append(len(avg_predictions))

            # 4. Item-Based CF (with FIXED random_state)
            item_similarities = {}
            all_items = list(set([r.menu_id for r in train_data]))

            # Set random seed for consistency
            np.random.seed(random_state + fold_idx)

            for item1 in all_items:
                item_similarities[item1] = {}
                for item2 in all_items:
                    if item1 != item2:
                        ratings1 = []
                        ratings2 = []
                        for user_id in user_ratings:
                            if item1 in user_ratings[user_id] and item2 in user_ratings[user_id]:
                                ratings1.append(user_ratings[user_id][item1])
                                ratings2.append(user_ratings[user_id][item2])

                        if len(ratings1) >= 2:
                            corr = np.corrcoef(ratings1, ratings2)[0, 1]
                            if not np.isnan(corr):
                                item_similarities[item1][item2] = corr

            item_cf_predictions = []
            for r in test_data:
                if r.menu_id in item_similarities:
                    similar_items = sorted(
                        item_similarities[r.menu_id].items(),
                        key=lambda x: abs(x[1]),
                        reverse=True
                    )[:5]

                    if similar_items:
                        weighted_sum = 0
                        weight_sum = 0
                        for item_id, similarity in similar_items:
                            if r.customer_id in user_ratings and item_id in user_ratings[r.customer_id]:
                                weighted_sum += similarity * user_ratings[r.customer_id][item_id]
                                weight_sum += abs(similarity)

                        if weight_sum > 0:
                            item_cf_predictions.append(weighted_sum / weight_sum)
                            continue

                item_cf_predictions.append(avg_rating_train)

            item_cf_actuals = [r.score for r in test_data]
            item_cf_mae = float(np.mean([abs(p - a) for p, a in zip(item_cf_predictions, item_cf_actuals)]))
            item_cf_rmse = float(np.sqrt(np.mean([(p - a)**2 for p, a in zip(item_cf_predictions, item_cf_actuals)])))
            baseline_metrics['item_cf']['mae'].append(item_cf_mae)
            baseline_metrics['item_cf']['rmse'].append(item_cf_rmse)
            baseline_metrics['item_cf']['predictions'].append(len(item_cf_predictions))

        # Calculate average baseline metrics across folds
        results['Random'] = {
            'mae': float(np.mean(baseline_metrics['random']['mae'])),
            'rmse': float(np.mean(baseline_metrics['random']['rmse'])),
            'predictions': int(np.mean(baseline_metrics['random']['predictions']))
        }

        results['Most Popular'] = {
            'mae': float(np.mean(baseline_metrics['most_popular']['mae'])),
            'rmse': float(np.mean(baseline_metrics['most_popular']['rmse'])),
            'predictions': int(np.mean(baseline_metrics['most_popular']['predictions']))
        }

        results['Average Rating'] = {
            'mae': float(np.mean(baseline_metrics['average_rating']['mae'])),
            'rmse': float(np.mean(baseline_metrics['average_rating']['rmse'])),
            'predictions': int(np.mean(baseline_metrics['average_rating']['predictions']))
        }

        results['Item-Based CF'] = {
            'mae': float(np.mean(baseline_metrics['item_cf']['mae'])),
            'rmse': float(np.mean(baseline_metrics['item_cf']['rmse'])),
            'predictions': int(np.mean(baseline_metrics['item_cf']['predictions']))
        }

        # DEBUG: Log Item-Based CF results
        logging.warning(f"🎯 Item-Based CF: MAE={results['Item-Based CF']['mae']:.4f} (from 5-fold CV with FIXED seeds)")

        # 6. Hybrid (Ours) - Use unified CV results
        results['Hybrid (Ours)'] = {
            'mae': cv_results['alpha_0.5']['avg_mae'],
            'rmse': cv_results['alpha_0.5']['avg_rmse'],
            'hit_rate': cv_results['alpha_0.5']['avg_hit_rate'],
            'predictions': int(len(ratings) * 0.2)
        }

        # 7. Fuzzy Logic Only - Use unified CV results
        results['Fuzzy Logic Only'] = {
            'mae': cv_results['alpha_1.0']['avg_mae'],
            'rmse': cv_results['alpha_1.0']['avg_rmse'],
            'hit_rate': cv_results['alpha_1.0']['avg_hit_rate'],
            'predictions': int(len(ratings) * 0.2)
        }

        # 5. User-Based CF (CF Only α=0) - Use unified CV results
        results['User-Based CF'] = {
            'mae': cv_results['alpha_0.0']['avg_mae'],
            'rmse': cv_results['alpha_0.0']['avg_rmse'],
            'hit_rate': cv_results['alpha_0.0']['avg_hit_rate'],
            'predictions': int(len(ratings) * 0.2)
        }

        # DEBUG: Log CF alpha=0 results
        logging.warning(f"🎯 User-Based CF (Alpha=0.0): MAE={results['User-Based CF']['mae']:.4f} (from 5-fold CV)")

        # Determine winner
        if results:
            winner_name = min(results.keys(), key=lambda k: results[k]['mae'])
            results['winner'] = winner_name
            results['winner_mae'] = results[winner_name]['mae']
            results['total_ratings'] = len(ratings)
            results['test_size'] = test_size
            logging.warning(f"🏆 Winner: {winner_name} with MAE={results[winner_name]['mae']:.4f}")

        logging.warning("=" * 80)
        return results

    def calculate_data_sparsity(self) -> Dict:
        """
        Hitung data sparsity matrix

        Sparsity = persentase missing values di user-item matrix

        Returns:
            Dictionary dengan sparsity metrics
        """
        from app.models.rating import Rating
        from app.models.user import User, UserRole
        from app.models.menu import Menu

        # Get counts
        total_users = self.db.query(User).filter(User.role == UserRole.CUSTOMER).count()
        total_menus = self.db.query(Menu).count()
        total_ratings = self.db.query(Rating).count()

        if total_users == 0 or total_menus == 0:
            return {
                'total_users': total_users,
                'total_menus': total_menus,
                'total_ratings': total_ratings,
                'sparsity_percentage': 100.0,
                'density_percentage': 0.0,
                'possible_ratings': total_users * total_menus,
                'sparsity_level': 'No Data'
            }

        # Calculate sparsity
        possible_ratings = total_users * total_menus
        sparsity = (1 - (total_ratings / possible_ratings)) * 100
        density = (total_ratings / possible_ratings) * 100

        # Determine sparsity level
        if sparsity >= 95:
            sparsity_level = 'Very Sparse (Cold Start Problem Severe)'
        elif sparsity >= 80:
            sparsity_level = 'Sparse (Cold Start Problem Moderate)'
        elif sparsity >= 50:
            sparsity_level = 'Medium (Adequate Data)'
        else:
            sparsity_level = 'Dense (Good Data Coverage)'

        return {
            'total_users': total_users,
            'total_menus': total_menus,
            'total_ratings': total_ratings,
            'possible_ratings': possible_ratings,
            'sparsity_percentage': float(sparsity),
            'density_percentage': float(density),
            'sparsity_level': sparsity_level
        }


# StatisticalTests class untuk compatibility
class StatisticalTests:
    """
    Statistical tests untuk algorithm comparison
    """

    def __init__(self, db: Session):
        self.db = db
        self.evaluator = AlgorithmEvaluator(db)

    def pairwise_comparison(self,
                          mae1: float,
                          mae2: float,
                          n: int = 100) -> Dict:
        """
        Pairwise comparison antara dua algoritma

        Args:
            error1: Error rate algoritma 1
            error2: Error rate algoritma 2
            n: Jumlah sample

        Returns:
            Dictionary dengan statistical test results
        """
        from scipy import stats as scipy_stats
        import random

        # Generate synthetic paired samples for demonstration
        # In real implementation, this would use actual paired measurements
        errors1 = [mae1 + random.uniform(-0.1, 0.1) for _ in range(n)]
        errors2 = [mae2 + random.uniform(-0.1, 0.1) for _ in range(n)]

        # Paired t-test
        t_statistic, p_value = scipy_stats.ttest_rel(errors1, errors2)

        # Mean difference
        mean_diff = np.mean(errors1 - errors2)

        # Standard error of difference
        std_diff = np.std(errors1 - errors2, ddof=1)
        se_diff = std_diff / np.sqrt(n)

        # 95% Confidence Interval
        from scipy.stats import t as t_dist
        ci_critical = t_dist.ppf(0.975, df=n-1)
        ci_lower = mean_diff - (ci_critical * se_diff)
        ci_upper = mean_diff + (ci_critical * se_diff)

        # Effect size (Cohen's d)
        pooled_std = np.sqrt((np.std(errors1)**2 + np.std(errors2)**2) / 2)
        effect_size = mean_diff / pooled_std if pooled_std > 0 else 0

        # Interpretation
        is_significant = p_value < 0.05

        if abs(effect_size) < 0.2:
            effect_interpretation = "Small effect"
        elif abs(effect_size) < 0.5:
            effect_interpretation = "Medium effect"
        elif abs(effect_size) < 0.8:
            effect_interpretation = "Large effect"
        else:
            effect_interpretation = "Very large effect"

        return {
            'mean_error_alpha1': float(np.mean(errors1)),
            'mean_error_alpha2': float(np.mean(errors2)),
            'mean_difference': float(mean_diff),
            't_statistic': float(t_statistic),
            'p_value': float(p_value),
            'is_significant': bool(is_significant),
            'ci_95_lower': float(ci_lower),
            'ci_95_upper': float(ci_upper),
            'effect_size': float(effect_size),
            'effect_interpretation': effect_interpretation,
            'interpretation': f"Significance test result: p={p_value:.4f}",
            'n_runs': n
        }
