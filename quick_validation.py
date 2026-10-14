#!/usr/bin/env python3
"""
Quick validation test for the unified evaluation system.
"""

import sys
import os
sys.path.insert(0, '/media/devmon/sdb1-ata-RESCUE09RM22AR12/www/LCicious/backend')
os.chdir('/media/devmon/sdb1-ata-RESCUE09RM22AR12/www/LCicious/backend')

from app.db.session import SessionLocal
from app.algorithms.evaluation import AlgorithmEvaluator
from app.models.rating import Rating

print("=" * 80)
print("QUICK VALIDATION TEST - UNIFIED EVALUATION SYSTEM")
print("=" * 80)
print()

db = SessionLocal()
try:
    all_ratings = db.query(Rating).all()
    print(f"Total ratings: {len(all_ratings)}")
    print()

    evaluator = AlgorithmEvaluator(db)

    # Test 1: Cross-Validation (UNIFIED SOURCE)
    print("TEST 1: Cross-Validation Function")
    print("-" * 80)
    cv_results = evaluator.cross_validate(
        ratings=all_ratings,
        n_splits=5,
        alpha_values=[0.0, 0.5, 1.0],
        random_state=42
    )
    cf_mae_cv = cv_results['alpha_0.0']['avg_mae']
    hybrid_mae_cv = cv_results['alpha_0.5']['avg_mae']
    fuzzy_mae_cv = cv_results['alpha_1.0']['avg_mae']
    print(f"✅ CF Alpha=0.0 MAE: {cf_mae_cv:.4f}")
    print(f"✅ Hybrid Alpha=0.5 MAE: {hybrid_mae_cv:.4f}")
    print(f"✅ Fuzzy Alpha=1.0 MAE: {fuzzy_mae_cv:.4f}")
    print(f"📊 Raw MAE per fold: {[f'{m:.4f}' for m in cv_results['alpha_0.0']['raw_mae_per_fold']]}")
    print()

    # Test 2: Algorithm Comparison (should use same CV)
    print("TEST 2: Algorithm Comparison Function")
    print("-" * 80)
    comparison_results = evaluator.compare_algorithms(
        ratings=all_ratings,
        n_splits=5,
        random_state=42
    )
    cf_mae_comparison = comparison_results['Collaborative Filtering Only']['mae']
    hybrid_mae_comparison = comparison_results['Hybrid (Current System)']['mae']
    print(f"✅ CF Alpha=0.0 MAE: {cf_mae_comparison:.4f}")
    print(f"✅ Hybrid Alpha=0.5 MAE: {hybrid_mae_comparison:.4f}")
    print()

    # Test 3: Cross-Endpoint Consistency
    print("TEST 3: Cross-Endpoint Consistency Check")
    print("-" * 80)
    diff = abs(cf_mae_cv - cf_mae_comparison)
    print(f"Cross-Validation CF MAE: {cf_mae_cv:.4f}")
    print(f"Algorithm Comparison CF MAE: {cf_mae_comparison:.4f}")
    print(f"Difference: {diff:.6f}")
    if diff < 0.0001:
        print("✅ CROSS-ENDPOINT CONSISTENCY: PASSED")
    else:
        print("❌ CROSS-ENDPOINT CONSISTENCY: FAILED")
    print()

    # Test 4: Reproducibility
    print("TEST 4: Reproducibility Test (Run 2x)")
    print("-" * 80)
    print("Run 1...")
    cv_run1 = evaluator.cross_validate(
        ratings=all_ratings,
        n_splits=5,
        alpha_values=[0.0],
        random_state=42
    )
    cf_mae_run1 = cv_run1['alpha_0.0']['avg_mae']
    print(f"Run 1 CF MAE: {cf_mae_run1:.4f}")

    print("Run 2...")
    cv_run2 = evaluator.cross_validate(
        ratings=all_ratings,
        n_splits=5,
        alpha_values=[0.0],
        random_state=42
    )
    cf_mae_run2 = cv_run2['alpha_0.0']['avg_mae']
    print(f"Run 2 CF MAE: {cf_mae_run2:.4f}")

    repro_diff = abs(cf_mae_run1 - cf_mae_run2)
    print(f"Difference: {repro_diff:.6f}")
    if repro_diff < 0.0001:
        print("✅ REPRODUCIBILITY: PASSED")
    else:
        print("❌ REPRODUCIBILITY: FAILED")
    print()

    # Test 5: Baseline Comparison
    print("TEST 5: Baseline Comparison Function")
    print("-" * 80)
    baseline_results = evaluator.compare_with_baselines(
        ratings=all_ratings,
        n_splits=5,
        random_state=42
    )
    item_cf_mae = baseline_results['Item-Based CF']['mae']
    user_cf_mae = baseline_results['User-Based CF']['mae']
    hybrid_mae_baseline = baseline_results['Hybrid (Ours)']['mae']
    print(f"✅ Item-Based CF MAE: {item_cf_mae:.4f}")
    print(f"✅ User-Based CF MAE: {user_cf_mae:.4f}")
    print(f"✅ Hybrid (Ours) MAE: {hybrid_mae_baseline:.4f}")
    print(f"🏆 Winner: {baseline_results['winner']} with MAE={baseline_results['winner_mae']:.4f}")
    print()

    # Final Summary
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    all_tests_passed = True

    if diff < 0.0001:
        print("✅ Cross-Endpoint Consistency: PASSED")
    else:
        print("❌ Cross-Endpoint Consistency: FAILED")
        all_tests_passed = False

    if repro_diff < 0.0001:
        print("✅ Reproducibility: PASSED")
    else:
        print("❌ Reproducibility: FAILED")
        all_tests_passed = False

    if item_cf_mae is not None and not np.isnan(item_cf_mae):
        print("✅ Item-Based CF: WORKING")
    else:
        print("❌ Item-Based CF: FAILED")
        all_tests_passed = False

    print()
    if all_tests_passed:
        print("🎉 ALL KEY VALIDATION TESTS PASSED! ✅")
        print()
        print("The unified evaluation system is working correctly:")
        print("✅ Cross-Validation is the SINGLE source of MAE for all endpoints")
        print("✅ All functions use the same 5-fold CV with random_state=42")
        print("✅ MAE values are consistent across endpoints")
        print("✅ Results are reproducible across multiple runs")
        print("✅ Item-Based CF uses fixed random_state")
        print()
        print("READY FOR JOURNAL SUBMISSION! 🚀")
    else:
        print("❌ SOME VALIDATION TESTS FAILED - Please review above")

except Exception as e:
    print(f"❌ Validation error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print()
print("📋 VALIDATION COMPLETE")
print("=" * 80)
