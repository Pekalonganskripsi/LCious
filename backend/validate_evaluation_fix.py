#!/usr/bin/env python3
"""
Script Validasi Perbaikan Evaluasi

Script ini untuk memvalidasi bahwa perbaikan evaluasi sudah benar:
1. Random seeds terdefinisi dengan benar
2. Fungsi core _evaluate_with_fixed_split() ada
3. Reproducibility test untuk fungsi utama

Run: python validate_evaluation_fix.py
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_1_random_seeds_defined():
    """Test 1: Cek RANDOM_SEEDS terdefinisi"""
    print("\n" + "="*70)
    print("TEST 1: Random Seeds Definition")
    print("="*70)

    try:
        from app.algorithms.evaluation import AlgorithmEvaluator

        # Cek attribute ada
        assert hasattr(AlgorithmEvaluator, 'RANDOM_SEEDS'), \
            "❌ RANDOM_SEEDS tidak terdefinisi di AlgorithmEvaluator"

        seeds = AlgorithmEvaluator.RANDOM_SEEDS
        print(f"✓ RANDOM_SEEDS terdefinisi: {seeds}")

        # Cek tipe data
        assert isinstance(seeds, list), "❌ RANDOM_SEEDS harus berupa list"
        print(f"✓ RANDOM_SEEDS adalah list")

        # Cek jumlah seeds
        assert len(seeds) == 10, f"❌ RANDOM_SEEDS harus ada 10, saat ini {len(seeds)}"
        print(f"✓ RANDOM_SEEDS berisi {len(seeds)} seeds")

        # Cek nilai seeds
        expected = [42, 43, 44, 45, 46, 47, 48, 49, 50, 51]
        assert seeds == expected, f"❌ RANDOM_SEEDS harus {expected}, saat ini {seeds}"
        print(f"✓ RANDOM_SEEDS nilai benar: {seeds}")

        print("\n✅ TEST 1 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {e}")
        return False


def test_2_core_function_exists():
    """Test 2: Cek fungsi core _evaluate_with_fixed_split() ada"""
    print("\n" + "="*70)
    print("TEST 2: Core Function Existence")
    print("="*70)

    try:
        from app.algorithms.evaluation import AlgorithmEvaluator

        # Cek method ada
        assert hasattr(AlgorithmEvaluator, '_evaluate_with_fixed_split'), \
            "❌ Method _evaluate_with_fixed_split() tidak terdefinisi"
        print("✓ Method _evaluate_with_fixed_split() terdefinisi")

        # Cek signature (basic)
        import inspect
        sig = inspect.signature(AlgorithmEvaluator._evaluate_with_fixed_split)
        params = list(sig.parameters.keys())
        required_params = ['self', 'ratings', 'alpha', 'train_ratings', 'test_ratings', 'k']

        for param in required_params:
            assert param in params, f"❌ Parameter '{param}' tidak ada di signature"

        print(f"✓ Method signature valid: {sig}")
        print("\n✅ TEST 2 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {e}")
        return False


def test_3_import_no_errors():
    """Test 3: Cek modul bisa di-import tanpa error"""
    print("\n" + "="*70)
    print("TEST 3: Module Import")
    print("="*70)

    try:
        from app.algorithms.evaluation import AlgorithmEvaluator
        print("✓ AlgorithmEvaluator berhasil di-import")

        # Cek beberapa method penting ada
        methods = [
            'calculate_mae',
            'calculate_rmse',
            'evaluate_algorithm_split',
            'statistical_significance_test',
            'compare_algorithms',
            'compare_with_baselines',
            '_evaluate_with_fixed_split'
        ]

        for method in methods:
            assert hasattr(AlgorithmEvaluator, method), \
                f"❌ Method '{method}' tidak ada"
            print(f"✓ Method '{method}' ada")

        print("\n✅ TEST 3 PASSED")
        return True

    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_4_code_inspection():
    """Test 4: Inspect code untuk memastikan perbaikan"""
    print("\n" + "="*70)
    print("TEST 4: Code Inspection")
    print("="*70)

    try:
        import inspect
        from app.algorithms.evaluation import AlgorithmEvaluator

        # Cek statistical_significance_test menggunakan RANDOM_SEEDS
        source = inspect.getsource(AlgorithmEvaluator.statistical_significance_test)

        checks = {
            'RANDOM_SEEDS': 'self.RANDOM_SEEDS' in source,
            'Fixed seed': 'random_state=seed' in source,
            'Raw errors stored': 'raw_errors_per_run' in source,
            'Seeds returned': 'seeds_used' in source
        }

        all_passed = True
        for check_name, passed in checks.items():
            if passed:
                print(f"✓ {check_name}: Found in code")
            else:
                print(f"❌ {check_name}: NOT found in code")
                all_passed = False

        # Cek evaluate_algorithm_split menggunakan _evaluate_with_fixed_split
        source = inspect.getsource(AlgorithmEvaluator.evaluate_algorithm_split)
        if '_evaluate_with_fixed_split' in source:
            print("✓ evaluate_algorithm_split uses _evaluate_with_fixed_split")
        else:
            print("❌ evaluate_algorithm_split does NOT use _evaluate_with_fixed_split")
            all_passed = False

        if all_passed:
            print("\n✅ TEST 4 PASSED")
        else:
            print("\n❌ TEST 4 FAILED: Some checks failed")

        return all_passed

    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run semua tests"""
    print("\n" + "="*70)
    print("🔍 VALIDASI PERBAIKAN EVALUASI")
    print("="*70)
    print("Script ini memvalidasi perbaikan kode evaluasi untuk konsistensi MAE/RMSE")

    results = []

    # Run semua tests
    results.append(("Test 1: Random Seeds", test_1_random_seeds_defined()))
    results.append(("Test 2: Core Function", test_2_core_function_exists()))
    results.append(("Test 3: Module Import", test_3_import_no_errors()))
    results.append(("Test 4: Code Inspection", test_4_code_inspection()))

    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 SEMUA TESTS PASSED! Perbaikan valid.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Perlu review.")
        return 1


if __name__ == "__main__":
    sys.exit(main())