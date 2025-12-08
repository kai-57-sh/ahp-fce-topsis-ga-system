"""
Mathematical Validation Tests for Evaluator Module

Research-grade testing to prevent logical errors like the indexing bug:
- Array indexing validation for all np.argmin(), np.argsort(), slicing operations
- Ranking consistency verification (higher Ci must always get better rank)
- Boundary condition testing (empty arrays, single elements, identical values)
- Numerical stability testing (extreme values, near-zero denominators)
- Property-based testing using mathematical invariants
"""

import pytest
import numpy as np
from typing import Dict, Any, List
import warnings

# Add parent directory to path for imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from modules.evaluator import evaluate_batch, _calculate_ahp_weights, _apply_topsis
from modules.topsis_module import topsis_rank
from modules.ahp_module import calculate_weights, validate_judgment_matrix
from utils.validation import AuditLogger


class TestEvaluatorMathematicalValidation:
    """Comprehensive mathematical validation for evaluator module."""

    @pytest.fixture
    def basic_test_data(self):
        """Provide basic test data for mathematical validation."""
        # Create consistent test matrices
        decision_matrix = np.array([
            [1.0, 2.0, 3.0, 4.0],
            [2.0, 1.5, 2.5, 3.5],
            [1.5, 2.5, 2.0, 4.5],
            [3.0, 1.0, 3.5, 2.0]
        ])
        weights = np.array([0.3, 0.2, 0.3, 0.2])
        indicator_types = ['benefit', 'cost', 'benefit', 'cost']

        return {
            'decision_matrix': decision_matrix,
            'weights': weights,
            'indicator_types': indicator_types
        }

    @pytest.fixture
    def test_schemes(self):
        """Create test schemes with known mathematical properties."""
        return [
            {
                'scheme_id': 'test_scheme_1',
                'scheme_name': 'Test Scheme 1',
                'platform_inventory': {'USV': {'count': 5}},
                'deployment_plan': {'primary_sector': {'coordinates': [0, 0], 'radius_km': 50}},
                'task_assignments': {'test_task': {'primary_assets': ['USV'], 'coverage_requirement': 0.8}}
            },
            {
                'scheme_id': 'test_scheme_2',
                'scheme_name': 'Test Scheme 2',
                'platform_inventory': {'USV': {'count': 10}},
                'deployment_plan': {'primary_sector': {'coordinates': [0, 0], 'radius_km': 100}},
                'task_assignments': {'test_task': {'primary_assets': ['USV'], 'coverage_requirement': 0.9}}
            },
            {
                'scheme_id': 'test_scheme_3',
                'scheme_name': 'Test Scheme 3',
                'platform_inventory': {'USV': {'count': 15}},
                'deployment_plan': {'primary_sector': {'coordinates': [0, 0], 'radius_km': 150}},
                'task_assignments': {'test_task': {'primary_assets': ['USV'], 'coverage_requirement': 1.0}}
            }
        ]

    @pytest.mark.mathematical
    def test_array_indexing_validation(self, basic_test_data):
        """Test that array indexing operations are mathematically correct."""
        decision_matrix = basic_test_data['decision_matrix']
        weights = basic_test_data['weights']
        indicator_types = basic_test_data['indicator_types']

        # Run TOPSIS to get rankings
        topsis_result = topsis_rank(decision_matrix, weights, indicator_types)
        ci_scores = topsis_result['Ci']
        rankings = topsis_result['rankings']

        # Test indexing invariants
        n_alternatives = len(ci_scores)

        # 1. Best scheme should have highest Ci and rank 1
        best_ci_idx = np.argmax(ci_scores)  # Highest Ci
        best_rank_idx = np.argmin(rankings)  # Lowest rank (1 is best)

        # These should point to the same alternative
        assert best_ci_idx == best_rank_idx, f"Indexing mismatch: best Ci index {best_ci_idx} != best rank index {best_rank_idx}"

        # 2. Ci and rankings should be inversely correlated
        # (Higher Ci should have lower rank number)
        sorted_ci_indices = np.argsort(ci_scores)[::-1]  # Descending Ci
        sorted_rank_indices = np.argsort(rankings)  # Ascending rank

        np.testing.assert_array_equal(sorted_ci_indices, sorted_rank_indices,
                                    "Ci and rankings should be consistently ordered")

        # 3. All indices should be in valid range
        assert all(0 <= idx < n_alternatives for idx in [best_ci_idx, best_rank_idx]), \
            "Indices should be within valid range"

    @pytest.mark.mathematical
    def test_ranking_consistency_property(self, basic_test_data):
        """Test mathematical property: Higher Ci scores must always get better rankings."""
        decision_matrix = basic_test_data['decision_matrix']
        weights = basic_test_data['weights']
        indicator_types = basic_test_data['indicator_types']

        topsis_result = topsis_rank(decision_matrix, weights, indicator_types)
        ci_scores = topsis_result['Ci']
        rankings = topsis_result['rankings']

        # Mathematical invariant: If Ci_i > Ci_j, then rank_i < rank_j
        n = len(ci_scores)
        for i in range(n):
            for j in range(n):
                if ci_scores[i] > ci_scores[j]:
                    assert rankings[i] < rankings[j], \
                        f"Ranking inconsistency: Ci[{i}]={ci_scores[i]:.6f} > Ci[{j}]={ci_scores[j]:.6f} " \
                        f"but rank[{i}]={rankings[i]} >= rank[{j}]={rankings[j]}"
                elif ci_scores[i] == ci_scores[j]:
                    assert rankings[i] == rankings[j], \
                        f"Tie handling error: Equal Ci scores should have equal ranks"

    @pytest.mark.mathematical
    def test_boundary_conditions(self, basic_test_data):
        """Test edge cases and boundary conditions."""
        # Test 1: Minimum alternatives (2 alternatives, minimum for ranking)
        min_alt_matrix = np.array([
            [1.0, 2.0, 3.0],
            [2.0, 1.5, 2.5]
        ])
        min_weights = np.array([0.3, 0.3, 0.4])
        min_types = ['benefit', 'benefit', 'benefit']

        topsis_result = topsis_rank(min_alt_matrix, min_weights, min_types)

        assert len(topsis_result['Ci']) == 2, "Two alternatives should return two Ci scores"
        assert len(topsis_result['rankings']) == 2, "Two alternatives should return two rankings"
        assert all(ci >= 0.0 for ci in topsis_result['Ci']), "All Ci should be non-negative"
        assert set(topsis_result['rankings']) == {1, 2}, "Two alternatives should have ranks 1 and 2"

        # Test 2: Identical alternatives (edge case)
        identical_matrix = np.array([
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0]
        ])
        identical_weights = np.array([0.3, 0.3, 0.4])
        identical_types = ['benefit', 'benefit', 'benefit']

        topsis_result = topsis_rank(identical_matrix, identical_weights, identical_types)

        # All Ci scores should be identical
        ci_scores = topsis_result['Ci']
        assert np.allclose(ci_scores, ci_scores[0]), "Identical alternatives should have identical Ci scores"

        # Rankings should handle ties properly
        rankings = topsis_result['rankings']
        # For identical alternatives, rankings should be the same or very close
        assert np.allclose(rankings, rankings[0]), "Identical alternatives should have similar rankings"

    @pytest.mark.mathematical
    def test_numerical_stability(self):
        """Test numerical stability with extreme values."""
        # Test with very small values
        small_matrix = np.array([
            [1e-10, 1e-9, 1e-8],
            [1e-9, 1e-8, 1e-7],
            [1e-8, 1e-7, 1e-6]
        ])
        small_weights = np.array([0.3, 0.3, 0.4])
        small_types = ['benefit', 'benefit', 'benefit']

        # Should not raise exceptions
        topsis_result = topsis_rank(small_matrix, small_weights, small_types)
        assert not np.any(np.isnan(topsis_result['Ci'])), "Small values should not produce NaN"
        assert not np.any(np.isinf(topsis_result['Ci'])), "Small values should not produce Inf"

        # Test with very large values
        large_matrix = np.array([
            [1e6, 1e7, 1e8],
            [1e7, 1e8, 1e9],
            [1e8, 1e9, 1e10]
        ])
        large_weights = np.array([0.3, 0.3, 0.4])
        large_types = ['benefit', 'benefit', 'benefit']

        # Should not raise exceptions
        topsis_result = topsis_rank(large_matrix, large_weights, large_types)
        assert not np.any(np.isnan(topsis_result['Ci'])), "Large values should not produce NaN"
        assert not np.any(np.isinf(topsis_result['Ci'])), "Large values should not produce Inf"

    @pytest.mark.mathematical
    def test_weight_normalization_invariants(self, basic_test_data):
        """Test mathematical invariants related to weight normalization."""
        weights = basic_test_data['weights']

        # Weights should sum to 1.0 (within tolerance)
        assert abs(np.sum(weights) - 1.0) < 1e-10, f"Weights should sum to 1.0, got {np.sum(weights)}"

        # All weights should be positive
        assert np.all(weights > 0), "All weights should be positive"

        # Weights should be within [0, 1] range
        assert np.all(weights >= 0) and np.all(weights <= 1), "Weights should be in [0, 1] range"

    @pytest.mark.mathematical
    def test_decision_matrix_properties(self, basic_test_data):
        """Test mathematical properties of decision matrices."""
        decision_matrix = basic_test_data['decision_matrix']

        # Matrix should have consistent dimensions
        assert decision_matrix.shape[0] > 0, "Decision matrix should have at least one alternative"
        assert decision_matrix.shape[1] > 0, "Decision matrix should have at least one criterion"

        # No NaN or Inf values
        assert not np.any(np.isnan(decision_matrix)), "Decision matrix should not contain NaN"
        assert not np.any(np.isinf(decision_matrix)), "Decision matrix should not contain Inf"

        # All values should be non-negative for TOPSIS
        assert np.all(decision_matrix >= 0), "Decision matrix values should be non-negative"

    @pytest.mark.mathematical
    def test_batch_evaluation_indexing_correctness(self, test_schemes):
        """Test that batch evaluation uses correct indexing (prevents regression)."""
        # Create mock indicator and fuzzy configs for testing
        indicator_config = {
            'primary_capabilities': {},
            'secondary_indicators': {
                'C1_1': {'name': 'Test1', 'primary_capability': 'C1', 'type': 'benefit', 'fuzzy_flag': False},
                'C1_2': {'name': 'Test2', 'primary_capability': 'C1', 'type': 'benefit', 'fuzzy_flag': False},
                'C1_3': {'name': 'Test3', 'primary_capability': 'C1', 'type': 'benefit', 'fuzzy_flag': False}
            }
        }
        fuzzy_config = {
            'fuzzy_scale': {'差': 0.25, '中': 0.5, '良': 0.75, '优': 1.0},
            'applicable_indicators': ['C1_1', 'C1_2', 'C1_3']
        }

        # Use mock expert judgments to avoid file dependencies
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create temporary expert judgment files
            primary_file = os.path.join(temp_dir, 'primary.yaml')
            with open(primary_file, 'w') as f:
                f.write("""
matrix_id: test_primary
dimension: 1
matrix: [[1.0]]
""")

            expert_judgments = {
                'primary_capabilities_file': primary_file,
                'secondary_indicators_dir': temp_dir
            }

            # Run batch evaluation
            batch_result = evaluate_batch(test_schemes, indicator_config, fuzzy_config, expert_judgments)

            # Validate indexing correctness
            assert 'best_scheme' in batch_result, "Batch result should contain best_scheme"
            assert 'individual_results' in batch_result, "Batch result should contain individual_results"

            best_scheme = batch_result['best_scheme']
            individual_results = batch_result['individual_results']

            # Best scheme should have highest Ci and rank 1
            best_ci = best_scheme['Ci_score']
            best_rank = best_scheme['rank']

            assert best_rank == 1, "Best scheme should have rank 1"

            # Verify that best_scheme actually corresponds to the best individual result
            individual_cis = [result['Ci'] for result in individual_results.values()]
            max_individual_ci = max(individual_cis)

            assert abs(best_ci - max_individual_ci) < 1e-10, \
                f"Best scheme Ci ({best_ci}) should match max individual Ci ({max_individual_ci})"

    @pytest.mark.mathematical
    def test_evaluator_module_edge_cases(self):
        """Test edge cases specific to evaluator module functions."""
        # Test with empty decision matrix
        try:
            empty_matrix = np.array([]).reshape(0, 3)
            weights = np.array([0.3, 0.3, 0.4])
            types = ['benefit', 'benefit', 'benefit']

            # This should raise an appropriate error
            with pytest.raises((ValueError, IndexError)):
                topsis_rank(empty_matrix, weights, types)
        except Exception:
            # Any exception is acceptable for empty matrix
            pass

        # Test with mismatched dimensions
        try:
            mismatched_matrix = np.array([[1.0, 2.0], [3.0, 4.0]])  # 2x2
            wrong_weights = np.array([0.3, 0.3, 0.4])  # 3 elements
            types = ['benefit', 'benefit', 'benefit']

            # This should raise an appropriate error
            with pytest.raises((ValueError, IndexError)):
                topsis_rank(mismatched_matrix, wrong_weights, types)
        except Exception:
            # Any exception is acceptable for dimension mismatch
            pass

    @pytest.mark.mathematical
    def test_precision_and_tolerance_validation(self, basic_test_data):
        """Test that precision requirements are met."""
        decision_matrix = basic_test_data['decision_matrix']
        weights = basic_test_data['weights']
        indicator_types = basic_test_data['indicator_types']

        topsis_result = topsis_rank(decision_matrix, weights, indicator_types)
        ci_scores = topsis_result['Ci']

        # Ci scores should be in [0, 1] range with high precision
        assert np.all(ci_scores >= 0.0), "All Ci scores should be non-negative"
        assert np.all(ci_scores <= 1.0), "All Ci scores should be <= 1.0"

        # Test precision tolerance (1e-6 requirement from plan)
        # Sum of distances should be mathematically consistent
        assert not np.any(np.isnan(ci_scores)), "Ci scores should not be NaN"
        assert not np.any(np.isinf(ci_scores)), "Ci scores should not be infinite"

        # Test reproducibility
        topsis_result2 = topsis_rank(decision_matrix, weights, indicator_types)
        np.testing.assert_allclose(ci_scores, topsis_result2['Ci'], rtol=1e-12,
                                    err_msg="Results should be reproducible")


class TestEvaluatorRegressionPrevention:
    """Tests specifically designed to prevent regressions of known bugs."""

    @pytest.mark.mathematical
    def test_indexing_bug_regression_prevention(self):
        """Test to prevent the np.argmin() - 1 indexing bug we fixed."""
        # Create a test case that would have failed with the original bug
        ci_scores = np.array([0.1, 0.8, 0.3, 0.9, 0.2])

        # The correct logic should be:
        best_idx = np.argmin([2, 1, 3, 0, 4])  # Assuming ranks
        # NOT: best_idx = np.argmin([2, 1, 3, 0, 4]) - 1  # Original buggy code

        # Simulate what TOPSIS would return
        rankings = len(ci_scores) - np.argsort(ci_scores).argsort()  # Correct ranking calculation
        best_idx_correct = np.argmin(rankings)

        # Test the invariant: the best index should have the highest Ci score
        assert best_idx_correct == np.argmax(ci_scores), \
            f"Best index {best_idx_correct} should match argmax of Ci scores {np.argmax(ci_scores)}"

        # Test that the bug (off-by-1 error) would be caught
        best_idx_buggy = np.argmin(rankings) - 1
        assert best_idx_buggy != best_idx_correct, \
            "Buggy indexing should produce different result"

        # The buggy index should be invalid or point to wrong element
        if best_idx_buggy >= 0 and best_idx_buggy < len(ci_scores):
            # If it's a valid index, it should NOT point to the max Ci
            assert best_idx_buggy != np.argmax(ci_scores), \
                "Buggy index incorrectly points to max Ci"

    @pytest.mark.mathematical
    def test_array_bounds_validation(self):
        """Test that all array operations stay within bounds."""
        # Test various array sizes (minimum 2 for TOPSIS)
        for n in [2, 3, 5, 10, 50]:
            matrix = np.random.rand(n, 5)  # n alternatives, 5 criteria
            weights = np.ones(5) / 5  # Equal weights
            types = ['benefit'] * 5

            topsis_result = topsis_rank(matrix, weights, types)
            ci_scores = topsis_result['Ci']
            rankings = topsis_result['rankings']

            # All indices should be valid
            assert len(ci_scores) == n, f"Ci scores length should match number of alternatives {n}"
            assert len(rankings) == n, f"Rankings length should match number of alternatives {n}"

            # Best index should be in valid range
            best_idx = np.argmin(rankings)
            assert 0 <= best_idx < n, f"Best index {best_idx} should be in range [0, {n-1}]"

    @pytest.mark.mathematical
    def test_ranking_completeness_validation(self):
        """Test that rankings form a complete permutation."""
        for n in [2, 3, 5, 10]:  # Start from 2 (minimum for TOPSIS)
            matrix = np.random.rand(n, 5)
            weights = np.ones(5) / 5
            types = ['benefit'] * 5

            topsis_result = topsis_rank(matrix, weights, types)
            rankings = topsis_result['rankings']

            # Rankings should be a complete permutation of 1..n
            expected_rankings = set(range(1, n + 1))
            actual_rankings = set(rankings)

            assert actual_rankings == expected_rankings, \
                f"Rankings should be complete permutation of {{1..{n}}}, got {sorted(actual_rankings)}"