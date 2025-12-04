"""
AHP Consistency Check Utilities

Provides functions for calculating consistency ratio (CR) and validating
expert judgment matrices according to Saaty's AHP methodology.
"""

import numpy as np
from typing import Dict, Tuple, Optional


# Random Index (RI) values for consistency ratio calculation
# Source: Saaty (2008) and standard AHP literature
RANDOM_INDEX_TABLE = {
    1: 0.00,   # n=1
    2: 0.00,   # n=2
    3: 0.58,   # n=3
    4: 0.90,   # n=4
    5: 1.12,   # n=5
    6: 1.24,   # n=6
    7: 1.32,   # n=7
    8: 1.41,   # n=8
    9: 1.45,   # n=9
    10: 1.49,  # n=10
    11: 1.51,  # n=11
    12: 1.48,  # n=12
    13: 1.56,  # n=13
    14: 1.57,  # n=14
    15: 1.59,  # n=15
}


class AHPConsistencyError(Exception):
    """Raised when AHP consistency ratio exceeds acceptable threshold."""
    pass


def calculate_cr(judgment_matrix: np.ndarray,
                tolerance: float = 1e-6) -> Dict[str, float]:
    """
    Calculate Consistency Ratio (CR) for AHP judgment matrix.

    Args:
        judgment_matrix: Square numpy array of pairwise comparisons
        tolerance: Numerical tolerance for matrix consistency checks

    Returns:
        Dictionary containing:
            - 'CR': Consistency Ratio
            - 'CI': Consistency Index
            - 'lambda_max': Maximum eigenvalue
            - 'RI': Random Index value
            - 'n': Matrix dimension

    Raises:
        ValueError: If matrix is invalid
        AHPConsistencyError: If CR >= 0.1
    """
    # Validate input matrix
    if not is_valid_matrix(judgment_matrix):
        raise ValueError("Invalid judgment matrix: must be square with positive elements")

    n = judgment_matrix.shape[0]

    # Calculate eigenvalues and eigenvectors
    eigenvalues, eigenvectors = np.linalg.eig(judgment_matrix)

    # Get maximum eigenvalue (real part)
    lambda_max = np.max(eigenvalues.real)

    # Calculate Consistency Index (CI)
    if n == 1:
        CI = 0.0
    else:
        CI = (lambda_max - n) / (n - 1)

    # Get Random Index (RI) for matrix size
    RI = RANDOM_INDEX_TABLE.get(n, RANDOM_INDEX_TABLE[15])  # Default to n=15 RI

    # Calculate Consistency Ratio (CR)
    if RI > 0:
        CR = CI / RI
    else:
        CR = 0.0

    result = {
        'CR': CR,
        'CI': CI,
        'lambda_max': lambda_max,
        'RI': RI,
        'n': n
    }

    # Check consistency threshold
    if CR >= 0.1:
        raise AHPConsistencyError(f"Consistency Ratio {CR:.4f} exceeds threshold 0.1")

    return result


def calculate_weights(judgment_matrix: np.ndarray) -> np.ndarray:
    """
    Calculate normalized weights from AHP judgment matrix using eigenvalue method.

    Args:
        judgment_matrix: Square numpy array of pairwise comparisons

    Returns:
        Normalized weight vector (sums to 1.0)

    Raises:
        ValueError: If matrix is invalid
    """
    # Validate input matrix
    if not is_valid_matrix(judgment_matrix):
        raise ValueError("Invalid judgment matrix: must be square with positive elements")

    # Calculate eigenvalues and eigenvectors
    eigenvalues, eigenvectors = np.linalg.eig(judgment_matrix)

    # Find index of maximum eigenvalue
    max_eigenvalue_idx = np.argmax(eigenvalues.real)

    # Extract principal eigenvector (real part)
    principal_eigenvector = eigenvectors[:, max_eigenvalue_idx].real

    # Handle potential negative values (should not happen with consistent matrices)
    principal_eigenvector = np.abs(principal_eigenvector)

    # Normalize to sum to 1.0
    weights = principal_eigenvector / np.sum(principal_eigenvector)

    return weights


def is_valid_matrix(judgment_matrix: np.ndarray,
                   tolerance: float = 1e-6) -> bool:
    """
    Validate AHP judgment matrix properties.

    Args:
        judgment_matrix: Matrix to validate
        tolerance: Numerical tolerance for comparisons

    Returns:
        True if matrix is valid, False otherwise
    """
    # Check if matrix is square
    if judgment_matrix.ndim != 2:
        return False

    rows, cols = judgment_matrix.shape
    if rows != cols:
        return False

    # Check if matrix has positive elements
    if np.any(judgment_matrix <= 0):
        return False

    # Check diagonal elements (should be 1.0)
    diagonal = np.diag(judgment_matrix)
    if not np.allclose(diagonal, 1.0, atol=tolerance):
        return False

    # Check reciprocal property: A[i][j] * A[j][i] ≈ 1.0
    reciprocal_check = judgment_matrix * judgment_matrix.T
    if not np.allclose(reciprocal_check, 1.0, atol=tolerance):
        return False

    return True


def validate_judgment_matrix(judgment_matrix: np.ndarray,
                           tolerance: float = 1e-6) -> Dict[str, bool]:
    """
    Perform comprehensive validation of AHP judgment matrix.

    Args:
        judgment_matrix: Matrix to validate
        tolerance: Numerical tolerance for comparisons

    Returns:
        Dictionary with validation results:
            - 'is_square': Matrix is square
            - 'positive_elements': All elements are positive
            - 'diagonal_ones': Diagonal elements are 1.0
            - 'reciprocal_property': Reciprocal property holds
            - 'is_valid': Overall validation result
            - 'error_messages': List of validation errors
    """
    results = {
        'is_square': False,
        'positive_elements': False,
        'diagonal_ones': False,
        'reciprocal_property': False,
        'is_valid': False,
        'error_messages': []
    }

    # Check if matrix is square
    if judgment_matrix.ndim != 2:
        results['error_messages'].append("Matrix must be 2-dimensional")
        return results

    rows, cols = judgment_matrix.shape
    if rows != cols:
        results['error_messages'].append(f"Matrix must be square, got {rows}x{cols}")
        return results

    results['is_square'] = True
    n = rows

    # Check positive elements
    if np.any(judgment_matrix <= 0):
        results['error_messages'].append("All matrix elements must be positive")
    else:
        results['positive_elements'] = True

    # Check diagonal elements
    diagonal = np.diag(judgment_matrix)
    if not np.allclose(diagonal, 1.0, atol=tolerance):
        results['error_messages'].append("Diagonal elements must be 1.0")
    else:
        results['diagonal_ones'] = True

    # Check reciprocal property
    reciprocal_check = judgment_matrix * judgment_matrix.T
    if not np.allclose(reciprocal_check, 1.0, atol=tolerance):
        results['error_messages'].append("Matrix must satisfy reciprocal property A[i][j] = 1/A[j][i]")
    else:
        results['reciprocal_property'] = True

    # Overall validation
    results['is_valid'] = (results['is_square'] and
                          results['positive_elements'] and
                          results['diagonal_ones'] and
                          results['reciprocal_property'])

    return results


def get_random_index(matrix_size: int) -> float:
    """
    Get Random Index (RI) value for given matrix size.

    Args:
        matrix_size: Size of square matrix (n)

    Returns:
        RI value for the given matrix size
    """
    return RANDOM_INDEX_TABLE.get(matrix_size, RANDOM_INDEX_TABLE[15])


if __name__ == "__main__":
    # Example usage and testing
    test_matrix = np.array([
        [1.0, 2.0, 1.0],
        [0.5, 1.0, 0.5],
        [1.0, 2.0, 1.0]
    ])

    print("Testing AHP Consistency Check")
    print("Test Matrix:")
    print(test_matrix)

    try:
        cr_result = calculate_cr(test_matrix)
        weights = calculate_weights(test_matrix)
        validation = validate_judgment_matrix(test_matrix)

        print(f"\nWeights: {weights}")
        print(f"CR: {cr_result['CR']:.4f}")
        print(f"CI: {cr_result['CI']:.4f}")
        print(f"Lambda max: {cr_result['lambda_max']:.4f}")
        print(f"Validation: {validation['is_valid']}")

    except Exception as e:
        print(f"Error: {e}")