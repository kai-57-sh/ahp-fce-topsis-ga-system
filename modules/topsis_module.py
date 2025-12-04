"""
TOPSIS (Technique for Order Preference by Similarity to Ideal Solution) Module

Implements TOPSIS method for ranking alternatives based on distance to
positive and negative ideal solutions.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from utils.normalization import vector_normalize, check_normalization_properties


class TOPSISError(Exception):
    """Base exception for TOPSIS module errors."""
    pass


class DataValidationError(TOPSISError):
    """Raised when input data validation fails."""
    pass


def topsis_rank(decision_matrix: np.ndarray,
               weights: np.ndarray,
               indicator_types: List[str],
               validate_input: bool = True) -> Dict[str, Any]:
    """
    Perform TOPSIS ranking of alternatives.

    Args:
        decision_matrix: Decision matrix (alternatives × indicators)
                         Shape: (m, n) where m = alternatives, n = indicators
        weights: Weight vector for indicators (shape: n,)
        indicator_types: List indicating each indicator type
                          'benefit' for beneficial indicators (higher is better)
                          'cost' for cost indicators (lower is better)
        validate_input: Whether to validate input data

    Returns:
        Dictionary containing:
            'Ci': np.ndarray of relative closeness coefficients (0 to 1)
            'rankings': np.ndarray of rankings (1 = best)
            'PIS': np.ndarray of positive ideal solution
            'NIS': np.ndarray of negative ideal solution
            'D_plus': np.ndarray of distances to PIS
            'D_minus': np.ndarray of distances to NIS
            'normalized_matrix': np.ndarray of normalized decision matrix
            'weighted_matrix': np.ndarray of weighted normalized matrix
            'validation': dict with validation results

    Raises:
        DataValidationError: If input data is invalid
        TOPSISError: If TOPSIS calculation fails
    """
    # Validate input data
    if validate_input:
        _validate_topsis_input(decision_matrix, weights, indicator_types)

    m, n = decision_matrix.shape  # m alternatives, n indicators

    # Step 1: Normalize decision matrix using vector normalization
    normalized_matrix = vector_normalize(decision_matrix, axis=0)

    # Step 2: Apply weights to normalized matrix
    weighted_matrix = normalized_matrix * weights

    # Step 3: Identify positive and negative ideal solutions
    PIS, NIS = identify_ideal_solutions(weighted_matrix, indicator_types)

    # Step 4: Calculate distances to ideal solutions
    D_plus = np.linalg.norm(weighted_matrix - PIS, axis=1)  # Distance to PIS
    D_minus = np.linalg.norm(weighted_matrix - NIS, axis=1)  # Distance to NIS

    # Step 5: Calculate relative closeness coefficients
    # Ci = D_minus / (D_plus + D_minus)
    # Handle potential division by zero (when D_plus + D_minus = 0)
    denominator = D_plus + D_minus
    # Check for zero denominator and handle appropriately
    zero_denominator_mask = denominator < 1e-15  # Use small epsilon for numerical stability
    Ci = np.zeros_like(denominator)

    # Normal case: calculate Ci
    normal_mask = ~zero_denominator_mask
    if np.any(normal_mask):
        Ci[normal_mask] = D_minus[normal_mask] / denominator[normal_mask]

    # Edge case: when denominator is zero (alternatives are identical)
    if np.any(zero_denominator_mask):
        # For identical alternatives, assign equal Ci values (0.5 is neutral)
        Ci[zero_denominator_mask] = 0.5

    # Step 6: Rank alternatives based on Ci (higher Ci = better rank)
    rankings = len(Ci) - np.argsort(Ci).argsort()  # Convert to 1-based ranking

    # Validate results
    validation_results = _validate_topsis_results(Ci, rankings, D_plus, D_minus)

    return {
        'Ci': Ci,
        'rankings': rankings,
        'PIS': PIS,
        'NIS': NIS,
        'D_plus': D_plus,
        'D_minus': D_minus,
        'normalized_matrix': normalized_matrix,
        'weighted_matrix': weighted_matrix,
        'validation': validation_results
    }


def identify_ideal_solutions(weighted_matrix: np.ndarray,
                          indicator_types: List[str]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Identify Positive Ideal Solution (PIS) and Negative Ideal Solution (NIS).

    Args:
        weighted_matrix: Weighted normalized decision matrix
        indicator_types: List of indicator types ('benefit' or 'cost')

    Returns:
        Tuple of (PIS, NIS) as numpy arrays

    Raises:
        DataValidationError: If indicator types are invalid
    """
    # Validate indicator types
    valid_types = {'benefit', 'cost'}
    for ind_type in indicator_types:
        if ind_type not in valid_types:
            raise DataValidationError(f"Invalid indicator type: {ind_type}. Must be 'benefit' or 'cost'")

    weighted_matrix = np.array(weighted_matrix)

    # Initialize PIS and NIS arrays
    n_indicators = weighted_matrix.shape[1]
    PIS = np.zeros(n_indicators)
    NIS = np.zeros(n_indicators)

    # For each indicator, determine ideal values
    for j in range(n_indicators):
        column_values = weighted_matrix[:, j]

        if indicator_types[j] == 'benefit':
            # For benefit indicators: PIS = max, NIS = min
            PIS[j] = np.max(column_values)
            NIS[j] = np.min(column_values)
        else:  # cost indicator
            # For cost indicators: PIS = min, NIS = max
            PIS[j] = np.min(column_values)
            NIS[j] = np.max(column_values)

    return PIS, NIS


def _validate_topsis_input(decision_matrix: np.ndarray,
                          weights: np.ndarray,
                          indicator_types: List[str]) -> None:
    """
    Validate TOPSIS input data.

    Args:
        decision_matrix: Decision matrix to validate
        weights: Weight vector to validate
        indicator_types: Indicator types to validate

    Raises:
        DataValidationError: If validation fails
    """
    # Check decision matrix dimensions
    if decision_matrix.ndim != 2:
        raise DataValidationError("Decision matrix must be 2-dimensional")

    m, n = decision_matrix.shape
    if m < 2:
        raise DataValidationError("Need at least 2 alternatives for ranking")
    if n < 2:
        raise DataValidationError("Need at least 2 indicators for evaluation")

    # Check for negative values
    if np.any(decision_matrix < 0):
        raise DataValidationError("Decision matrix contains negative values")

    # Check weights dimensions
    if weights.ndim != 1:
        raise DataValidationError("Weights must be 1-dimensional array")

    if len(weights) != n:
        raise DataValidationError(f"Weights length ({len(weights)}) must match number of indicators ({n})")

    # Check weights validity
    if np.any(weights <= 0):
        raise DataValidationError("All weights must be positive")

    weight_sum = np.sum(weights)
    if abs(weight_sum - 1.0) > 1e-6:
        raise DataValidationError(f"Weights must sum to 1.0, got {weight_sum:.6f}")

    # Check indicator types
    if len(indicator_types) != n:
        raise DataValidationError(f"Indicator types length ({len(indicator_types)}) must match number of indicators ({n})")


def _validate_topsis_results(Ci: np.ndarray,
                           rankings: np.ndarray,
                           D_plus: np.ndarray,
                           D_minus: np.ndarray) -> Dict[str, Any]:
    """
    Validate TOPSIS calculation results.

    Args:
        Ci: Relative closeness coefficients
        rankings: Alternative rankings
        D_plus: Distances to PIS
        D_minus: Distances to NIS

    Returns:
        Dictionary with validation results
    """
    validation = {
        'valid': True,
        'warnings': [],
        'errors': []
    }

    # Check Ci range [0, 1]
    if np.any(Ci < 0) or np.any(Ci > 1):
        validation['errors'].append(f"Ci values must be in [0, 1], got range [{np.min(Ci):.3f}, {np.max(Ci):.3f}]")
        validation['valid'] = False

    # Check rankings uniqueness
    if len(set(rankings)) != len(rankings):
        validation['errors'].append("Rankings must be unique")
        validation['valid'] = False

    # Check ranking range
    if np.min(rankings) != 1 or np.max(rankings) != len(rankings):
        validation['errors'].append(f"Rankings must be 1 to {len(rankings)}, got range [{np.min(rankings)}, {np.max(rankings)}]")
        validation['valid'] = False

    # Check distance positivity
    if np.any(D_plus <= 0) or np.any(D_minus <= 0):
        validation['warnings'].append("Some distances to ideal solutions are zero or negative")

    # Check Ci ordering (higher Ci should have better rank)
    sorted_ci_indices = np.argsort(-Ci)  # Sort by Ci descending
    expected_rankings = np.arange(1, len(Ci) + 1)
    actual_rankings_sorted = rankings[sorted_ci_indices]

    if not np.array_equal(actual_rankings_sorted, expected_rankings):
        validation['errors'].append("Rankings do not match Ci ordering")
        validation['valid'] = False

    # Check for ties
    ci_differences = np.diff(np.sort(Ci))
    min_difference = np.min(ci_differences) if len(ci_differences) > 0 else 1.0
    if min_difference < 0.05:
        validation['warnings'].append(f"Some Ci scores are very close (min difference: {min_difference:.4f})")

    return validation


def compare_alternatives(alternative1_index: int,
                        alternative2_index: int,
                        topsis_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare two alternatives using TOPSIS results.

    Args:
        alternative1_index: Index of first alternative
        alternative2_index: Index of second alternative
        topsis_results: Results from topsis_rank function

    Returns:
        Dictionary with comparison results
    """
    Ci = topsis_results['Ci']
    rankings = topsis_results['rankings']
    D_plus = topsis_results['D_plus']
    D_minus = topsis_results['D_minus']

    # Get values for both alternatives
    ci1, ci2 = Ci[alternative1_index], Ci[alternative2_index]
    rank1, rank2 = rankings[alternative1_index], rankings[alternative2_index]
    d_plus1, d_plus2 = D_plus[alternative1_index], D_plus[alternative2_index]
    d_minus1, d_minus2 = D_minus[alternative1_index], D_minus[alternative2_index]

    # Determine winner
    winner = 1 if ci1 > ci2 else 2
    if ci1 == ci2:
        winner = 0  # Tie

    # Calculate differences
    ci_diff = ci1 - ci2
    rank_diff = rank2 - rank1  # Lower rank number is better
    d_plus_diff = d_plus1 - d_plus2
    d_minus_diff = d_minus1 - d_minus2

    return {
        'winner': winner,
        'alternative1': {
            'index': alternative1_index,
            'Ci': ci1,
            'rank': rank1,
            'D_plus': d_plus1,
            'D_minus': d_minus1
        },
        'alternative2': {
            'index': alternative2_index,
            'Ci': ci2,
            'rank': rank2,
            'D_plus': d_plus2,
            'D_minus': d_minus2
        },
        'differences': {
            'Ci': ci_diff,
            'rank': rank_diff,
            'D_plus': d_plus_diff,
            'D_minus': d_minus_diff
        }
    }


def sensitivity_analysis_weights(decision_matrix: np.ndarray,
                               base_weights: np.ndarray,
                               indicator_types: List[str],
                               perturbation: float = 0.2) -> Dict[str, Any]:
    """
    Perform sensitivity analysis on indicator weights.

    Args:
        decision_matrix: Decision matrix
        base_weights: Base weight vector
        indicator_types: Indicator types
        perturbation: Perturbation amount (±20% default)

    Returns:
        Dictionary with sensitivity analysis results
    """
    original_result = topsis_rank(decision_matrix, base_weights, indicator_types)
    original_rankings = original_result['rankings']
    original_ci = original_result['Ci']

    sensitivity_results = {
        'base_weights': base_weights,
        'original_rankings': original_rankings,
        'original_ci': original_ci,
        'weight_sensitivities': {},
        'ranking_stability': {},
        'summary': {}
    }

    n_indicators = len(base_weights)
    ranking_changes = []

    # Perturb each weight individually
    for i in range(n_indicators):
        # Positive perturbation
        perturbed_weights_plus = base_weights.copy()
        perturbed_weights_plus[i] *= (1 + perturbation)
        perturbed_weights_plus /= np.sum(perturbed_weights_plus)  # Renormalize

        result_plus = topsis_rank(decision_matrix, perturbed_weights_plus, indicator_types)

        # Negative perturbation
        perturbed_weights_minus = base_weights.copy()
        perturbed_weights_minus[i] *= (1 - perturbation)
        perturbed_weights_minus /= np.sum(perturbed_weights_minus)  # Renormalize

        result_minus = topsis_rank(decision_matrix, perturbed_weights_minus, indicator_types)

        # Calculate ranking changes
        rank_changes_plus = np.abs(result_plus['rankings'] - original_rankings)
        rank_changes_minus = np.abs(result_minus['rankings'] - original_rankings)

        max_rank_change = max(np.max(rank_changes_plus), np.max(rank_changes_minus))

        ranking_changes.append(max_rank_change)

        sensitivity_results['weight_sensitivities'][f'indicator_{i+1}'] = {
            'base_weight': base_weights[i],
            'perturbed_weight_plus': perturbed_weights_plus[i],
            'perturbed_weight_minus': perturbed_weights_minus[i],
            'ranking_changes_plus': rank_changes_plus.tolist(),
            'ranking_changes_minus': rank_changes_minus.tolist(),
            'max_rank_change': max_rank_change
        }

    # Calculate summary statistics
    sensitivity_results['summary'] = {
        'max_rank_change_across_all': max(ranking_changes),
        'avg_rank_change_across_all': np.mean(ranking_changes),
        'most_sensitive_indicator': np.argmax(ranking_changes) + 1,
        'least_sensitive_indicator': np.argmin(ranking_changes) + 1
    }

    # Check overall stability
    max_change = sensitivity_results['summary']['max_rank_change_across_all']
    sensitivity_results['ranking_stability']['stable'] = max_change <= 1
    sensitivity_results['ranking_stability']['max_rank_change'] = max_change

    return sensitivity_results


if __name__ == "__main__":
    # Example usage and testing
    print("Testing TOPSIS Module")

    # Test data: 3 alternatives × 4 indicators
    decision_matrix = np.array([
        [0.8, 0.6, 0.9, 0.7],  # Alternative 1
        [0.7, 0.8, 0.6, 0.9],  # Alternative 2
        [0.9, 0.7, 0.8, 0.6]   # Alternative 3
    ])

    weights = np.array([0.3, 0.25, 0.25, 0.2])  # Sum to 1.0
    indicator_types = ['benefit', 'benefit', 'benefit', 'cost']

    try:
        result = topsis_rank(decision_matrix, weights, indicator_types)

        print("TOPSIS Results:")
        print(f"Ci scores: {result['Ci']}")
        print(f"Rankings: {result['rankings']}")
        print(f"PIS: {result['PIS']}")
        print(f"NIS: {result['NIS']}")
        print(f"Validation: {'PASSED' if result['validation']['valid'] else 'FAILED'}")

        # Test comparison
        comparison = compare_alternatives(0, 1, result)
        print(f"\nComparison between alternatives 1 and 2:")
        print(f"Winner: Alternative {comparison['winner']}")
        print(f"Ci difference: {comparison['differences']['Ci']:.3f}")

        # Test sensitivity analysis
        sensitivity = sensitivity_analysis_weights(decision_matrix, weights, indicator_types, perturbation=0.1)
        print(f"\nSensitivity Analysis:")
        print(f"Max rank change: {sensitivity['summary']['max_rank_change_across_all']}")
        print(f"Most sensitive indicator: {sensitivity['summary']['most_sensitive_indicator']}")

    except Exception as e:
        print(f"Error: {e}")