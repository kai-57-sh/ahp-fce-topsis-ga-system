"""
Unit Tests for TOPSIS Module

Tests TOPSIS ranking algorithm, ideal solution identification, and distance calculations.
"""

import pytest
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from modules.topsis_module import topsis_rank, identify_ideal_solutions, vector_normalize, TOPSISError


class TestTOPSISModule:
    """Test cases for TOPSIS module functionality."""

    @pytest.fixture
    def sample_decision_matrix(self):
        """Sample decision matrix for testing."""
        return np.array([
            [1.0, 2.0, 3.0, 4.0],
            [2.0, 1.5, 2.5, 3.5],
            [1.5, 2.5, 2.0, 4.5],
            [3.0, 1.0, 3.5, 2.0]
        ])

    @pytest.fixture
    def sample_weights(self):
        """Sample weights for testing."""
        return np.array([0.3, 0.2, 0.3, 0.2])

    @pytest.fixture
    def sample_indicator_types(self):
        """Sample indicator types for testing."""
        return ['benefit', 'cost', 'benefit', 'cost']

    def test_topsis_rank_ci_range(self, sample_decision_matrix, sample_weights, sample_indicator_types):
        """Test TOPSIS ranking produces Ci scores in correct range."""
        result = topsis_rank(sample_decision_matrix, sample_weights, sample_indicator_types)

        # Check basic structure
        assert 'Ci' in result
        assert 'rankings' in result
        assert 'PIS' in result
        assert 'NIS' in result

        # Check Ci scores are in [0, 1] range
        ci_scores = result['Ci']
        assert all(0.0 <= ci <= 1.0 for ci in ci_scores), f"Ci scores not in [0,1] range: {ci_scores}"

        # Check rankings are positive integers
        rankings = result['rankings']
        assert all(rank > 0 for rank in rankings), f"Rankings should be positive: {rankings}"

        # Check correct number of results
        n_alternatives = sample_decision_matrix.shape[0]
        assert len(ci_scores) == n_alternatives
        assert len(rankings) == n_alternatives

    def test_identify_ideal_solutions_benefit_cost(self, sample_decision_matrix, sample_indicator_types):
        """Test ideal solution identification for benefit and cost indicators."""
        # Apply weights to create weighted matrix
        weights = np.array([0.25, 0.25, 0.25, 0.25])
        normalized_matrix = vector_normalize(sample_decision_matrix, axis=0)
        weighted_matrix = normalized_matrix * weights

        PIS, NIS = identify_ideal_solutions(weighted_matrix, sample_indicator_types)

        # Check PIS and NIS dimensions
        n_indicators = weighted_matrix.shape[1]
        assert len(PIS) == n_indicators
        assert len(NIS) == n_indicators

        # Check benefit indicators: PIS should be max, NIS should be min
        for j, indicator_type in enumerate(sample_indicator_types):
            column_values = weighted_matrix[:, j]
            if indicator_type == 'benefit':
                assert PIS[j] == np.max(column_values), f"PIS for benefit indicator should be max"
                assert NIS[j] == np.min(column_values), f"NIS for benefit indicator should be min"
            else:  # cost indicator
                assert PIS[j] == np.min(column_values), f"PIS for cost indicator should be min"
                assert NIS[j] == np.max(column_values), f"NIS for cost indicator should be max"

    def test_topsis_rank_all_benefit_indicators(self):
        """Test TOPSIS ranking with all benefit indicators."""
        decision_matrix = np.array([
            [1.0, 2.0, 3.0],
            [2.0, 3.0, 4.0],
            [1.5, 2.5, 3.5]
        ])
        weights = np.array([0.33, 0.33, 0.34])
        indicator_types = ['benefit', 'benefit', 'benefit']

        result = topsis_rank(decision_matrix, weights, indicator_types)

        # All benefit indicators: higher values should rank better
        ci_scores = result['Ci']
        rankings = result['rankings']

        # The alternative with highest values should have best rank (rank 1)
        best_rank_index = np.argmin(rankings)
        assert best_rank_index == 1, "Second alternative should have best rank (highest values)"

    def test_topsis_rank_all_cost_indicators(self):
        """Test TOPSIS ranking with all cost indicators."""
        decision_matrix = np.array([
            [4.0, 3.0, 2.0],
            [2.0, 1.0, 1.5],
            [3.0, 2.0, 1.8]
        ])
        weights = np.array([0.33, 0.33, 0.34])
        indicator_types = ['cost', 'cost', 'cost']

        result = topsis_rank(decision_matrix, weights, indicator_types)

        # All cost indicators: lower values should rank better
        ci_scores = result['Ci']
        rankings = result['rankings']

        # The alternative with lowest values should have best rank (rank 1)
        best_rank_index = np.argmin(rankings)
        assert best_rank_index == 1, "Second alternative should have best rank (lowest values)"

    def test_topsis_rank_mixed_indicators(self, sample_decision_matrix, sample_indicator_types):
        """Test TOPSIS ranking with mixed benefit and cost indicators."""
        weights = np.array([0.25, 0.25, 0.25, 0.25])

        result = topsis_rank(sample_decision_matrix, weights, sample_indicator_types)

        # Should produce valid rankings for mixed indicators
        rankings = result['rankings']
        ci_scores = result['Ci']

        # Rankings should be unique (no ties in this test case)
        assert len(set(rankings)) == len(rankings), "Rankings should be unique"

        # Best rank should be 1
        assert min(rankings) == 1, "Best rank should be 1"

        # All ranks should be present
        expected_ranks = set(range(1, len(rankings) + 1))
        actual_ranks = set(rankings)
        assert actual_ranks == expected_ranks, f"Missing ranks: {expected_ranks - actual_ranks}"

    def test_topsis_rank_equal_alternatives(self):
        """Test TOPSIS ranking with identical alternatives."""
        decision_matrix = np.array([
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],  # Identical to first
            [1.0, 2.0, 3.0]   # Identical to first
        ])
        weights = np.array([0.33, 0.33, 0.34])
        indicator_types = ['benefit', 'benefit', 'benefit']

        result = topsis_rank(decision_matrix, weights, indicator_types)

        # All alternatives should have same Ci score and rank
        ci_scores = result['Ci']
        rankings = result['rankings']

        # All Ci scores should be equal
        assert np.allclose(ci_scores, ci_scores[0]), "All Ci scores should be equal for identical alternatives"

        # Rankings may be the same or different based on implementation
        # This is acceptable as long as they're valid
        assert all(rank > 0 for rank in rankings), "All ranks should be positive"

    def test_vector_normalize_function(self):
        """Test vector normalization function."""
        matrix = np.array([
            [3.0, 4.0],
            [1.0, 2.0],
            [2.0, 6.0]
        ])

        normalized = vector_normalize(matrix, axis=0)

        # Check dimensions
        assert normalized.shape == matrix.shape

        # Check each column is normalized (Euclidean norm = 1)
        for j in range(normalized.shape[1]):
            column_norm = np.linalg.norm(normalized[:, j])
            assert abs(column_norm - 1.0) < 1e-10, f"Column {j} not properly normalized"

        # Check non-negative values
        assert np.all(normalized >= 0), "Normalized values should be non-negative"

    def test_topsis_rank_edge_cases(self):
        """Test TOPSIS ranking with edge cases."""
        # Test with single alternative (minimum valid case)
        single_alternative = np.array([[1.0, 2.0, 3.0]])
        weights = np.array([0.33, 0.33, 0.34])
        indicator_types = ['benefit', 'benefit', 'benefit']

        with pytest.raises(TOPSISISError):  # Should require at least 2 alternatives
            topsis_rank(single_alternative, weights, indicator_types)

    def test_topsis_rank_invalid_weights(self, sample_decision_matrix, sample_indicator_types):
        """Test TOPSIS ranking with invalid weights."""
        invalid_weights = np.array([0.5, 0.3, 0.2])  # Wrong length

        with pytest.raises(TOPSISISError):
            topsis_rank(sample_decision_matrix, invalid_weights, sample_indicator_types)

        # Test with weights that don't sum to 1
        weights_not_summing = np.array([0.5, 0.5, 0.5, 0.5])  # Sums to 2.0

        with pytest.raises(TOPSISISError):
            topsis_rank(sample_decision_matrix, weights_not_summing, sample_indicator_types)

    def test_topsis_rank_invalid_indicator_types(self, sample_decision_matrix, sample_weights):
        """Test TOPSIS ranking with invalid indicator types."""
        invalid_types = ['benefit', 'invalid', 'cost', 'benefit']

        with pytest.raises(TOPSISISError):
            topsis_rank(sample_decision_matrix, sample_weights, invalid_types)

    def test_topsis_rank_negative_values(self):
        """Test TOPSIS ranking with negative values in decision matrix."""
        negative_matrix = np.array([
            [1.0, -2.0, 3.0],
            [2.0, 1.0, -1.5],
            [1.5, -1.0, 2.0]
        ])
        weights = np.array([0.33, 0.33, 0.34])
        indicator_types = ['benefit', 'cost', 'benefit']

        with pytest.raises(TOPSISISError):
            topsis_rank(negative_matrix, weights, indicator_types)

    def test_topsis_distance_calculations(self, sample_decision_matrix, sample_weights, sample_indicator_types):
        """Test distance calculations in TOPSIS."""
        result = topsis_rank(sample_decision_matrix, sample_weights, sample_indicator_types)

        # Check that distances are calculated
        assert 'D_plus' in result
        assert 'D_minus' in result

        D_plus = result['D_plus']
        D_minus = result['D_minus']

        # Check distance dimensions
        n_alternatives = sample_decision_matrix.shape[0]
        assert len(D_plus) == n_alternatives
        assert len(D_minus) == n_alternatives

        # Check distances are non-negative
        assert np.all(D_plus >= 0), "Distances to PIS should be non-negative"
        assert np.all(D_minus >= 0), "Distances to NIS should be non-negative"

    def test_topsis_rank_validation_passed(self, sample_decision_matrix, sample_weights, sample_indicator_types):
        """Test TOPSIS validation results."""
        result = topsis_rank(sample_decision_matrix, sample_weights, sample_indicator_types)

        # Check validation section
        assert 'validation' in result
        validation = result['validation']

        assert 'valid' in validation
        assert 'errors' in validation
        assert 'warnings' in validation

        # Should pass validation with valid inputs
        assert validation['valid'] == True
        assert len(validation['errors']) == 0

    def test_topsis_rank_reproducibility(self, sample_decision_matrix, sample_weights, sample_indicator_types):
        """Test TOPSIS ranking produces reproducible results."""
        # Run TOPSIS twice with same inputs
        result1 = topsis_rank(sample_decision_matrix, sample_weights, sample_indicator_types)
        result2 = topsis_rank(sample_decision_matrix, sample_weights, sample_indicator_types)

        # Results should be identical
        np.testing.assert_array_almost_equal(result1['Ci'], result2['Ci'])
        np.testing.assert_array_equal(result1['rankings'], result2['rankings'])

    def test_ideal_solutions_edge_cases(self):
        """Test ideal solution identification with edge cases."""
        # Test with matrix where all values in a column are the same
        uniform_column_matrix = np.array([
            [1.0, 2.0, 3.0],
            [2.0, 2.0, 4.0],
            [3.0, 2.0, 5.0]
        ])
        weights = np.array([0.33, 0.33, 0.34])
        indicator_types = ['benefit', 'benefit', 'benefit']

        normalized = vector_normalize(uniform_column_matrix, axis=0)
        weighted = normalized * weights

        PIS, NIS = identify_ideal_solutions(weighted, indicator_types)

        # For uniform column, PIS and NIS should be the same
        assert PIS[1] == NIS[1], "For uniform column, PIS and NIS should be equal"

    def test_performance_with_large_matrix(self):
        """Test TOPSIS performance with larger matrices."""
        # Generate larger matrix
        np.random.seed(42)
        n_alternatives = 50
        n_indicators = 20

        large_matrix = np.random.rand(n_alternatives, n_indicators) * 10 + 1
        large_weights = np.random.rand(n_indicators)
        large_weights = large_weights / np.sum(large_weights)  # Normalize to sum to 1
        large_types = np.random.choice(['benefit', 'cost'], n_indicators).tolist()

        # Should handle larger matrices without issues
        result = topsis_rank(large_matrix, large_weights, large_types)

        # Check basic properties
        assert len(result['Ci']) == n_alternatives
        assert len(result['rankings']) == n_alternatives
        assert all(0.0 <= ci <= 1.0 for ci in result['Ci'])

    def test_numerical_precision(self):
        """Test numerical precision in TOPSIS calculations."""
        # Use values that could cause precision issues
        precise_matrix = np.array([
            [1e-10, 1e10, 1.0],
            [2e-10, 2e10, 2.0],
            [3e-10, 3e10, 3.0]
        ])
        weights = np.array([0.33, 0.33, 0.34])
        indicator_types = ['benefit', 'cost', 'benefit']

        result = topsis_rank(precise_matrix, weights, indicator_types)

        # Should handle extreme values without numerical issues
        assert not np.any(np.isnan(result['Ci'])), "Ci scores should not be NaN"
        assert not np.any(np.isinf(result['Ci'])), "Ci scores should not be infinite"
        assert all(0.0 <= ci <= 1.0 for ci in result['Ci']), "Ci scores should be in valid range"


if __name__ == '__main__':
    # Run tests if executed directly
    pytest.main([__file__, '-v'])