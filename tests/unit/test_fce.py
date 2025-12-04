"""
Unit Tests for FCE Module

Tests fuzzy comprehensive evaluation, membership functions, and score calculations.
"""

import pytest
import numpy as np
import yaml
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from modules.fce_module import fuzzy_evaluate, validate_membership_degrees, FCEError


class TestFCEModule:
    """Test cases for FCE module functionality."""

    @pytest.fixture
    def fuzzy_scale(self):
        """Standard fuzzy scale for testing."""
        return {
            '差': 0.25,  # Poor
            '中': 0.50,  # Medium
            '良': 0.75,  # Good
            '优': 1.00   # Excellent
        }

    @pytest.fixture
    def sample_fuzzy_data(self):
        """Load sample fuzzy data from fixtures."""
        fixture_path = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'sample_fuzzy_data.yaml')
        with open(fixture_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def test_fuzzy_evaluate_membership_sum(self, fuzzy_scale):
        """Test fuzzy evaluation with membership degree validation."""
        expert_assessments = {
            '差': 0,  # No assessments as 'Poor'
            '中': 1,  # One assessment as 'Medium'
            '良': 2,  # Two assessments as 'Good'
            '优': 0   # No assessments as 'Excellent'
        }

        result = fuzzy_evaluate(expert_assessments, fuzzy_scale)

        # Check basic structure
        assert 'membership_vector' in result
        assert 'fuzzy_score' in result
        assert 'total_experts' in result
        assert 'valid' in result

        # Check membership sum validation
        assert result['valid'] == True
        membership_vector = result['membership_vector']
        assert abs(np.sum(membership_vector) - 1.0) < 1e-6

    def test_fuzzy_evaluate_score_range(self, fuzzy_scale):
        """Test fuzzy evaluation produces scores in correct range."""
        expert_assessments = {
            '差': 1,  # One assessment as 'Poor'
            '中': 0,  # No assessments as 'Medium'
            '良': 1,  # One assessment as 'Good'
            '优': 1   # One assessment as 'Excellent'
        }

        result = fuzzy_evaluate(expert_assessments, fuzzy_scale)

        # Check fuzzy score is in valid range
        fuzzy_score = result['fuzzy_score']
        assert 0.0 <= fuzzy_score <= 1.0, f"Fuzzy score {fuzzy_score} not in [0,1] range"

        # Check membership vector is valid
        membership_vector = result['membership_vector']
        assert len(membership_vector) == 4  # Should have 4 linguistic terms
        assert all(0.0 <= mv <= 1.0 for mv in membership_vector), "Membership values should be in [0,1] range"

    def test_fuzzy_evaluate_multiple_experts(self, fuzzy_scale):
        """Test fuzzy evaluation with multiple experts."""
        # Aggregate expert assessments into counts
        # 3 experts: 1 said "良" (Good), 1 said "优" (Excellent), 1 said "中" (Medium)
        expert_assessments = {
            '差': 0,  # Count of "Poor" assessments
            '中': 1,  # Count of "Medium" assessments
            '良': 1,  # Count of "Good" assessments
            '优': 1   # Count of "Excellent" assessments
        }

        result = fuzzy_evaluate(expert_assessments, fuzzy_scale)

        # Should contain fuzzy evaluation results
        assert 'fuzzy_score' in result
        assert 'membership_vector' in result
        assert 'total_experts' in result
        assert result['total_experts'] == 3

        # Fuzzy score should be a reasonable value
        assert 0.0 <= result['fuzzy_score'] <= 1.0

    def test_fuzzy_evaluate_simple(self, fuzzy_scale):
        """Test fuzzy evaluation with simple expert assessments."""
        expert_assessments = {
            '差': 1,  # 1 expert said "Poor"
            '中': 2,  # 2 experts said "Medium"
            '良': 1,  # 1 expert said "Good"
            '优': 0   # 0 experts said "Excellent"
        }

        result = fuzzy_evaluate(expert_assessments, fuzzy_scale)

        # Should contain fuzzy evaluation results
        assert 'fuzzy_score' in result
        assert 'membership_vector' in result
        assert 'total_experts' in result
        assert result['total_experts'] == 4

        # Fuzzy score should be a reasonable value
        assert 0.0 <= result['fuzzy_score'] <= 1.0

    def test_validate_membership_degrees_valid(self):
        """Test membership degree validation with valid input."""
        membership_vectors = {
            'indicator_1': [0.25, 0.50, 0.25, 0.0],  # Sums to 1.0
            'indicator_2': [0.0, 0.75, 0.25, 0.0],    # Sums to 1.0
            'indicator_3': [1.0, 0.0, 0.0, 0.0]       # Sums to 1.0
        }

        # Test each indicator separately since validate_membership_degrees expects numpy array
        for indicator_name, vector in membership_vectors.items():
            validation = validate_membership_degrees(np.array(vector))

            assert validation['all_valid'] == True, f"Indicator {indicator_name} should be valid"
            assert len(validation['error_messages']) == 0, f"Indicator {indicator_name} should have no errors"
            assert abs(validation['sum_value'] - 1.0) < 1e-6, f"Indicator {indicator_name} sum should be 1.0"

    def test_validate_membership_degrees_invalid(self):
        """Test membership degree validation with invalid input."""
        membership_vectors = {
            'indicator_1': [0.3, 0.4, 0.3, 0.1],  # Sums to 1.1 (invalid)
            'indicator_2': [0.2, 0.3, 0.2, 0.1],  # Sums to 0.8 (invalid)
        }

        # Test each indicator separately since validate_membership_degrees expects numpy array
        for indicator_name, vector in membership_vectors.items():
            validation = validate_membership_degrees(np.array(vector))

            assert validation['all_valid'] == False, f"Indicator {indicator_name} should be invalid"
            # The function might not add error messages for all validation failures
            # Check that validation failed through the flags instead
            assert not validation['sum_to_one'], f"Indicator {indicator_name} should fail sum validation"

    def test_fuzzy_evaluate_unknown_linguistic_term(self, fuzzy_scale):
        """Test fuzzy evaluation with unknown linguistic term."""
        # Add unknown term to expert assessments
        expert_assessments = {
            '差': 0,
            '中': 0,
            '良': 1,
            '优': 0,
            'unknown_term': 1  # This should be handled gracefully
        }

        # Should handle unknown term gracefully
        result = fuzzy_evaluate(expert_assessments, fuzzy_scale)

        # Should still produce result, unknown term should be ignored or default to 0
        assert 'fuzzy_score' in result
        assert 'membership_vector' in result
        assert result['total_experts'] == 1  # Only counts known terms

    def test_fuzzy_evaluate_empty_assessments(self, fuzzy_scale):
        """Test fuzzy evaluation with empty assessments."""
        # All counts are zero - should raise FCEError
        expert_assessments = {
            '差': 0,
            '中': 0,
            '良': 0,
            '优': 0
        }

        # Should raise exception for zero total experts
        with pytest.raises(FCEError):
            fuzzy_evaluate(expert_assessments, fuzzy_scale)

    def test_fuzzy_evaluate_edge_cases(self, fuzzy_scale):
        """Test fuzzy evaluation edge cases."""
        # Test with extreme linguistic terms - all experts say "差" (worst)
        expert_assessments_worst = {
            '差': 5,  # All experts say "Poor"
            '中': 0,
            '良': 0,
            '优': 0
        }

        result_worst = fuzzy_evaluate(expert_assessments_worst, fuzzy_scale)

        # Should handle extreme values correctly
        assert 'fuzzy_score' in result_worst
        assert abs(result_worst['fuzzy_score'] - fuzzy_scale['差']) < 1e-6

        # Test with extreme linguistic terms - all experts say "优" (best)
        expert_assessments_best = {
            '差': 0,
            '中': 0,
            '良': 0,
            '优': 5   # All experts say "Excellent"
        }

        result_best = fuzzy_evaluate(expert_assessments_best, fuzzy_scale)

        # Should handle extreme values correctly
        assert 'fuzzy_score' in result_best
        assert abs(result_best['fuzzy_score'] - fuzzy_scale['优']) < 1e-6

    def test_membership_degree_normalization(self):
        """Test membership degree normalization functionality."""
        # Test with unnormalized vectors
        unnormalized_vectors = [
            [0.3, 0.4, 0.3, 0.1],  # Sums to 1.1
            [0.2, 0.3, 0.2, 0.1],  # Sums to 0.8
        ]

        for i, vector in enumerate(unnormalized_vectors):
            validation = validate_membership_degrees(np.array(vector))

            # Should identify normalization issues
            assert validation['all_valid'] == False, f"Vector {i} should be invalid"
            assert not validation['sum_to_one'], f"Vector {i} should not sum to one"

    def test_fuzzy_score_calculation_method(self, fuzzy_scale):
        """Test fuzzy score calculation method."""
        expert_assessments = {
            '差': 0,
            '中': 1,  # One assessment as 'Medium'
            '良': 2,  # Two assessments as 'Good'
            '优': 0   # No assessments as 'Excellent'
        }

        result = fuzzy_evaluate(expert_assessments, fuzzy_scale)

        # Should use weighted average method
        fuzzy_score = result['fuzzy_score']
        membership_vector = result['membership_vector']

        # Manually calculate expected weighted average
        expected_score = (0 * fuzzy_scale['差'] + 1 * fuzzy_scale['中'] +
                         2 * fuzzy_scale['良'] + 0 * fuzzy_scale['优']) / 3

        assert abs(fuzzy_score - expected_score) < 1e-6, "Should use weighted average method"

    def test_fuzzy_evaluation_data_integrity(self, fuzzy_scale):
        """Test data integrity in fuzzy evaluation results."""
        expert_assessments = {
            '差': 1,
            '中': 2,
            '良': 1,
            '优': 0
        }

        result = fuzzy_evaluate(expert_assessments, fuzzy_scale)

        # Check data structure integrity
        assert isinstance(result, dict)
        assert 'fuzzy_score' in result
        assert 'membership_vector' in result
        assert 'total_experts' in result
        assert 'valid' in result

        # Check membership vector integrity
        membership_vector = result['membership_vector']
        assert isinstance(membership_vector, np.ndarray)
        assert len(membership_vector) == 4  # Should have 4 linguistic terms

        # Check numeric types
        fuzzy_score = result['fuzzy_score']
        total_experts = result['total_experts']
        assert isinstance(fuzzy_score, (int, float, np.number))
        assert isinstance(total_experts, int)

    def test_error_handling_invalid_data(self, fuzzy_scale):
        """Test error handling with invalid data structures."""
        # Test with None assessments
        with pytest.raises((ValueError, TypeError, FCEError)):
            fuzzy_evaluate(None, fuzzy_scale)

        # Test with empty assessments
        with pytest.raises(FCEError):
            fuzzy_evaluate({}, fuzzy_scale)

        # Test with invalid fuzzy scale
        with pytest.raises(FCEError):
            fuzzy_evaluate({'差': 1, '中': 0, '良': 0, '优': 0}, {})

    def test_confidence_boundary_values(self, fuzzy_scale):
        """Test confidence values at boundaries."""
        # Test single expert assessment
        expert_assessments_single = {
            '差': 0,
            '中': 0,
            '良': 1,  # One assessment as 'Good'
            '优': 0
        }

        result_single = fuzzy_evaluate(expert_assessments_single, fuzzy_scale)
        assert 'fuzzy_score' in result_single

        # Single assessment should give the exact fuzzy scale value
        assert abs(result_single['fuzzy_score'] - fuzzy_scale['良']) < 1e-6

        # Test with multiple experts - average should be weighted
        expert_assessments_multiple = {
            '差': 0,
            '中': 0,
            '良': 5,  # Five assessments as 'Good'
            '优': 0
        }

        result_multiple = fuzzy_evaluate(expert_assessments_multiple, fuzzy_scale)
        assert 'fuzzy_score' in result_multiple

        # Multiple same assessments should still give the same fuzzy scale value
        assert abs(result_multiple['fuzzy_score'] - fuzzy_scale['良']) < 1e-6


if __name__ == '__main__':
    # Run tests if executed directly
    pytest.main([__file__, '-v'])