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
        expert_assessments = {
            'expert_001': {
                'assessments': {
                    'C1_1': {'linguistic_term': '良', 'confidence': 0.9}
                }
            },
            'expert_002': {
                'assessments': {
                    'C1_1': {'linguistic_term': '优', 'confidence': 0.8}
                }
            },
            'expert_003': {
                'assessments': {
                    'C1_1': {'linguistic_term': '中', 'confidence': 0.7}
                }
            }
        }

        result = fuzzy_evaluate(expert_assessments, fuzzy_scale)

        # Should aggregate multiple expert opinions
        assert 'fuzzy_scores' in result
        assert len(result['fuzzy_scores']) > 0

        # Check that multiple experts were considered
        for indicator_id, score_data in result['fuzzy_scores'].items():
            assert 'expert_scores' in score_data
            assert len(score_data['expert_scores']) == 3

    def test_fuzzy_evaluate_with_confidence_weights(self, fuzzy_scale):
        """Test fuzzy evaluation considers expert confidence."""
        expert_assessments = {
            'expert_001': {
                'assessments': {
                    'C1_1': {'linguistic_term': '良', 'confidence': 0.9}  # High confidence
                }
            },
            'expert_002': {
                'assessments': {
                    'C1_1': {'linguistic_term': '优', 'confidence': 0.1}  # Low confidence
                }
            }
        }

        result = fuzzy_evaluate(expert_assessments, fuzzy_scale)

        # Result should be closer to the high-confidence assessment
        score_data = result['fuzzy_scores']['C1_1']
        assert 'fuzzy_score' in score_data

        # High confidence (良 = 0.75) should have more influence than low confidence (优 = 1.0)
        # So result should be closer to 0.75 than 1.0
        fuzzy_score = score_data['fuzzy_score']
        assert fuzzy_score < 0.9, f"Score {fuzzy_score} should be closer to 0.75 than 1.0 due to confidence weighting"

    def test_validate_membership_degrees_valid(self):
        """Test membership degree validation with valid input."""
        membership_vectors = {
            'indicator_1': [0.25, 0.50, 0.25, 0.0],  # Sums to 1.0
            'indicator_2': [0.0, 0.75, 0.25, 0.0],    # Sums to 1.0
            'indicator_3': [1.0, 0.0, 0.0, 0.0]       # Sums to 1.0
        }

        validation = validate_membership_degrees(membership_vectors)

        assert validation['valid'] == True
        assert len(validation['errors']) == 0
        assert all(abs(sum_val - 1.0) < 1e-6 for sum_val in validation['membership_sums'].values())

    def test_validate_membership_degrees_invalid(self):
        """Test membership degree validation with invalid input."""
        membership_vectors = {
            'indicator_1': [0.3, 0.4, 0.3, 0.1],  # Sums to 1.1 (invalid)
            'indicator_2': [0.2, 0.3, 0.2, 0.1],  # Sums to 0.8 (invalid)
        }

        validation = validate_membership_degrees(membership_vectors)

        assert validation['valid'] == False
        assert len(validation['errors']) > 0

    def test_fuzzy_evaluate_unknown_linguistic_term(self, fuzzy_scale):
        """Test fuzzy evaluation with unknown linguistic term."""
        expert_assessments = {
            'expert_001': {
                'assessments': {
                    'C1_1': {'linguistic_term': 'unknown_term', 'confidence': 0.8}
                }
            }
        }

        # Should handle unknown term gracefully
        result = fuzzy_evaluate(expert_assessments, fuzzy_scale)

        # Should still produce result, possibly with default or error handling
        assert 'fuzzy_scores' in result
        assert 'validation' in result

    def test_fuzzy_evaluate_empty_assessments(self, fuzzy_scale):
        """Test fuzzy evaluation with empty assessments."""
        expert_assessments = {
            'expert_001': {
                'assessments': {}
            }
        }

        # Should handle empty assessments gracefully
        result = fuzzy_evaluate(expert_assessments, fuzzy_scale)

        assert 'fuzzy_scores' in result
        assert len(result['fuzzy_scores']) == 0

    def test_fuzzy_evaluate_edge_cases(self, fuzzy_scale):
        """Test fuzzy evaluation edge cases."""
        # Test with extreme linguistic terms
        expert_assessments = {
            'expert_001': {
                'assessments': {
                    'C1_1': {'linguistic_term': '差', 'confidence': 1.0},  # Worst case
                    'C1_2': {'linguistic_term': '优', 'confidence': 1.0}   # Best case
                }
            }
        }

        result = fuzzy_evaluate(expert_assessments, fuzzy_scale)

        # Should handle extreme values correctly
        assert 'fuzzy_scores' in result
        for indicator_id, score_data in result['fuzzy_scores'].items():
            fuzzy_score = score_data['fuzzy_score']
            assert 0.0 <= fuzzy_score <= 1.0

    def test_membership_degree_normalization(self):
        """Test membership degree normalization functionality."""
        # Test with unnormalized vectors
        unnormalized_vectors = {
            'indicator_1': [0.3, 0.4, 0.3, 0.1],  # Sums to 1.1
            'indicator_2': [0.2, 0.3, 0.2, 0.1],  # Sums to 0.8
        }

        validation = validate_membership_degrees(unnormalized_vectors)

        # Should identify normalization issues
        assert validation['valid'] == False
        assert 'normalization_required' in validation['errors'][0].lower()

    def test_fuzzy_score_calculation_method(self, fuzzy_scale):
        """Test fuzzy score calculation method."""
        expert_assessments = {
            'expert_001': {
                'assessments': {
                    'C1_1': {
                        'linguistic_term': '良',
                        'confidence': 0.8,
                        'membership_vector': [0.0, 0.2, 0.8, 0.0]  # Pre-calculated membership
                    }
                }
            }
        }

        result = fuzzy_evaluate(expert_assessments, fuzzy_scale)

        # Should use weighted average method
        score_data = result['fuzzy_scores']['C1_1']
        assert 'calculation_method' in score_data
        assert score_data['calculation_method'] == 'weighted_average'

    def test_fuzzy_evaluation_data_integrity(self, fuzzy_scale):
        """Test data integrity in fuzzy evaluation results."""
        expert_assessments = {
            'expert_001': {
                'assessments': {
                    'C1_1': {'linguistic_term': '良', 'confidence': 0.9},
                    'C1_2': {'linguistic_term': '中', 'confidence': 0.8}
                }
            }
        }

        result = fuzzy_evaluate(expert_assessments, fuzzy_scale)

        # Check data structure integrity
        assert isinstance(result, dict)
        assert 'fuzzy_scores' in result
        assert 'overall_score' in result
        assert 'validation' in result

        # Check nested structure integrity
        for indicator_id, score_data in result['fuzzy_scores'].items():
            assert isinstance(score_data, dict)
            assert 'fuzzy_score' in score_data
            assert 'membership_vector' in score_data

        # Check numeric types
        overall_score = result['overall_score']
        assert isinstance(overall_score, (int, float, np.number))

    def test_error_handling_invalid_data(self, fuzzy_scale):
        """Test error handling with invalid data structures."""
        # Test with None assessments
        with pytest.raises((ValueError, TypeError, FCEError)):
            fuzzy_evaluate(None, fuzzy_scale)

        # Test with invalid fuzzy scale
        with pytest.raises((ValueError, KeyError, FCEError)):
            fuzzy_evaluate({}, {})

    def test_confidence_boundary_values(self, fuzzy_scale):
        """Test confidence values at boundaries."""
        # Test with confidence = 0
        expert_assessments_zero_conf = {
            'expert_001': {
                'assessments': {
                    'C1_1': {'linguistic_term': '良', 'confidence': 0.0}
                }
            }
        }

        result_zero = fuzzy_evaluate(expert_assessments_zero_conf, fuzzy_scale)
        assert 'fuzzy_scores' in result

        # Test with confidence = 1
        expert_assessments_full_conf = {
            'expert_001': {
                'assessments': {
                    'C1_1': {'linguistic_term': '良', 'confidence': 1.0}
                }
            }
        }

        result_full = fuzzy_evaluate(expert_assessments_full_conf, fuzzy_scale)
        assert 'fuzzy_scores' in result

        # Results should be different due to confidence weighting
        score_zero = result_zero['fuzzy_scores']['C1_1']['fuzzy_score']
        score_full = result_full['fuzzy_scores']['C1_1']['fuzzy_score']

        # Full confidence should give the exact fuzzy scale value
        assert abs(score_full - fuzzy_scale['良']) < 1e-6


if __name__ == '__main__':
    # Run tests if executed directly
    pytest.main([__file__, '-v'])