"""
FCE (Fuzzy Comprehensive Evaluation) Module

Implements fuzzy comprehensive evaluation for converting qualitative expert
assessments into quantitative scores using 4-level linguistic scale.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import yaml


class FCEError(Exception):
    """Base exception for FCE module errors."""
    pass


class MembershipError(FCEError):
    """Raised when membership degrees are invalid."""
    pass


def fuzzy_evaluate(expert_assessments: Dict[str, int],
                  fuzzy_scale: Dict[str, float],
                  validate_membership: bool = True,
                  tolerance: float = 0.001) -> Dict[str, Any]:
    """
    Convert linguistic expert assessments to quantitative fuzzy scores.

    Args:
        expert_assessments: Dictionary with linguistic term counts
                           e.g., {'差': 0, '中': 1, '良': 3, '优': 1}
        fuzzy_scale: Dictionary mapping linguistic terms to numerical values
                     e.g., {'差': 0.25, '中': 0.50, '良': 0.75, '优': 1.00}
        validate_membership: Whether to validate membership degree sum
        tolerance: Tolerance for membership sum validation

    Returns:
        Dictionary containing:
            'membership_vector': np.ndarray of normalized membership degrees
            'fuzzy_score': float, weighted average (defuzzified score)
            'total_experts': int, total number of expert assessments
            'valid': bool, True if membership degrees sum to 1.0
            'assessment_distribution': dict, original assessment counts

    Raises:
        MembershipError: If membership degrees don't sum to 1.0
        FCEError: If input data is invalid
    """
    # Validate input data
    if not expert_assessments:
        raise FCEError("Expert assessments cannot be empty")

    if not fuzzy_scale:
        raise FCEError("Fuzzy scale cannot be empty")

    # Get linguistic terms in order (差, 中, 良, 优)
    linguistic_terms = ['差', '中', '良', '优']
    assessment_counts = []
    score_values = []

    for term in linguistic_terms:
        count = expert_assessments.get(term, 0)
        score = fuzzy_scale.get(term, 0.0)

        if count < 0:
            raise FCEError(f"Negative count for term '{term}': {count}")

        # Ensure score is a float
        if isinstance(score, dict):
            score = float(score.get('value', 0.0)) if 'value' in score else 0.0
        else:
            score = float(score)

        assessment_counts.append(count)
        score_values.append(score)

    assessment_counts = np.array(assessment_counts, dtype=float)
    score_values = np.array(score_values)

    total_experts = np.sum(assessment_counts)

    if total_experts == 0:
        raise FCEError("Total expert assessments cannot be zero")

    # Calculate membership vector (normalized counts)
    membership_vector = assessment_counts / total_experts

    # Validate membership degrees sum
    membership_sum = np.sum(membership_vector)
    if validate_membership and abs(membership_sum - 1.0) > tolerance:
        raise MembershipError(f"Membership degrees sum to {membership_sum:.6f}, expected 1.0 ± {tolerance}")

    # Calculate fuzzy score using weighted average (defuzzification)
    fuzzy_score = np.dot(membership_vector, score_values)

    return {
        'membership_vector': membership_vector,
        'fuzzy_score': fuzzy_score,
        'total_experts': int(total_experts),
        'valid': abs(membership_sum - 1.0) <= tolerance,
        'assessment_distribution': {term: int(count) for term, count in zip(linguistic_terms, assessment_counts)},
        'score_values': score_values
    }


def validate_membership_degrees(membership_vector: np.ndarray,
                              tolerance: float = 0.001) -> Dict[str, Any]:
    """
    Validate membership degrees for fuzzy evaluation.

    Args:
        membership_vector: Array of membership degrees
        tolerance: Tolerance for validation

    Returns:
        Dictionary with validation results:
            - 'sum_to_one': Whether degrees sum to 1.0
            - 'all_positive': Whether all degrees are non-negative
            - 'all_valid': Overall validation result
            - 'sum_value': Actual sum of degrees
            - 'error_messages': List of validation errors
    """
    result = {
        'sum_to_one': False,
        'all_positive': False,
        'all_valid': False,
        'sum_value': 0.0,
        'error_messages': []
    }

    # Check if all degrees are non-negative
    if np.any(membership_vector < 0):
        result['error_messages'].append("Negative membership degrees found")
    else:
        result['all_positive'] = True

    # Check if degrees sum to 1.0
    sum_value = np.sum(membership_vector)
    result['sum_value'] = sum_value

    if abs(sum_value - 1.0) <= tolerance:
        result['sum_to_one'] = True

    # Overall validation
    result['all_valid'] = result['all_positive'] and result['sum_to_one']

    return result


def load_fuzzy_scale(config_path: str) -> Dict[str, float]:
    """
    Load fuzzy scale from configuration file.

    Args:
        config_path: Path to fuzzy scale configuration file

    Returns:
        Dictionary mapping linguistic terms to numerical values

    Raises:
        FCEError: If configuration cannot be loaded or is invalid
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        if 'fuzzy_scale' not in config:
            raise FCEError("Missing 'fuzzy_scale' section in configuration")

        fuzzy_scale = config['fuzzy_scale']

        # Validate fuzzy scale
        required_terms = ['差', '中', '良', '优']
        for term in required_terms:
            if term not in fuzzy_scale:
                raise FCEError(f"Missing linguistic term '{term}' in fuzzy scale")

            value = fuzzy_scale[term]
            if not isinstance(value, (int, float)) or not (0.0 <= value <= 1.0):
                raise FCEError(f"Invalid fuzzy value for '{term}': {value}")

        return fuzzy_scale

    except yaml.YAMLError as e:
        raise FCEError(f"Error parsing YAML file {config_path}: {e}")
    except FileNotFoundError:
        raise FCEError(f"Fuzzy scale file not found: {config_path}")
    except Exception as e:
        raise FCEError(f"Error loading fuzzy scale: {e}")


def process_fuzzy_indicators(scheme_data: Dict[str, Any],
                           fuzzy_scale: Dict[str, float],
                           applicable_indicators: List[str]) -> Dict[str, float]:
    """
    Process all fuzzy indicators for a combat system scheme.

    Args:
        scheme_data: Scheme configuration data
        fuzzy_scale: Fuzzy scale mapping
        applicable_indicators: List of indicators that use fuzzy evaluation

    Returns:
        Dictionary mapping indicator IDs to fuzzy scores

    Raises:
        FCEError: If processing fails
    """
    fuzzy_scores = {}

    # Check if scheme has fuzzy assessments
    if 'fuzzy_assessments' not in scheme_data:
        # Generate default assessments if not provided
        fuzzy_assessments = {}
        for indicator in applicable_indicators:
            fuzzy_assessments[indicator] = {'差': 0, '中': 1, '良': 2, '优': 0}
    else:
        fuzzy_assessments = scheme_data['fuzzy_assessments']

    # Process each fuzzy indicator
    for indicator_id in applicable_indicators:
        if indicator_id in fuzzy_assessments:
            try:
                assessment_data = fuzzy_assessments[indicator]
                result = fuzzy_evaluate(assessment_data, fuzzy_scale)
                fuzzy_scores[indicator_id] = result['fuzzy_score']
            except Exception as e:
                raise FCEError(f"Error processing fuzzy indicator {indicator_id}: {e}")
        else:
            # Default to moderate assessment if not provided
            default_assessment = {'差': 0, '中': 1, '良': 0, '优': 0}
            result = fuzzy_evaluate(default_assessment, fuzzy_scale)
            fuzzy_scores[indicator_id] = result['fuzzy_score']

    return fuzzy_scores


def aggregate_expert_assessments(expert_assessments_list: List[Dict[str, int]],
                               fuzzy_scale: Dict[str, float]) -> Dict[str, Any]:
    """
    Aggregate assessments from multiple experts.

    Args:
        expert_assessments_list: List of assessment dictionaries from multiple experts
        fuzzy_scale: Fuzzy scale mapping

    Returns:
        Dictionary with aggregated assessment results

    Raises:
        FCEError: If aggregation fails
    """
    if not expert_assessments_list:
        raise FCEError("No expert assessments provided")

    # Initialize aggregated counts
    linguistic_terms = ['差', '中', '良', '优']
    aggregated_assessments = {term: 0 for term in linguistic_terms}

    # Sum assessments from all experts
    for assessments in expert_assessments_list:
        for term in linguistic_terms:
            count = assessments.get(term, 0)
            if count < 0:
                raise FCEError(f"Negative assessment count for term '{term}': {count}")
            aggregated_assessments[term] += count

    # Calculate fuzzy score for aggregated assessments
    result = fuzzy_evaluate(aggregated_assessments, fuzzy_scale)

    # Add expert statistics
    result['num_experts'] = len(expert_assessments_list)
    result['individual_assessments'] = expert_assessments_list

    return result


def calculate_fuzzy_confidence(membership_vector: np.ndarray,
                             confidence_level: float = 0.95) -> Dict[str, Any]:
    """
    Calculate confidence metrics for fuzzy evaluation.

    Args:
        membership_vector: Membership degrees
        confidence_level: Desired confidence level (0.0-1.0)

    Returns:
        Dictionary with confidence metrics
    """
    # Calculate entropy as uncertainty measure
    entropy = -np.sum(membership_vector * np.log(membership_vector + 1e-10))

    # Maximum entropy for 4 linguistic terms
    max_entropy = np.log(4)

    # Normalized entropy (0 = certain, 1 = completely uncertain)
    normalized_entropy = entropy / max_entropy

    # Confidence (inverse of entropy)
    confidence = 1.0 - normalized_entropy

    # Most likely linguistic term
    max_idx = np.argmax(membership_vector)
    linguistic_terms = ['差', '中', '良', '优']
    most_likely_term = linguistic_terms[max_idx]
    max_membership = membership_vector[max_idx]

    return {
        'confidence': confidence,
        'entropy': entropy,
        'normalized_entropy': normalized_entropy,
        'most_likely_term': most_likely_term,
        'max_membership': max_membership,
        'membership_spread': np.std(membership_vector)
    }


if __name__ == "__main__":
    # Example usage and testing
    print("Testing FCE Module")

    # Test fuzzy scale
    fuzzy_scale = {
        '差': 0.25,
        '中': 0.50,
        '良': 0.75,
        '优': 1.00
    }

    # Test expert assessments
    expert_assessments = {
        '差': 0,
        '中': 1,
        '良': 3,
        '优': 1
    }

    try:
        result = fuzzy_evaluate(expert_assessments, fuzzy_scale)
        print(f"Fuzzy score: {result['fuzzy_score']:.3f}")
        print(f"Membership vector: {result['membership_vector']}")
        print(f"Total experts: {result['total_experts']}")
        print(f"Valid: {result['valid']}")

        # Test confidence calculation
        confidence_result = calculate_fuzzy_confidence(result['membership_vector'])
        print(f"Confidence: {confidence_result['confidence']:.3f}")
        print(f"Most likely term: {confidence_result['most_likely_term']}")

        # Test aggregation
        expert1_assessments = {'差': 0, '中': 2, '良': 1, '优': 0}
        expert2_assessments = {'差': 1, '中': 1, '良': 2, '优': 0}
        expert3_assessments = {'差': 0, '中': 0, '良': 2, '优': 1}

        aggregated = aggregate_expert_assessments([
            expert1_assessments,
            expert2_assessments,
            expert3_assessments
        ], fuzzy_scale)

        print(f"\nAggregated fuzzy score: {aggregated['fuzzy_score']:.3f}")
        print(f"Aggregated assessments: {aggregated['assessment_distribution']}")

    except Exception as e:
        print(f"Error: {e}")