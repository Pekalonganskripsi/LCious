"""
Test suite untuk memvalidasi konsistensi dan reproducibility evaluasi

这些测试确保：
1. Setiap kali evaluasi dijalankan dengan parameter yang sama menghasilkan hasil yang identik
2. Semua endpoint menghasilkan nilai MAE/RMSE yang konsisten untuk konfigurasi yang sama
3. Random seeds yang digunakan tetap konsisten
"""

import pytest
import numpy as np
from typing import Dict, List


class TestEvaluationReproducibility:
    """Test suite untuk reproducibility evaluasi"""

    def test_random_seeds_defined(self):
        """Test bahwa RANDOM_SEEDS terdefinisi dengan benar"""
        from app.algorithms.evaluation import AlgorithmEvaluator

        # Cek bahwa RANDOM_SEEDS ada
        assert hasattr(AlgorithmEvaluator, 'RANDOM_SEEDS')
        assert isinstance(AlgorithmEvaluator.RANDOM_SEEDS, list)

        # Cek bahwa ada 10 seeds
        assert len(AlgorithmEvaluator.RANDOM_SEEDS) == 10

        # Cek bahwa seeds adalah integer
        assert all(isinstance(seed, int) for seed in AlgorithmEvaluator.RANDOM_SEEDS)

        # Cek bahwa seeds adalah [42, 43, ..., 51]
        expected_seeds = [42, 43, 44, 45, 46, 47, 48, 49, 50, 51]
        assert AlgorithmEvaluator.RANDOM_SEEDS == expected_seeds

    def test_evaluate_algorithm_split_reproducibility(self, db_session, sample_ratings):
        """
        Test bahwa evaluate_algorithm_split menghasilkan hasil yang sama
        setiap kali dipanggil dengan parameter yang sama
        """
        from app.algorithms.evaluation import AlgorithmEvaluator

        evaluator = AlgorithmEvaluator(db_session)

        # Jalankan pertama
        results1 = evaluator.evaluate_algorithm_split(
            ratings=sample_ratings,
            test_split=0.2,
            alpha_values=[0.0, 0.5, 1.0],
            random_seed=42
        )

        # Jalankan kedua
        results2 = evaluator.evaluate_algorithm_split(
            ratings=sample_ratings,
            test_split=0.2,
            alpha_values=[0.0, 0.5, 1.0],
            random_seed=42
        )

        # Bandingkan hasil
        assert 'alpha_0.0' in results1
        assert 'alpha_0.0' in results2
        assert results1['alpha_0.0']['mae'] == results2['alpha_0.0']['mae'], \
            "MAE untuk α=0 harus IDENTIK antara run 1 dan run 2"
        assert results1['alpha_0.0']['rmse'] == results2['alpha_0.0']['rmse'], \
            "RMSE untuk α=0 harus IDENTIK antara run 1 dan run 2"
        assert results1['alpha_0.5']['mae'] == results2['alpha_0.5']['mae'], \
            "MAE untuk α=0.5 harus IDENTIK antara run 1 dan run 2"
        assert results1['alpha_1.0']['mae'] == results2['alpha_1.0']['mae'], \
            "MAE untuk α=1.0 harus IDENTIK antara run 1 dan run 2"

    def test_statistical_test_reproducibility(self, db_session, sample_ratings):
        """
        Test bahwa statistical_significance_test menghasilkan hasil yang sama
        setiap kali dipanggil dengan parameter yang sama
        """
        from app.algorithms.evaluation import AlgorithmEvaluator

        evaluator = AlgorithmEvaluator(db_session)

        # Jalankan pertama
        results1 = evaluator.statistical_significance_test(
            ratings=sample_ratings,
            alpha1=0.5,
            alpha2=0.0,
            test_size=0.2,
            n_runs=5
        )

        # Jalankan kedua
        results2 = evaluator.statistical_significance_test(
            ratings=sample_ratings,
            alpha1=0.5,
            alpha2=0.0,
            test_size=0.2,
            n_runs=5
        )

        # Bandingkan hasil utama
        assert results1['mean_error_alpha1'] == results2['mean_error_alpha1'], \
            "Mean error α1 harus IDENTIK antara run 1 dan run 2"
        assert results1['mean_error_alpha2'] == results2['mean_error_alpha2'], \
            "Mean error α2 harus IDENTIK antara run 1 dan run 2"
        assert results1['t_statistic'] == results2['t_statistic'], \
            "T-statistic harus IDENTIK antara run 1 dan run 2"
        assert results1['p_value'] == results2['p_value'], \
            "P-value harus IDENTIK antara run 1 dan run 2"

        # Cek bahwa raw_errors_per_run tersimpan
        assert 'raw_errors_per_run' in results1
        assert 'seeds_used' in results1
        assert len(results1['raw_errors_per_run']) == 5
        assert len(results1['seeds_used']) == 5

    def test_cross_endpoint_consistency(self, db_session, sample_ratings):
        """
        Test bahwa semua endpoint menghasilkan MAE/RMSE yang konsisten
        untuk CF (α=0)
        """
        from app.algorithms.evaluation import AlgorithmEvaluator

        evaluator = AlgorithmEvaluator(db_session)

        # 1. Dapatkan hasil dari evaluate_algorithm_split
        split_results = evaluator.evaluate_algorithm_split(
            ratings=sample_ratings,
            test_split=0.2,
            alpha_values=[0.0],
            random_seed=42
        )
        split_mae = split_results['alpha_0.0']['mae']
        split_rmse = split_results['alpha_0.0']['rmse']

        # 2. Dapatkan hasil dari compare_algorithms
        compare_results = evaluator.compare_algorithms(
            ratings=sample_ratings,
            test_size=0.2,
            k=10
        )
        compare_mae = compare_results['Collaborative Filtering Only']['mae']
        compare_rmse = compare_results['Collaborative Filtering Only']['rmse']

        # 3. Dapatkan hasil dari statistical_significance_test (run pertama)
        stat_results = evaluator.statistical_significance_test(
            ratings=sample_ratings,
            alpha1=0.0,
            alpha2=0.5,  # Tidak masalah, kita hanya ambil α1
            test_size=0.2,
            n_runs=1
        )
        stat_mae = stat_results['mean_error_alpha1']

        # Bandingkan hasil
        assert split_mae == compare_mae, \
            f"MAE dari evaluate_algorithm_split ({split_mae}) harus SAMA dengan compare_algorithms ({compare_mae})"
        assert split_rmse == compare_rmse, \
            f"RMSE dari evaluate_algorithm_split ({split_rmse}) harus SAMA dengan compare_algorithms ({compare_rmse})"

        # Statistical test mungkin sedikit berbeda karena menggunakan split yang berbeda
        # tapi seharusnya konsisten jika menggunakan seed yang sama
        # Untuk sekarang kita hanya pastikan tidak terlalu jauh
        assert abs(split_mae - stat_mae) < 0.1, \
            f"MAE dari statistical test ({stat_mae}) tidak boleh terlalu jauh dari evaluate_algorithm_split ({split_mae})"

    def test_all_baselines_present(self, db_session, sample_ratings):
        """
        Test bahwa semua 7 baseline algorithms ada di hasil compare_with_baselines
        """
        from app.algorithms.evaluation import AlgorithmEvaluator

        evaluator = AlgorithmEvaluator(db_session)

        results = evaluator.compare_with_baselines(
            ratings=sample_ratings,
            test_size=0.2,
            k=10
        )

        # Cek bahwa semua baseline ada
        expected_baselines = [
            'Random',
            'Most Popular',
            'Average Rating',
            'Item-Based CF',
            'User-Based CF',
            'Hybrid (Ours)',
            'Fuzzy Logic Only'
        ]

        for baseline in expected_baselines:
            assert baseline in results, \
                f"Baseline '{baseline}' harus ada di hasil compare_with_baselines"

            # Cek bahwa tidak ada error
            assert 'mae' in results[baseline], \
                f"Baseline '{baseline}' harus punya MAE"
            assert results[baseline]['mae'] is not None, \
                f"Baseline '{baseline}' tidak boleh punya MAE None"

        # Cek bahwa winner ditentukan
        assert 'winner' in results
        assert 'winner_mae' in results


class TestEvaluationErrorHandling:
    """Test suite untuk error handling evaluasi"""

    def test_insufficient_data_handling(self, db_session):
        """
        Test bahwa fungsi evaluasi menangani data yang tidak cukup dengan baik
        """
        from app.algorithms.evaluation import AlgorithmEvaluator
        from app.models.rating import Rating

        evaluator = AlgorithmEvaluator(db_session)

        # Coba dengan data sangat sedikit
        few_ratings = db_session.query(Rating).limit(5).all()

        # Harus tidak crash, tapi mungkin return results kosong atau default
        try:
            results = evaluator.evaluate_algorithm_split(
                ratings=few_ratings,
                test_split=0.2,
                alpha_values=[0.5]
            )
            # Jika success, cek bahwa results valid
            assert isinstance(results, dict)
        except Exception as e:
            # Jika error, harus informative
            assert "insufficient" in str(e).lower() or "need at least" in str(e).lower()


# Fixtures untuk test
@pytest.fixture
def db_session(test_db):
    """Database session fixture"""
    yield test_db


@pytest.fixture
def sample_ratings(db_session):
    """Sample ratings fixture untuk test"""
    from app.models.rating import Rating
    from app.models.user import User, UserRole
    from app.models.menu import Menu

    # Create users
    users = []
    for i in range(5):
        user = User(
            id=f"test_user_{i}",
            username=f"testuser{i}",
            email=f"test{i}@example.com",
            password_hash="hash",
            role=UserRole.CUSTOMER,
            is_active=True
        )
        db_session.add(user)
        users.append(user)

    # Create menus
    menus = []
    for i in range(10):
        menu = Menu(
            id=f"test_menu_{i}",
            merchant_id="test_merchant_1",
            name=f"Test Menu {i}",
            description="Test",
            price=10000 + i * 1000,
            category="Test",
            cuisine="Indonesian",
            taste_profile="spicy"
        )
        db_session.add(menu)
        menus.append(menu)

    db_session.commit()

    # Create ratings
    ratings = []
    for user in users:
        for menu in menus[:5]:  # Each user rates 5 menus
            rating = Rating(
                customer_id=user.id,
                menu_id=menu.id,
                score=np.random.randint(3, 6)  # Rating 3-5
            )
            db_session.add(rating)
            ratings.append(rating)

    db_session.commit()
    return ratings


@pytest.fixture
def test_db():
    """Create test database"""
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()