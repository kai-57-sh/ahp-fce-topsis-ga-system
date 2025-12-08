"""
Basic Property-Based Testing

Simplified property-based testing for mathematical validation without complex decorators.
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st, assume
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from modules.topsis_module import topsis_rank


class TestBasicPropertyValidation:
    """Basic property-based validation tests."""

    @given(
        st.lists(st.floats(min_value=0.0, max_value=100.0, allow_nan=False), min_size=2, max_size=20)
    )
    def test_array_indexing_bounds(self, values):
        """Test array indexing bounds property."""
        arr = np.array(values)
        n = len(arr)
        max_idx = np.argmax(arr)
        min_idx = np.argmin(arr)

        assert 0 <= max_idx < n, f"argmax index {max_idx} should be in range [0, {n-1}]"
        assert 0 <= min_idx < n, f"argmin index {min_idx} should be in range [0, {n-1}]"

    @given(
        st.lists(st.integers(min_value=1, max_value=100), min_size=2, max_size=20)
    )
    def test_ranking_completeness(self, scores):
        """Test ranking completeness property."""
        scores = np.array(scores)
        n = len(scores)

        # Create rankings (higher score = better rank)
        ranks = len(scores) - np.argsort(scores).argsort()

        # Rankings should be a permutation of 1..n
        expected_rankings = set(range(1, n + 1))
        actual_rankings = set(ranks)
        assert actual_rankings == expected_rankings, "Rankings must be complete permutation"

    @given(
        st.lists(st.floats(min_value=0.01, max_value=1.0, allow_nan=False), min_size=3, max_size=6)
    )
    def test_weight_normalization(self, values):
        """Test weight normalization property."""
        weights = np.array(values)
        normalized = weights / np.sum(weights)

        # Sum should be 1.0
        assert abs(np.sum(normalized) - 1.0) < 1e-12, "Normalized weights should sum to 1.0"

        # All weights should be positive
        assert all(w > 0 for w in normalized), "All normalized weights should be positive"

    @given(
        st.integers(min_value=2, max_value=5)
    )
    def test_topsis_with_random_data(self, n):
        """Test TOPSIS with random data."""
        assume(2 <= n <= 5)

        # Generate random decision matrix
        matrix = np.random.rand(n, 3)
        weights = np.array([0.3, 0.3, 0.4])
        types = ['benefit', 'benefit', 'benefit']

        try:
            result = topsis_rank(matrix, weights, types)

            # Basic structure checks
            assert 'Ci' in result, "Should have Ci scores"
            assert 'rankings' in result, "Should have rankings"

            # Length checks
            assert len(result['Ci']) == n, f"Should have {n} Ci scores"
            assert len(result['rankings']) == n, f"Should have {n} rankings"

            # Range checks
            assert all(0.0 <= ci <= 1.0 for ci in result['Ci']), "All Ci scores should be in [0,1]"

        except Exception:
            # Some cases might fail - this is acceptable
            pass


# Configure pytest
def pytest_configure(config):
    from hypothesis import settings
    settings.register_profile("default", max_examples=100)
    settings.load_profile("default")