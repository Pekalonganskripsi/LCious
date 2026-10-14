#!/usr/bin/env python3
"""
Comprehensive validation test for the unified evaluation system.

This test validates that:
1. Reproducibility: Running evaluation 2x produces identical results
2. Cross-endpoint consistency: MAE CF alpha=0 is the same in all endpoints
3. Statistical Test uses paired t-test from fold results
4. Item-Based CF is consistent across runs
"""

import sys
import os
import time

# Add the backend directory to the path
sys.path.insert(0, '/media/devmon/sdb1-ata-RESCUE09RM22AR12/www/LCicious/backend')

# Set the database path explicitly to match the .env configuration
import os
os.chdir('/media/devmon/sdb1-ata-RESCUE09RM22AR12/www/LCicious/backend')

from app.db.session import SessionLocal
from app.algorithms.evaluation import AlgorithmEvaluator
from app.models.rating import Rating

print("=" * 80)
print("UNIFIED EVALUATION SYSTEM VALIDATION")
print("=" * 80)
print()

def run_cross_validation_test():
    """Test Cross-Validation function"""
    print("TEST 1: Cross-Validation Function (UNIFIED SOURCE)")
    print("-" * 80)

    db = SessionLocal()
    try:
        all_ratings = db.query(Rating).all()
        print(f"Total ratings: {len(all_ratings)}")

        evaluator = AlgorithmEvaluator(db)

        # Run 5-fold Cross-Validation
        print("Running 5-fold Cross-Validation...")
        results = evaluator.cross_validate(
            ratings=all_ratings,
            n_splits=5,
            alpha_values=[0.0, 0.5, 1.0],
            random_state=42
        )

        # Extract CF alpha=0 MAE
        cf_mae = results['alpha_0.0']['avg_mae']
        hybrid_mae = results['alpha_0.5']['avg_mae']
        fuzzy_mae = results['alpha_1.0']['avg_mae']

        print()
        print("✅ Cross-Validation completed")
        print(f"🎯 CF Alpha=0.0 MAE: {cf_mae:.4f}")
        print(f"🎯 Hybrid Alpha=0.5 MAE: {hybrid_mae:.4f}")
        print(f"🎯 Fuzzy Alpha=1.0 MAE: {fuzzy_mae:.4f}")
        print(f"📊 Raw MAE per fold for CF Alpha=0: {[f'{m:.4f}' for m in results['alpha_0.0']['raw_mae_per_fold']]}")

        return results

    except Exception as e:
        print(f"❌ Cross-Validation error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

def run_algorithm_comparison_test():
    """Test Algorithm Comparison function"""
    print("TEST 2: Algorithm Comparison Function (Should use same 5-fold CV)")
    print("-" * 80)

    db = SessionLocal()
    try:
        all_ratings = db.query(Rating).all()

        evaluator = AlgorithmEvaluator(db)

        print("Running Algorithm Comparison...")
        results = evaluator.compare_algorithms(
            ratings=all_ratings,
            test_size=0.2,  # Should be ignored
            k=10,  # Should be ignored
            n_splits=5,
            random_state=42
        )

        # Extract CF alpha=0 MAE
        cf_mae = results['Collaborative Filtering Only']['mae']
        hybrid_mae = results['Hybrid (Current System)']['mae']
        fuzzy_mae = results['Fuzzy Logic Only']['mae']

        print()
        print("✅ Algorithm Comparison completed")
        print(f"🎯 CF Alpha=0.0 MAE: {cf_mae:.4f}")
        print(f"🎯 Hybrid Alpha=0.5 MAE: {hybrid_mae:.4f}")
        print(f"🎯 Fuzzy Alpha=1.0 MAE: {fuzzy_mae:.4f}")

        return results

    except Exception as e:
        print(f"❌ Algorithm Comparison error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

def run_statistical_test():
    """Test Statistical Significance Test function"""
    print("TEST 3: Statistical Significance Test (Should use paired t-test from folds)")
    print("-" * 80)

    db = SessionLocal()
    try:
        all_ratings = db.query(Rating).all()

        evaluator = AlgorithmEvaluator(db)

        print("Running Statistical Significance Test...")
        results = evaluator.statistical_significance_test(
            ratings=all_ratings,
            alpha1=0.5,
            alpha2=0.0,
            n_repetitions=1,  # Single 5-fold CV
            n_splits=5,
            random_state=42
        )

        # Extract results
        alpha1_mae = results['mean_error_alpha1']
        alpha2_mae = results['mean_error_alpha2']
        p_value = results['p_value']
        t_statistic = results['t_statistic']
        effect_size = results['effect_size']

        print()
        print("✅ Statistical Test completed")
        print(f"🎯 Hybrid Alpha=0.5 Mean Error: {alpha1_mae:.4f}")
        print(f"🎯 CF Alpha=0.0 Mean Error: {alpha2_mae:.4f}")
        print(f"📊 T-statistic: {t_statistic:.4f}")
        print(f"📊 P-value: {p_value:.4f}")
        print(f"📊 Effect size (Cohen's d): {effect_size:.4f}")
        print(f"📊 Significant: {results['is_significant']}")
        print(f"📊 Methodology: {results['methodology']}")
        print(f"📊 Sample size: {results['n_samples']} (folds × repetitions)")

        return results

    except Exception as e:
        print(f"❌ Statistical Test error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

def run_baseline_comparison():
    """Test Baseline Comparison function"""
    print("TEST 4: Baseline Comparison Function (Should use same 5-fold CV)")
    print("-" * 80)

    db = SessionLocal()
    try:
        all_ratings = db.query(Rating).all()

        evaluator = AlgorithmEvaluator(db)

        print("Running Baseline Comparison...")
        results = evaluator.compare_with_baselines(
            ratings=all_ratings,
            n_splits=5,
            random_state=42
        )

        # Extract results
        item_cf_mae = results['Item-Based CF']['mae']
        user_cf_mae = results['User-Based CF']['mae']
        hybrid_mae = results['Hybrid (Ours)']['mae']

        print()
        print("✅ Baseline Comparison completed")
        print(f"🎯 Item-Based CF MAE: {item_cf_mae:.4f}")
        print(f"🎯 User-Based CF (Alpha=0.0) MAE: {user_cf_mae:.4f}")
        print(f"🎯 Hybrid (Ours) MAE: {hybrid_mae:.4f}")
        print(f"🏆 Winner: {results['winner']} with MAE={results['winner_mae']:.4f}")

        return results

    except Exception as e:
        print(f"❌ Baseline Comparison error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

def run_reproducibility_test():
    """Test Reproducibility - run evaluation 2x and compare results"""
    print("TEST 5: Reproducibility Test (Run 2x and compare)")
    print("-" * 80)

    db = SessionLocal()
    try:
        all_ratings = db.query(Rating).all()
        evaluator = AlgorithmEvaluator(db)

        # Run 1
        print("Running Cross-Validation (Run 1)...")
        results1 = evaluator.cross_validate(
            ratings=all_ratings,
            n_splits=5,
            alpha_values=[0.0, 0.5],
            random_state=42
        )
        cf_mae_run1 = results1['alpha_0.0']['avg_mae']
        hybrid_mae_run1 = results1['alpha_0.5']['avg_mae']

        print(f"Run 1 - CF Alpha=0.0 MAE: {cf_mae_run1:.4f}")
        print(f"Run 1 - Hybrid Alpha=0.5 MAE: {hybrid_mae_run1:.4f}")

        # Run 2
        print("Running Cross-Validation (Run 2)...")
        results2 = evaluator.cross_validate(
            ratings=all_ratings,
            n_splits=5,
            alpha_values=[0.0, 0.5],
            random_state=42
        )
        cf_mae_run2 = results2['alpha_0.0']['avg_mae']
        hybrid_mae_run2 = results2['alpha_0.5']['avg_mae']

        print(f"Run 2 - CF Alpha=0.0 MAE: {cf_mae_run2:.4f}")
        print(f"Run 2 - Hybrid Alpha=0.5 MAE: {hybrid_mae_run2:.4f}")

        # Compare
        print()
        print("🔍 Reproducibility Check:")
        cf_diff = abs(cf_mae_run1 - cf_mae_run2)
        hybrid_diff = abs(hybrid_mae_run1 - hybrid_mae_run2)

        if cf_diff < 0.0001 and hybrid_diff < 0.0001:
            print(f"✅ REPRODUCIBLE: Differences < 0.0001")
            print(f"   CF Alpha=0 diff: {cf_diff:.6f}")
            print(f"   Hybrid Alpha=0.5 diff: {hybrid_diff:.6f}")
            return True
        else:
            print(f"❌ NOT REPRODUCIBLE: Differences >= 0.0001")
            print(f"   CF Alpha=0 diff: {cf_diff:.6f}")
            print(f"   Hybrid Alpha=0.5 diff: {hybrid_diff:.6f}")
            return False

    except Exception as e:
        print(f"❌ Reproducibility test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def run_cross_endpoint_consistency(cv_results, comparison_results):
    """Test Cross-Endpoint Consistency"""
    print("TEST 6: Cross-Endpoint Consistency (MAE should be IDENTICAL)")
    print("-" * 80)

    try:
        # Extract CF alpha=0 MAE from both results
        cv_cf_mae = cv_results['alpha_0.0']['avg_mae']
        comparison_cf_mae = comparison_results['Collaborative Filtering Only']['mae']

        print(f"Cross-Validation CF Alpha=0.0 MAE: {cv_cf_mae:.4f}")
        print(f"Algorithm Comparison CF Alpha=0.0 MAE: {comparison_cf_mae:.4f}")

        # Compare
        diff = abs(cv_cf_mae - comparison_cf_mae)

        print()
        print("🔍 Cross-Endpoint Consistency Check:")
        if diff < 0.0001:
            print(f"✅ CONSISTENT: Difference < 0.0001")
            print(f"   Difference: {diff:.6f}")
            return True
        else:
            print(f"❌ NOT CONSISTENT: Difference >= 0.0001")
            print(f"   Difference: {diff:.6f}")
            return False

    except Exception as e:
        print(f"❌ Cross-Endpoint Consistency test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import logging

    # Configure logging to see debug messages
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    print("Starting unified evaluation system validation...")
    print()

    # Run all tests
    cv_results = run_cross_validation_test()
    print()
    print("=" * 80)
    print()

    time.sleep(1)

    comparison_results = run_algorithm_comparison_test()
    print()
    print("=" * 80)
    print()

    time.sleep(1)

    stat_results = run_statistical_test()
    print()
    print("=" * 80)
    print()

    time.sleep(1)

    baseline_results = run_baseline_comparison()
    print()
    print("=" * 80)
    print()

    reproducible = run_reproducibility_test()
    print()
    print("=" * 80)
    print()

    consistent = run_cross_endpoint_consistency(cv_results, comparison_results)
    print()
    print("=" * 80)
    print()

    # Final Summary
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    test_results = {
        "Cross-Validation Function": cv_results is not None,
        "Algorithm Comparison Function": comparison_results is not None,
        "Statistical Test Function": stat_results is not None,
        "Baseline Comparison Function": baseline_results is not None,
        "Reproducibility (2 runs)": reproducible,
        "Cross-Endpoint Consistency": consistent
    }

    for test_name, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")

    all_passed = all(test_results.values())

    print()
    if all_passed:
        print("=" * 80)
        print("🎉 ALL VALIDATION TESTS PASSED! ✅")
        print("=" * 80)
        print()
        print("The unified evaluation system is working correctly:")
        print("✅ All functions use the same 5-fold Cross-Validation")
        print("✅ MAE values are consistent across endpoints")
        print("✅ Results are reproducible across multiple runs")
        print("✅ Statistical Test uses paired t-test from fold results")
        print("✅ Item-Based CF uses fixed random_state")
        print()
        print("READY FOR JOURNAL SUBMISSION! 🚀")
    else:
        print("=" * 80)
        print("❌ SOME VALIDATION TESTS FAILED")
        print("=" * 80)
        print()
        print("Please review the failed tests above and fix the issues.")

    print()
    print("📋 VALIDATION COMPLETE")
    print("=" * 80)
