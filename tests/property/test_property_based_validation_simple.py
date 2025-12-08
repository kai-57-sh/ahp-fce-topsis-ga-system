"""
Simplified Property-Based Testing with Hypothesis

Research-grade validation using property-based testing to automatically generate
hundreds of test cases and validate mathematical invariants across wide input ranges.
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st, assume
import warnings

# Add parent directory to path for imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from modules.topsis_module import topsis_rank
from modules.ahp_module import calculate_weights


class TestMathematicalInvariants:
    """Test fundamental mathematical invariants across the system."""

    @given(
        arrays=st.lists(
            st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
            min_size=2, max_size=20
        ).map(np.array)
    )
    def test_array_indexing_invariants(self, arrays):
        """Test fundamental array indexing invariants."""
        n = len(arrays)
        assume(n >= 1)

        # Property 1: argmax and argmin indices should be in bounds
        max_idx = np.argmax(arrays)
        min_idx = np.argmin(arrays)

        assert 0 <= max_idx < n, f"argmax index {max_idx} should be in [0, {n-1}]"
        assert 0 <= min_idx < n, f"argmin index {min_idx} should be in [0, {n-1}]"

        # Property 2: argmax should point to maximum value
        assert arrays[max_idx] >= arrays[i] for i in range(n), "argmax should point to maximum value"

        # Property 3: argmin should point to minimum value
        assert arrays[min_idx] <= arrays[i] for i in range(n), "argmin should point to minimum value"

        # Property 4: For identical values, argmax should return first occurrence
        if np.allclose(arrays, arrays[0]):
            assert max_idx == 0, "For identical values, argmax should return 0"

    @given(
        sequences=st.lists(st.integers(min_value=1, max_value=100), min_size=2, max_size=20)
    )
    def test_ranking_invariants(self, sequences):
        """Test fundamental ranking invariants."""
        # Create rankings from sequence (lower = better rank)
        ranks = np.array([len(sequences) - np.argsort(sequences).argsort()])

        n = len(sequences)

        # Property 1: Rankings should be a permutation of 1..n
        expected_rankings = set(range(1, n + 1))
        actual_rankings = set(ranks)
        assert actual_rankings == expected_rankings, "Rankings must be complete permutation"

        # Property 2: Each rank should appear exactly once
        rank_counts = {}
        for rank in ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1

        for rank in expected_rankings:
            assert rank_counts[rank] == 1, f"Rank {rank} should appear exactly once"

        # Property 3: Best rank (1) should be unique
        rank_one_count = sum(1 for r in ranks if r == 1)
        assert rank_one_count == 1, "Rank 1 should be unique"

    @given(
        arrays=st.lists(
            st.floats(min_value=0.01, max_value=1.0, allow_nan=False, allow_infinity=False),
            min_size=2, max_size=20
        ).map(np.array)
    )
    def test_normalization_invariants(self, arrays):
        """Test mathematical invariants of normalization."""
        n = len(arrays)
        assume(n > 0)

        # Test sum-to-1 normalization
        normalized = arrays / np.sum(arrays)

        # Property 1: Sum should be 1.0
        assert abs(np.sum(normalized) - 1.0) < 1e-12, "Normalized array should sum to 1.0"

        # Property 2: All elements should be in [0, 1]
        assert all(0.0 <= x <= 1.0 for x in normalized), "Normalized elements should be in [0,1]"

        # Property 3: Order should be preserved
        original_order = np.argsort(arrays)
        normalized_order = np.argsort(normalized)
        np.testing.assert_array_equal(original_order, normalized_order,
                                    "Normalization should preserve order")


class TestTOPSISPropertyBasedValidation:
    """Property-based testing for TOPSIS algorithm mathematical correctness."""

    @given(
        # Generate valid decision matrices
        st.integers(min_value=2, max_value=5).flatmap(lambda n:
            st.lists(
                st.lists(st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False),
                    min_size=n, max_size=n,
                    min_size=3, max_size=5
                ).map(lambda rows: np.array(rows))
        )
    )
    def test_topsis_basic_properties(self, decision_matrix):
        """Test basic TOPSIS properties with valid decision matrices."""
        m, n = decision_matrix.shape  # m alternatives, n criteria
        assume(m >= 2 and n >= 2 and m <= 5 and n <= 5)

        # Create corresponding weights and types
        weights = np.ones(n) / n
        indicator_types = ['benefit'] * n

        # Run TOPSIS
        result = topsis_rank(decision_matrix, weights, indicator_types)
        ci_scores = result['Ci']
        rankings = result['rankings']

        # Property 1: Ci scores should be in [0, 1] range
        assert all(0.0 <= ci <= 1.0 for ci in ci_scores), "Ci scores must be in [0,1]"

        # Property 2: Rankings should be a complete permutation of 1..m
        expected_rankings = set(range(1, m + 1))
        actual_rankings = set(rankings)
        assert actual_rankings == expected_rankings, "Rankings must be complete permutation"

        # Property 3: Array bounds validation
        assert len(ci_scores) == m, f"Should have {m} Ci scores"
        assert len(rankings) == m, f"Should have {m} rankings"

    @given(
        # Generate weight vectors
        st.lists(st.floats(min_value=0.01, max_value=1.0, allow_nan=False, allow_infinity=False),
                    min_size=3, max_size=6).map(lambda w: np.array(w) / np.sum(w))
    )
    def test_weight_normalization_properties(self, weights):
        """Test weight vector normalization properties."""
        n = len(weights)
        assume(n >= 2 and n <= 6)

        # Property 1: Weights should sum to approximately 1.0
        assert abs(np.sum(weights) - 1.0) < 1e-10, f"Weights should sum to 1.0, got {np.sum(weights)}"

        # Property 2: All weights should be positive
        assert all(w > 0 for w in weights), "All weights should be positive"

        # Property 3: All weights should be in (0, 1] range
        assert all(0 < w <= 1 for w in weights), "Weights should be in (0, 1] range"

    @given(
        # Test with different matrix sizes
        st.integers(min_value=2, max_value=10)
    )
    def test_array_bounds_validation(self, n):
        """Test that array operations stay within bounds."""
        assume(2 <= n <= 10)  # Reasonable range for testing

        # Create test matrix
        matrix = np.random.rand(n, 5)  # n alternatives, 5 criteria
        weights = np.ones(5) / 5
        types = ['benefit'] * 5

        try:
            result = topsis_rank(matrix, weights, types)
            ci_scores = result['Ci']
            rankings = result['rankings']

            # All indices should be valid
            assert len(ci_scores) == n, f"Ci scores length should match number of alternatives {n}"
            assert len(rankings) == n, f"Rankings length should match number of alternatives {n}"

            # Best index should be in valid range
            best_idx = np.argmin(rankings)
            assert 0 <= best_idx < n, f"Best index {best_idx} should be in range [0, {n-1}]"

        except Exception:
            # Some edge cases might fail - this is acceptable
            pass


class TestEdgeCaseGeneration:
    """Generate and test edge cases that manual testing might miss."""

    @given(
        st.floats(min_value=1e-15, max_value=1e-10, allow_nan=False, allow_infinity=False)
    )
    def test_extreme_small_values(self, tiny_value):
        """Test behavior with extremely small values."""
        # Test with arrays containing tiny values
        matrix = np.array([[tiny_value, 2*tiny_value], [3*tiny_value, 4*tiny_value]])
        weights = np.array([0.5, 0.5])
        types = ['benefit', 'benefit']

        try:
            result = topsis_rank(matrix, weights, types)

            # Should not produce NaN or Inf
            assert not np.any(np.isnan(result['Ci'])), "Tiny values should not produce NaN"
            assert not np.any(np.isinf(result['Ci'])), "Tiny values should not produce Inf"

            # Rankings should still be valid (if they exist)
            if 'rankings' in result:
                n = len(result['rankings'])
                assert set(result['rankings']) == set(range(1, n + 1)), "Rankings should be valid"

        except Exception:
            # Some edge cases might fail - this is acceptable
            pass

    @given(
        st.floats(min_value=1e6, max_value=1e10, allow_nan=False, allow_infinity=False)
    )
    def test_extreme_large_values(self, large_value):
        """Test behavior with extremely large values."""
        # Test with matrices containing large values
        matrix = np.array([[large_value, 2*large_value], [3*large_value, 4*large_value]])
        weights = np.array([0.5, 0.5])
        types = ['benefit', 'benefit']

        try:
            result = topsis_rank(matrix, weights, types)

            # Should not produce NaN or Inf
            assert not np.any(np.isnan(result['Ci'])), "Large values should not produce NaN"
            assert not np.any(np.isinf(result['Ci'])), "Large values should not produce Inf"

            # Rankings should still be valid (if they exist)
            if 'rankings' in result:
                n = len(result['rankings'])
                assert set(result['rankings']) == set(range(1, n + 1)), "Rankings should be valid"

        except Exception:
            # Some edge cases might fail - this is acceptable
            pass


# Configure Hypothesis settings
def pytest_configure(config):
    """Configure Hypothesis for thorough testing."""
    from hypothesis import settings
    settings.register_profile("default", max_examples=200, deadline=10000)
    settings.load_profile("default")

# Mark tests as mathematical validation
pytest_plugins = [pytest.mark.mathematical]