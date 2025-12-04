"""
Normalization Utilities for TOPSIS

Provides vector normalization functions for TOPSIS algorithm implementation.
"""

import numpy as np
from typing import Tuple, Optional


def vector_normalize(decision_matrix: np.ndarray,
                    axis: int = 0,
                    avoid_division_by_zero: bool = True) -> np.ndarray:
    """
    Normalize decision matrix using vector normalization (Euclidean norm).

    Formula: r_ij = x_ij / sqrt(sum(x_ij^2 for i=1 to m))

    Args:
        decision_matrix: Input matrix to normalize (m x n)
                        m = number of alternatives/configurations
                        n = number of indicators/criteria
        axis: Axis along which to normalize
              0 = normalize each column (indicators) - standard for TOPSIS
              1 = normalize each row (configurations)
        avoid_division_by_zero: If True, add small epsilon to avoid division by zero

    Returns:
        Normalized matrix with same shape as input

    Raises:
        ValueError: If input matrix is invalid
    """
    # Validate input matrix
    if decision_matrix.ndim != 2:
        raise ValueError("Decision matrix must be 2-dimensional")

    if avoid_division_by_zero:
        # Add small epsilon to avoid division by zero
        epsilon = 1e-12
        decision_matrix = decision_matrix.copy()
        decision_matrix[np.abs(decision_matrix) < epsilon] = epsilon

    # Calculate Euclidean norm along specified axis
    norms = np.linalg.norm(decision_matrix, axis=axis, keepdims=True)

    # Handle zero norms (should not happen with avoid_division_by_zero=True)
    if np.any(norms == 0):
        raise ValueError("Zero norm encountered during normalization")

    # Perform normalization
    normalized_matrix = decision_matrix / norms

    return normalized_matrix


def min_max_normalize(decision_matrix: np.ndarray,
                     axis: int = 0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Normalize decision matrix using min-max normalization.

    Formula: r_ij = (x_ij - min(x_j)) / (max(x_j) - min(x_j))

    Args:
        decision_matrix: Input matrix to normalize (m x n)
        axis: Axis along which to normalize
              0 = normalize each column
              1 = normalize each row

    Returns:
        Tuple of (normalized_matrix, min_values, max_values)
    """
    # Calculate min and max values along specified axis
    min_values = np.min(decision_matrix, axis=axis, keepdims=True)
    max_values = np.max(decision_matrix, axis=axis, keepdims=True)

    # Calculate range
    range_values = max_values - min_values

    # Handle zero range (constant columns)
    zero_range_mask = range_values == 0
    range_values[zero_range_mask] = 1.0  # Avoid division by zero

    # Perform normalization
    normalized_matrix = (decision_matrix - min_values) / range_values

    # Set constant columns to 0.5 (neutral value)
    if axis == 0:
        normalized_matrix[:, zero_range_mask.flatten()] = 0.5
    else:
        normalized_matrix[zero_range_mask.flatten(), :] = 0.5

    return normalized_matrix, min_values.squeeze(), max_values.squeeze()


def z_score_normalize(decision_matrix: np.ndarray,
                     axis: int = 0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Normalize decision matrix using z-score (standard) normalization.

    Formula: r_ij = (x_ij - mean(x_j)) / std(x_j)

    Args:
        decision_matrix: Input matrix to normalize (m x n)
        axis: Axis along which to normalize
              0 = normalize each column
              1 = normalize each row

    Returns:
        Tuple of (normalized_matrix, means, stds)
    """
    # Calculate mean and standard deviation along specified axis
    means = np.mean(decision_matrix, axis=axis, keepdims=True)
    stds = np.std(decision_matrix, axis=axis, keepdims=True)

    # Handle zero standard deviation (constant columns)
    zero_std_mask = stds == 0
    stds[zero_std_mask] = 1.0  # Avoid division by zero

    # Perform normalization
    normalized_matrix = (decision_matrix - means) / stds

    # Set constant columns to 0 (z-score of constant)
    if axis == 0:
        normalized_matrix[:, zero_std_mask.flatten()] = 0.0
    else:
        normalized_matrix[zero_std_mask.flatten(), :] = 0.0

    return normalized_matrix, means.squeeze(), stds.squeeze()


def check_normalization_properties(normalized_matrix: np.ndarray,
                                axis: int = 0,
                                tolerance: float = 1e-10) -> dict:
    """
    Check if vector normalization was performed correctly.

    Args:
        normalized_matrix: Matrix to check
        axis: Axis that was normalized
        tolerance: Numerical tolerance for checks

    Returns:
        Dictionary with validation results
    """
    results = {
        'has_negative_values': False,
        'normalized_to_unit_length': True,
        'zero_variance_indicators': [],
        'validation_errors': []
    }

    # Check for negative values
    if np.any(normalized_matrix < 0):
        results['has_negative_values'] = True
        results['validation_errors'].append("Negative values found in normalized matrix")

    # Check unit length property (for vector normalization)
    if axis == 0:
        # Check each column
        column_norms = np.linalg.norm(normalized_matrix, axis=0)
        if not np.allclose(column_norms, 1.0, atol=tolerance):
            results['normalized_to_unit_length'] = False
            results['validation_errors'].append(f"Columns not normalized to unit length: {column_norms}")
    else:
        # Check each row
        row_norms = np.linalg.norm(normalized_matrix, axis=1)
        if not np.allclose(row_norms, 1.0, atol=tolerance):
            results['normalized_to_unit_length'] = False
            results['validation_errors'].append(f"Rows not normalized to unit length: {row_norms}")

    # Check for zero variance indicators
    if axis == 0:
        column_stds = np.std(normalized_matrix, axis=0)
        zero_var_indices = np.where(column_stds < tolerance)[0]
        results['zero_variance_indicators'] = zero_var_indices.tolist()
    else:
        row_stds = np.std(normalized_matrix, axis=1)
        zero_var_indices = np.where(row_stds < tolerance)[0]
        results['zero_variance_indicators'] = zero_var_indices.tolist()

    return results


def handle_zero_variance_indicators(decision_matrix: np.ndarray,
                                  axis: int = 0,
                                  replacement_value: Optional[float] = None) -> np.ndarray:
    """
    Handle indicators with zero variance (all values identical).

    Args:
        decision_matrix: Input matrix
        axis: Axis to check for zero variance
        replacement_value: Value to use for zero variance indicators
                          If None, uses small epsilon

    Returns:
        Matrix with zero variance handled
    """
    if replacement_value is None:
        replacement_value = 1e-6

    result_matrix = decision_matrix.copy()

    if axis == 0:
        # Check each column
        column_stds = np.std(decision_matrix, axis=0)
        zero_var_mask = column_stds < 1e-12
        result_matrix[:, zero_var_mask] = replacement_value
    else:
        # Check each row
        row_stds = np.std(decision_matrix, axis=1)
        zero_var_mask = row_stds < 1e-12
        result_matrix[zero_var_mask, :] = replacement_value

    return result_matrix


if __name__ == "__main__":
    # Example usage and testing
    test_matrix = np.array([
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0],
        [1.0, 2.0, 3.0]  # Duplicate row for testing
    ])

    print("Testing Normalization Utilities")
    print("Original Matrix:")
    print(test_matrix)

    # Test vector normalization
    print("\nVector Normalization (column-wise):")
    vector_norm = vector_normalize(test_matrix, axis=0)
    print(vector_norm)

    # Check properties
    properties = check_normalization_properties(vector_norm, axis=0)
    print(f"Normalized correctly: {properties['normalized_to_unit_length']}")
    print(f"Negative values: {properties['has_negative_values']}")

    # Test min-max normalization
    print("\nMin-Max Normalization (column-wise):")
    minmax_norm, mins, maxs = min_max_normalize(test_matrix, axis=0)
    print(minmax_norm)
    print(f"Min values: {mins}")
    print(f"Max values: {maxs}")

    # Test zero variance handling
    print("\nZero Variance Test:")
    zero_var_matrix = np.array([
        [1.0, 2.0],
        [1.0, 2.0],
        [1.0, 2.0]
    ])
    print("Matrix with zero variance:")
    print(zero_var_matrix)

    handled = handle_zero_variance_indicators(zero_var_matrix, axis=0)
    print("After handling zero variance:")
    print(handled)