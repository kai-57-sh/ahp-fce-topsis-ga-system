"""
AHP (Analytic Hierarchy Process) Module

Implements Saaty's AHP method for calculating indicator weights from expert
pairwise comparison matrices with consistency validation.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import yaml
from utils.consistency_check import calculate_cr, validate_judgment_matrix, AHPConsistencyError


class AHPError(Exception):
    """Base exception for AHP module errors."""
    pass


class JudgmentMatrixError(AHPError):
    """Raised when judgment matrix is invalid."""
    pass


def calculate_weights(judgment_matrix: np.ndarray,
                     validate_consistency: bool = True,
                     cr_threshold: float = 0.1) -> Dict[str, Any]:
    """
    Calculate normalized weights from AHP judgment matrix using eigenvalue method.

    Args:
        judgment_matrix: Square numpy array of pairwise comparisons (n×n)
                        Values typically in range [1/9, 9]
                        Must satisfy reciprocal property: A[i][j] = 1/A[j][i]
        validate_consistency: Whether to validate consistency ratio
        cr_threshold: Maximum acceptable consistency ratio

    Returns:
        Dictionary containing:
            'weights': np.ndarray of normalized weights (sum = 1.0)
            'lambda_max': float, maximum eigenvalue
            'CR': float, Consistency Ratio
            'CI': float, Consistency Index
            'valid': bool, True if CR < threshold
            'validation': dict, detailed validation results

    Raises:
        JudgmentMatrixError: If matrix is invalid
        AHPConsistencyError: If CR >= threshold and validate_consistency=True
    """
    # Add robust input validation
    if judgment_matrix.size == 0:
        raise JudgmentMatrixError("Empty matrix provided")

    if not np.isfinite(judgment_matrix).all():
        raise JudgmentMatrixError("Matrix contains invalid numerical values (inf or nan)")

    # Validate matrix structure - always perform basic validation
    validation = validate_judgment_matrix(judgment_matrix)
    if not validation['is_valid']:
        # Only raise errors for critical structural issues, not reciprocal property when validation is disabled
        if not validate_consistency and "reciprocal" in str(validation['error_messages']):
            # Allow reciprocal property violations when validation is disabled
            pass
        else:
            raise JudgmentMatrixError(f"Invalid judgment matrix: {validation['error_messages']}")

    n = judgment_matrix.shape[0]

    # Calculate eigenvalues and eigenvectors using NumPy
    eigenvalues, eigenvectors = np.linalg.eig(judgment_matrix)

    # Find maximum eigenvalue (real part)
    max_eigenvalue = np.max(eigenvalues.real)
    max_eigenvalue_idx = np.argmax(eigenvalues.real)

    # Extract principal eigenvector (real part)
    principal_eigenvector = eigenvectors[:, max_eigenvalue_idx].real

    # Handle potential negative values (should not happen with consistent matrices)
    principal_eigenvector = np.abs(principal_eigenvector)

    # Normalize to sum to 1.0
    weights = principal_eigenvector / np.sum(principal_eigenvector)

    # Calculate consistency metrics
    if n == 1:
        CI = 0.0
        CR = 0.0
    else:
        CI = (max_eigenvalue - n) / (n - 1)
        # Random Index values
        RI_TABLE = {1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
                   6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
        RI = RI_TABLE.get(n, 1.59)  # Default to 1.59 for n>10
        CR = CI / RI if RI > 0 else 0.0

    # Check consistency if required
    is_valid = True
    if validate_consistency and CR >= cr_threshold:
        is_valid = False
        raise AHPConsistencyError(f"Consistency Ratio {CR:.4f} exceeds threshold {cr_threshold}")

    return {
        'weights': weights,
        'lambda_max': max_eigenvalue,
        'CI': CI,
        'CR': CR,
        'valid': is_valid,
        'validation': validation
    }


def validate_judgment_matrix(judgment_matrix: np.ndarray,
                           tolerance: float = 1e-6) -> Dict[str, Any]:
    """
    Validate AHP judgment matrix properties.

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
    return _validate_judgment_matrix(judgment_matrix, tolerance)


def _validate_judgment_matrix(judgment_matrix: np.ndarray,
                             tolerance: float = 1e-6) -> Dict[str, Any]:
    result = {
        'is_square': False,
        'positive_elements': False,
        'diagonal_ones': False,
        'reciprocal_property': False,
        'is_valid': False,
        'error_messages': []
    }

    # Check if matrix is square
    if judgment_matrix.ndim != 2:
        result['error_messages'].append("Matrix must be 2-dimensional")
        return result

    rows, cols = judgment_matrix.shape
    if rows != cols:
        result['error_messages'].append(f"Matrix must be square, got {rows}x{cols}")
        return result

    result['is_square'] = True
    n = rows

    # Check if matrix has positive elements
    if np.any(judgment_matrix <= 0):
        result['error_messages'].append("All matrix elements must be positive")
    else:
        result['positive_elements'] = True

    # Check diagonal elements (should be 1.0)
    diagonal = np.diag(judgment_matrix)
    if not np.allclose(diagonal, 1.0, atol=tolerance):
        result['error_messages'].append("Diagonal elements must be 1.0")
    else:
        result['diagonal_ones'] = True

    # Check reciprocal property: A[i][j] * A[j][i] ≈ 1.0
    reciprocal_check = judgment_matrix * judgment_matrix.T
    if not np.allclose(reciprocal_check, 1.0, atol=tolerance):
        result['error_messages'].append("Matrix must satisfy reciprocal property A[i][j] = 1/A[j][i]")
    else:
        result['reciprocal_property'] = True

    # Overall validation
    result['is_valid'] = (result['is_square'] and
                          result['positive_elements'] and
                          result['diagonal_ones'] and
                          result['reciprocal_property'])

    return result


def load_judgment_matrix(file_path: str) -> Dict[str, Any]:
    """
    Load judgment matrix from YAML file.

    Args:
        file_path: Path to YAML file containing judgment matrix

    Returns:
        Dictionary with matrix data and metadata

    Raises:
        JudgmentMatrixError: If file cannot be loaded or is invalid
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # Validate required fields
        required_fields = ['matrix_id', 'matrix']
        for field in required_fields:
            if field not in data:
                raise JudgmentMatrixError(f"Missing required field: {field}")

        # Convert matrix to numpy array
        matrix = np.array(data['matrix'], dtype=float)

        # Validate matrix dimensions
        expected_dim = data.get('dimension', matrix.shape[0])  # Use matrix size if dimension not provided
        if matrix.shape != (expected_dim, expected_dim):
            # Only raise error if dimension is explicitly provided and doesn't match
            if 'dimension' in data:
                raise JudgmentMatrixError(f"Matrix dimension mismatch: expected {expected_dim}x{expected_dim}, got {matrix.shape}")
            else:
                raise JudgmentMatrixError(f"Matrix must be square: got {matrix.shape}")

        return data

    except yaml.YAMLError as e:
        raise JudgmentMatrixError(f"Error parsing YAML file {file_path}: {e}")
    except FileNotFoundError:
        raise JudgmentMatrixError(f"File not found: {file_path}")
    except Exception as e:
        raise JudgmentMatrixError(f"Error loading judgment matrix: {e}")


def calculate_primary_weights(primary_matrix_file: str,
                            secondary_matrices_dir: str,
                            cr_threshold: float = 0.1) -> Dict[str, Any]:
    """
    Calculate complete AHP weights for primary and secondary indicators.

    Args:
        primary_matrix_file: Path to primary capabilities judgment matrix
        secondary_matrices_dir: Directory containing secondary indicator matrices
        cr_threshold: Maximum acceptable consistency ratio

    Returns:
        Dictionary containing all weights and validation results

    Raises:
        JudgmentMatrixError: If any matrix is invalid or inconsistent
    """
    results = {
        'primary_weights': {},
        'secondary_weights': {},
        'global_weights': {},
        'validation_results': {},
        'errors': []
    }

    try:
        # Calculate primary weights
        primary_data = load_judgment_matrix(primary_matrix_file)
        primary_matrix = np.array(primary_data['matrix'])
        primary_result = calculate_weights(primary_matrix, cr_threshold=cr_threshold)

        results['primary_weights'] = {
            'weights': primary_result['weights'],
            'CR': primary_result['CR'],
            'valid': primary_result['valid'],
            'matrix_id': primary_data['matrix_id']
        }

        # Calculate secondary weights for each primary capability
        primary_capabilities = ['C1', 'C2', 'C3', 'C4', 'C5']
        secondary_mapping = {
            'C1': ['C1_1', 'C1_2', 'C1_3'],
            'C2': ['C2_1', 'C2_2', 'C2_3'],
            'C3': ['C3_1', 'C3_2', 'C3_3'],
            'C4': ['C4_1', 'C4_2', 'C4_3'],
            'C5': ['C5_1', 'C5_2', 'C5_3']
        }

        global_weights = {}

        for cap_idx, cap in enumerate(primary_capabilities):
            secondary_file = f"{secondary_matrices_dir}/secondary_indicators/c{cap_idx + 1}_indicators.yaml"

            try:
                secondary_data = load_judgment_matrix(secondary_file)
                secondary_matrix = np.array(secondary_data['matrix'])
                secondary_result = calculate_weights(secondary_matrix, cr_threshold=cr_threshold)

                # Store secondary weights
                secondary_weights = secondary_result['weights']
                results['secondary_weights'][cap] = {
                    'weights': secondary_weights,
                    'CR': secondary_result['CR'],
                    'valid': secondary_result['valid'],
                    'matrix_id': secondary_data['matrix_id']
                }

                # Calculate global weights (primary weight * secondary weight)
                primary_weight = primary_result['weights'][cap_idx]
                for sec_idx, sec_indicator in enumerate(secondary_mapping[cap]):
                    global_weights[sec_indicator] = primary_weight * secondary_weights[sec_idx]

            except Exception as e:
                error_msg = f"Error processing {cap} secondary indicators: {e}"
                results['errors'].append(error_msg)
                continue

        results['global_weights'] = global_weights

        # Normalize global weights to sum to 1.0
        if global_weights:
            total_weight = sum(global_weights.values())
            results['global_weights'] = {k: v / total_weight for k, v in global_weights.items()}

    except Exception as e:
        raise JudgmentMatrixError(f"Error calculating AHP weights: {e}")

    return results


def save_weights(weights: Dict[str, Any], output_path: str) -> None:
    """
    Save calculated weights to YAML file.

    Args:
        weights: Weights dictionary to save
        output_path: Path to save the weights
    """
    # Convert numpy arrays to lists for YAML serialization
    serializable_weights = {}

    def make_serializable(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        else:
            return obj

    serializable_weights = make_serializable(weights)

    # Add metadata
    serializable_weights['metadata'] = {
        'calculated_at': np.datetime64('now').astype(str),
        'method': 'AHP eigenvalue method',
        'consistency_threshold': 0.1
    }

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(serializable_weights, f, default_flow_style=False, allow_unicode=True)
    except Exception as e:
        raise AHPError(f"Error saving weights to {output_path}: {e}")


if __name__ == "__main__":
    # Example usage and testing
    print("Testing AHP Module")

    # Test matrix from research.md
    test_matrix = np.array([
        [1.0, 2.0, 1.0],
        [0.5, 1.0, 0.5],
        [1.0, 2.0, 1.0]
    ])

    try:
        result = calculate_weights(test_matrix)
        print(f"Weights: {result['weights']}")
        print(f"CR: {result['CR']:.4f}")
        print(f"Lambda max: {result['lambda_max']:.4f}")
        print(f"Valid: {result['valid']}")

        # Test with inconsistent matrix
        inconsistent_matrix = np.array([
            [1.0, 9.0, 1.0],
            [0.11, 1.0, 0.11],
            [1.0, 9.0, 1.0]
        ])

        try:
            inconsistent_result = calculate_weights(inconsistent_matrix)
        except AHPConsistencyError as e:
            print(f"\nExpected consistency error: {e}")

    except Exception as e:
        print(f"Error: {e}")