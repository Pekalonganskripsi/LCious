#!/usr/bin/env python3
"""
Direct test script to call evaluation functions and capture debug logs.

This script directly tests the evaluation functions without needing API authentication.
It tests:
1. Cross-validation function
2. Algorithm comparison function
3. Statistical test function
4. Baseline comparison function
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, '/media/devmon/sdb1-ata-RESCUE09RM22AR12/www/LCicious/backend')

from app.db.session import SessionLocal
from app.algorithms.evaluation import AlgorithmEvaluator
from app.models.rating import Rating

# Set the database path explicitly to match the .env configuration
import os
os.chdir('/media/devmon/sdb1-ata-RESCUE09RM22AR12/www/LCicious/backend')

print("=" * 80)
print("EVALUATION DEBUG TEST - Testing all evaluation functions")
print("=" * 80)
print()

def test_cross_validation():
    """Test 1: Cross-validation function"""
    print("TEST 1: Cross-Validation Function")
    print("-" * 80)

    db = SessionLocal()
    try:
        # Get all ratings
        all_ratings = db.query(Rating).all()
        print(f"Total ratings: {len(all_ratings)}")
        print()

        # Create evaluator
        evaluator = AlgorithmEvaluator(db)

        # Run cross-validation
        print("Running cross-validation with alpha values [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]...")
        results = evaluator.cross_validate(
            ratings=all_ratings,
            n_splits=5,
            alpha_values=[0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]
        )

        print()
        print("✅ Cross-Validation completed")

        # Extract CF alpha=0 MAE
        if 'alpha_0.0' in results:
            cf_mae = results['alpha_0.0']['avg_mae']
            cf_std = results['alpha_0.0']['std_mae']
            print(f"🎯 CF Alpha=0.0 MAE: {cf_mae:.4f} (std: {cf_std:.4f})")
            print(f"📊 Raw MAE values: {results['alpha_0.0']}")

    except Exception as e:
        print(f"❌ Cross-Validation error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

    print()
    print("=" * 80)
    print()

def test_algorithm_comparison():
    """Test 2: Algorithm comparison function"""
    print("TEST 2: Algorithm Comparison Function")
    print("-" * 80)

    db = SessionLocal()
    try:
        # Get all ratings
        all_ratings = db.query(Rating).all()
        print(f"Total ratings: {len(all_ratings)}")
        print()

        # Create evaluator
        evaluator = AlgorithmEvaluator(db)

        # Run algorithm comparison
        print("Running algorithm comparison...")
        results = evaluator.compare_algorithms(
            ratings=all_ratings,
            test_size=0.2,
            k=10
        )

        print()
        print("✅ Algorithm Comparison completed")

        # Extract CF alpha=0 MAE
        if 'Collaborative Filtering Only' in results:
            cf_mae = results['Collaborative Filtering Only']['mae']
            print(f"🎯 CF Alpha=0.0 MAE: {cf_mae:.4f}")
            print(f"📊 Results: {results['Collaborative Filtering Only']}")

    except Exception as e:
        print(f"❌ Algorithm Comparison error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

    print()
    print("=" * 80)
    print()

def test_statistical_test():
    """Test 3: Statistical test function"""
    print("TEST 3: Statistical Test Function")
    print("-" * 80)

    db = SessionLocal()
    try:
        # Get all ratings
        all_ratings = db.query(Rating).all()
        print(f"Total ratings: {len(all_ratings)}")
        print()

        # Create evaluator
        evaluator = AlgorithmEvaluator(db)

        # Run statistical test
        print("Running statistical test with alpha1=0.5, alpha2=0.0, n_runs=10...")
        results = evaluator.statistical_significance_test(
            ratings=all_ratings,
            alpha1=0.5,
            alpha2=0.0,
            test_size=0.2,
            n_runs=10
        )

        print()
        print("✅ Statistical Test completed")

        # Extract CF alpha=0 MAE
        if 'mean_error_alpha2' in results:
            cf_mae = results['mean_error_alpha2']
            print(f"🎯 CF Alpha=0.0 Mean Error: {cf_mae:.4f}")
            print(f"📊 Alpha1 MAE: {results['mean_error_alpha1']:.4f}")
            print(f"📊 Seeds used: {results['seeds_used']}")

    except Exception as e:
        print(f"❌ Statistical Test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

    print()
    print("=" * 80)
    print()

def test_baseline_comparison():
    """Test 4: Baseline comparison function"""
    print("TEST 4: Baseline Comparison Function")
    print("-" * 80)

    db = SessionLocal()
    try:
        # Get all ratings
        all_ratings = db.query(Rating).all()
        print(f"Total ratings: {len(all_ratings)}")
        print()

        # Create evaluator
        evaluator = AlgorithmEvaluator(db)

        # Run baseline comparison
        print("Running baseline comparison...")
        results = evaluator.compare_with_baselines(
            ratings=all_ratings,
            test_size=0.2,
            k=10
        )

        print()
        print("✅ Baseline Comparison completed")

        # Extract Item-Based CF and User-Based CF MAE
        if 'Item-Based CF' in results:
            item_cf_mae = results['Item-Based CF']['mae']
            print(f"🎯 Item-Based CF MAE: {item_cf_mae:.4f}")

        if 'User-Based CF' in results:
            user_cf_mae = results['User-Based CF']['mae']
            print(f"🎯 User-Based CF (Alpha=0.0) MAE: {user_cf_mae:.4f}")
            print(f"📊 Results: {results['User-Based CF']}")

    except Exception as e:
        print(f"❌ Baseline Comparison error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

    print()
    print("=" * 80)
    print()

def test_baseline_metrics():
    """Test 5: Baseline metrics function"""
    print("TEST 5: Baseline Metrics Function")
    print("-" * 80)

    db = SessionLocal()
    try:
        # Get all ratings
        all_ratings = db.query(Rating).all()
        print(f"Total ratings: {len(all_ratings)}")
        print()

        # Create evaluator
        evaluator = AlgorithmEvaluator(db)

        # Run baseline metrics
        print("Running baseline metrics calculation...")
        results = evaluator.calculate_baseline_metrics(
            ratings=all_ratings,
            test_size=0.2
        )

        print()
        print("✅ Baseline Metrics completed")

        # Extract Item-Based CF MAE
        if 'item_cf' in results and results['item_cf']['mae'] is not None:
            item_cf_mae = results['item_cf']['mae']
            print(f"🎯 Item-Based CF MAE: {item_cf_mae:.4f}")
            print(f"📊 Results: {results['item_cf']}")
        else:
            print(f"❌ Item-Based CF failed: {results['item_cf'].get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Baseline Metrics error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

    print()
    print("=" * 80)
    print()

if __name__ == "__main__":
    import logging

    # Configure logging to see debug messages
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    print("Starting direct evaluation tests...")
    print()

    # Run tests
    test_cross_validation()
    import time
    time.sleep(1)

    test_algorithm_comparison()
    time.sleep(1)

    test_statistical_test()
    time.sleep(1)

    test_baseline_comparison()
    time.sleep(1)

    test_baseline_metrics()

    print("All tests completed!")
    print()
    print("📋 Check the output above for:")
    print("   🔍 DEBUG: [function_name]() called")
    print("   🎯 CF Alpha=0.0 results")
    print("   ✅ _evaluate_with_fixed_split() result")
    print("   ⚠️  Item-Based CF has its own implementation")
    print()
    print("🔍 ROOT CAUSE ANALYSIS:")
    print("   Compare the MAE values for CF Alpha=0.0 across all tests")
    print("   - Cross-Validation MAE: ____")
    print("   - Algorithm Comparison MAE: ____")
    print("   - Statistical Test MAE: ____")
    print("   - Baseline Comparison User-Based CF MAE: ____")
    print()
    print("   If these values are different, the functions are NOT using the same")
    print("   train/test split or random seeds!")
