"""
Unit Tests for AHP Module

Tests AHP weight calculation, consistency validation, and matrix processing.
"""

import pytest
import numpy as np
import yaml
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from modules.ahp_module import calculate_weights, validate_judgment_matrix, load_judgment_matrix, JudgmentMatrixError
from utils.consistency_check import AHPConsistencyError


class TestAHPModule:
    """Test cases for AHP module functionality."""

    @pytest.fixture
    def sample_matrices(self):
        """Load sample matrices from fixtures."""
        fixture_path = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'sample_matrices.yaml')
        with open(fixture_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def test_calculate_weights_valid_matrix(self, sample_matrices):
        """Test weight calculation with valid consistent matrix."""
        matrix_data = sample_matrices['valid_matrix_3x3']
        matrix = np.array(matrix_data['matrix'])

        result = calculate_weights(matrix, validate_consistency=True)

        # Check basic structure
        assert 'weights' in result
        assert 'CR' in result
        assert 'lambda_max' in result
        assert 'valid' in result

        # Check consistency
        assert result['valid'] == True
        assert result['CR'] <= 0.1

        # Check weights sum to 1
        weight_sum = sum(result['weights'])
        assert abs(weight_sum - 1.0) < 1e-6, f"Weights sum to {weight_sum}, expected 1.0"

        # Check weights are positive
        assert all(w > 0 for w in result['weights']), "All weights should be positive"

        # Check number of weights matches matrix size
        assert len(result['weights']) == matrix.shape[0]

    def test_calculate_weights_invalid_cr(self, sample_matrices):
        """Test weight calculation with inconsistent matrix."""
        matrix_data = sample_matrices['invalid_matrix_inconsistent']
        matrix = np.array(matrix_data['matrix'])

        # The test matrix violates reciprocal property, so calculate_weights should raise JudgmentMatrixError
        try:
            result = calculate_weights(matrix, validate_consistency=True)
            # If it doesn't raise an exception, the validation should catch the issue
            assert result['valid'] == False, "Matrix with reciprocal violation should be invalid"
        except JudgmentMatrixError:
            # This is expected for matrices that violate reciprocal property
            pass

    def test_calculate_weights_without_validation(self, sample_matrices):
        """Test weight calculation without consistency validation."""
        matrix_data = sample_matrices['invalid_matrix_inconsistent']
        matrix = np.array(matrix_data['matrix'])

        # Should not raise exception when validation is disabled
        result = calculate_weights(matrix, validate_consistency=False)

        # Should still calculate weights
        assert 'weights' in result
        assert 'CR' in result
        assert len(result['weights']) == matrix.shape[0]

    def test_validate_judgment_matrix_reciprocal_violation(self, sample_matrices):
        """Test matrix validation with reciprocal property violation."""
        matrix_data = sample_matrices['invalid_matrix_no_reciprocal']
        matrix = np.array(matrix_data['matrix'])

        # Should fail validation due to reciprocal violation
        result = validate_judgment_matrix(matrix)
        assert result['is_valid'] == False, "Matrix with reciprocal violation should be invalid"

    def test_validate_judgment_matrix_not_square(self, sample_matrices):
        """Test matrix validation with non-square matrix."""
        matrix_data = sample_matrices['invalid_matrix_not_square']
        matrix = np.array(matrix_data['matrix'])

        # Should fail validation due to non-square matrix
        result = validate_judgment_matrix(matrix)
        assert result['is_valid'] == False, "Non-square matrix should be invalid"

    def test_validate_judgment_matrix_wrong_diagonal(self, sample_matrices):
        """Test matrix validation with incorrect diagonal elements."""
        matrix_data = sample_matrices['invalid_matrix_wrong_diagonal']
        matrix = np.array(matrix_data['matrix'])

        # Should fail validation due to non-unit diagonal
        result = validate_judgment_matrix(matrix)
        assert result['is_valid'] == False, "Non-unit diagonal matrix should be invalid"

    def test_validate_judgment_matrix_valid(self, sample_matrices):
        """Test matrix validation with valid matrix."""
        matrix_data = sample_matrices['valid_matrix_5x5']
        matrix = np.array(matrix_data['matrix'])

        # Should pass validation
        result = validate_judgment_matrix(matrix)
        assert result['is_valid'] == True, "Valid matrix should pass validation"

    def test_calculate_weights_perfect_consistency(self, sample_matrices):
        """Test weight calculation with perfectly consistent matrix."""
        matrix_data = sample_matrices['valid_matrix_3x3']
        matrix = np.array(matrix_data['matrix'])

        result = calculate_weights(matrix, validate_consistency=True)

        # Perfectly consistent matrix should have CR = 0
        assert abs(result['CR'] - 0.0) < 1e-6, f"Expected CR ≈ 0, got {result['CR']}"

        # Should be valid
        assert result['valid'] == True

    def test_calculate_weights_large_matrix(self, sample_matrices):
        """Test weight calculation with larger matrix."""
        matrix_data = sample_matrices['valid_matrix_5x5']
        matrix = np.array(matrix_data['matrix'])

        result = calculate_weights(matrix, validate_consistency=True)

        # Should handle larger matrices correctly
        assert len(result['weights']) == 5
        assert result['valid'] == True
        assert result['CR'] <= 0.1

    def test_load_judgment_matrix(self):
        """Test loading judgment matrix from YAML file."""
        # Create a temporary YAML file for testing
        test_matrix = {
            'matrix_id': 'test_load',
            'matrix': [
                [1.0, 2.0, 3.0],
                [0.5, 1.0, 1.5],
                [0.333, 0.667, 1.0]
            ]
        }

        # Write to temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_matrix, f)
            temp_path = f.name

        try:
            # Test loading
            result = load_judgment_matrix(temp_path)

            assert 'matrix' in result
            assert 'matrix_id' in result
            assert result['matrix_id'] == 'test_load'
            assert len(result['matrix']) == 3

        finally:
            # Clean up
            os.unlink(temp_path)

    def test_calculate_weights_random_matrix_properties(self):
        """Test mathematical properties of weight calculation with random matrix."""
        # Generate a random positive reciprocal matrix
        np.random.seed(42)  # For reproducibility
        n = 4

        # Create random matrix ensuring reciprocal property
        matrix = np.ones((n, n))
        for i in range(n):
            for j in range(i+1, n):
                # Generate random comparison
                comparison = np.random.uniform(0.2, 5.0)
                matrix[i, j] = comparison
                matrix[j, i] = 1.0 / comparison

        result = calculate_weights(matrix, validate_consistency=False)

        # Test mathematical properties
        assert len(result['weights']) == n
        assert abs(sum(result['weights']) - 1.0) < 1e-10
        assert all(w > 0 for w in result['weights'])
        assert result['lambda_max'] >= n  # Should be >= matrix size

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test 2x2 matrix (smallest valid size)
        matrix_2x2 = np.array([
            [1.0, 2.0],
            [0.5, 1.0]
        ])

        result = calculate_weights(matrix_2x2, validate_consistency=True)
        assert len(result['weights']) == 2
        assert abs(sum(result['weights']) - 1.0) < 1e-6

    def test_error_handling_invalid_input(self):
        """Test error handling with invalid inputs."""
        # Test with empty matrix - should handle gracefully
        try:
            result = calculate_weights(np.array([]), validate_consistency=True)
            # If it doesn't raise exception, check result
            assert 'valid' in result
        except (ValueError, AHPConsistencyError):
            # Exception handling is also acceptable
            pass

        # Test with matrix containing invalid values
        matrix_with_zeros = np.array([
            [1.0, 0.0],
            [float('inf'), 1.0]  # This would create an invalid reciprocal
        ])

        try:
            result = calculate_weights(matrix_with_zeros, validate_consistency=True)
            # If it doesn't raise exception, check result
            assert 'valid' in result
        except (ValueError, AHPConsistencyError):
            # Exception handling is also acceptable
            pass

    def test_consistency_ratio_calculation(self):
        """Test specific consistency ratio calculation."""
        # Known test case with expected CR
        matrix = np.array([
            [1, 3, 5],
            [1/3, 1, 2],
            [1/5, 1/2, 1]
        ])

        result = calculate_weights(matrix, validate_consistency=False)

        # For this matrix, CR should be approximately 0.003 (very consistent)
        assert result['CR'] < 0.1
        assert result['CR'] > 0.0

        # Lambda max should be > n for positive reciprocal matrices
        assert result['lambda_max'] > 3.0


if __name__ == '__main__':
    # Run tests if executed directly
    pytest.main([__file__, '-v'])