"""
Evaluator Module - AHP-FCE-TOPSIS Pipeline Orchestration

Coordinates the complete evaluation pipeline from raw scheme data to final rankings.
Implements User Story 1: Combat System Evaluation.
"""

import numpy as np
import yaml
import os
import sys
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json

from modules.ahp_module import calculate_primary_weights, load_judgment_matrix, AHPConsistencyError
from modules.fce_module import load_fuzzy_scale, process_fuzzy_indicators, fuzzy_evaluate
from modules.topsis_module import topsis_rank
from utils.validation import AuditLogger, validate_evaluation_result, validate_scheme_config
from utils.consistency_check import calculate_cr


class EvaluatorError(Exception):
    """Base exception for evaluator module."""
    pass


class ConfigurationError(EvaluatorError):
    """Raised when configuration is invalid."""
    pass


class EvaluationError(EvaluatorError):
    """Raised when evaluation fails."""
    pass


def evaluate_single_scheme(scheme_data: Dict[str, Any],
                          indicator_config: Dict[str, Any],
                          fuzzy_config: Dict[str, Any],
                          expert_judgments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate a single combat system configuration using AHP-FCE-TOPSIS pipeline.

    Args:
        scheme_data: Combat system scheme configuration
        indicator_config: Indicator hierarchy and weights configuration
        fuzzy_config: Fuzzy evaluation sets configuration
        expert_judgments: Expert judgment matrices for AHP

    Returns:
        Dictionary containing complete evaluation results

    Raises:
        ConfigurationError: If configuration is invalid
        EvaluationError: If evaluation fails
    """
    # Initialize audit logger
    scheme_id = scheme_data.get('scheme_id', 'unknown')
    scenario_id = scheme_data.get('scenario_context', 'unknown')
    audit_logger = AuditLogger(scheme_id, scenario_id)

    try:
        # Step 1: Validate inputs
        _validate_inputs(scheme_data, indicator_config, fuzzy_config, expert_judgments)
        audit_logger.log_transformation(
            stage="Input Validation",
            input_data={"scheme_id": scheme_id, "scenario_id": scenario_id},
            output_data={"validation": "passed"}
        )

        # Step 2: Integrate scenario context (NEW)
        from .scenario_integration import integrate_scenario_into_evaluation
        adjusted_indicator_config, adjusted_fuzzy_config, scenario_integrator = integrate_scenario_into_evaluation(
            scheme_data, indicator_config, fuzzy_config, audit_logger
        )

        # Step 3: Calculate AHP weights with scenario adjustments
        weights_result = _calculate_ahp_weights(adjusted_indicator_config, expert_judgments, audit_logger)
        global_weights = weights_result['global_weights']

        # Apply scenario-based weight adjustments (NEW)
        if scenario_integrator and hasattr(scenario_integrator, 'objective_weights'):
            global_weights = _apply_scenario_weight_adjustments(global_weights, scenario_integrator, audit_logger)

        # Step 4: Generate indicator values with scenario awareness (MODIFIED)
        if scenario_integrator:
            indicator_values = _generate_scenario_aware_indicator_values(
                scheme_data, adjusted_indicator_config, scenario_integrator, audit_logger
            )
        else:
            indicator_values = _generate_indicator_values(scheme_data, adjusted_indicator_config, audit_logger)

        # Step 5: Apply scenario-aware fuzzy evaluation (MODIFIED)
        if scenario_integrator:
            fuzzy_results = _apply_scenario_aware_fuzzy_evaluation(
                indicator_values, adjusted_fuzzy_config, scenario_integrator, audit_logger
            )
        else:
            fuzzy_results = _apply_fuzzy_evaluation(indicator_values, fuzzy_config, audit_logger)

        # Step 6: Combine fuzzy and quantitative indicators
        combined_values = _combine_indicator_values(indicator_values, fuzzy_results, audit_logger)

        # Step 7: Prepare TOPSIS input with scenario considerations
        if scenario_integrator:
            topsis_input = _prepare_scenario_aware_topsis_input(combined_values, scenario_integrator, audit_logger)
        else:
            topsis_input = _prepare_topsis_input(combined_values, audit_logger)

        # Step 8: Apply TOPSIS ranking
        topsis_result = _apply_topsis(topsis_input, global_weights, audit_logger)

        # Step 9: Generate final evaluation result with scenario context (MODIFIED)
        if scenario_integrator:
            evaluation_result = _generate_scenario_aware_evaluation_result(
                scheme_data, combined_values, global_weights, topsis_result, scenario_integrator, audit_logger
            )
        else:
            evaluation_result = _generate_evaluation_result(
                scheme_data, combined_values, global_weights, topsis_result, audit_logger
            )

        return evaluation_result

    except Exception as e:
        audit_logger.log_transformation(
            stage="Error",
            input_data={"error": str(e)},
            output_data={"status": "failed"}
        )
        raise EvaluationError(f"Evaluation failed for scheme {scheme_id}: {e}")


def evaluate_batch(schemes: List[Dict[str, Any]],
                 indicator_config: Dict[str, Any],
                 fuzzy_config: Dict[str, Any],
                 expert_judgments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate multiple combat system configurations and rank them.

    Args:
        schemes: List of scheme configurations
        indicator_config: Indicator hierarchy configuration
        fuzzy_config: Fuzzy evaluation configuration
        expert_judgments: Expert judgment matrices

    Returns:
        Dictionary containing batch evaluation results

    Raises:
        EvaluationError: If batch evaluation fails
    """
    if len(schemes) < 2:
        raise EvaluationError("Need at least 2 schemes for batch evaluation")

    batch_results = {
        'evaluation_timestamp': datetime.now().isoformat(),
        'num_schemes': len(schemes),
        'individual_results': {},
        'comparison_matrix': None,
        'rankings': {},
        'best_scheme': None,
        'validation_results': {}
    }

    try:
        # Calculate shared AHP weights once
        audit_logger = AuditLogger("batch_evaluation", "batch")
        weights_result = _calculate_ahp_weights(indicator_config, expert_judgments, audit_logger)
        global_weights = weights_result['global_weights']

        # Evaluate each scheme individually and collect indicator values
        individual_results = []
        decision_matrix = []

        for scheme in schemes:
            try:
                result = evaluate_single_scheme(scheme, indicator_config, fuzzy_config, expert_judgments)
                individual_results.append(result)

                # Extract indicator values for TOPSIS decision matrix
                indicator_values = result.get('indicator_values', {})
                if indicator_values:
                    # Ensure consistent ordering
                    indicator_order = [
                        'C1_1', 'C1_2', 'C1_3', 'C2_1', 'C2_2', 'C2_3',
                        'C3_1', 'C3_2', 'C3_3', 'C4_1', 'C4_2', 'C4_3',
                        'C5_1', 'C5_2', 'C5_3'
                    ]
                    row = [indicator_values.get(ind_id, 0.0) for ind_id in indicator_order]
                    decision_matrix.append(row)

                batch_results['individual_results'][scheme['scheme_id']] = result
            except Exception as e:
                error_msg = f"Failed to evaluate scheme {scheme.get('scheme_id', 'unknown')}: {e}"
                batch_results['validation_results'][scheme.get('scheme_id', 'unknown')] = {'error': error_msg}
                raise EvaluationError(error_msg)

        # Prepare decision matrix for TOPSIS
        decision_matrix = np.array(decision_matrix)

        # Determine indicator types
        indicator_types = _get_indicator_types(indicator_config)

        # Apply TOPSIS to rank all schemes
        topsis_result = topsis_rank(decision_matrix,
                                   np.array(list(global_weights.values())),
                                   indicator_types)

        # Update results with rankings
        for i, scheme in enumerate(schemes):
            scheme_id = scheme['scheme_id']
            if scheme_id in batch_results['individual_results']:
                batch_results['individual_results'][scheme_id]['Ci'] = float(topsis_result['Ci'][i])
                batch_results['individual_results'][scheme_id]['rank'] = int(topsis_result['rankings'][i])

        # Store TOPSIS results
        batch_results['comparison_matrix'] = {
            'decision_matrix': decision_matrix.tolist(),
            'normalized_matrix': topsis_result['normalized_matrix'].tolist(),
            'weighted_matrix': topsis_result['weighted_matrix'].tolist(),
            'Ci_scores': topsis_result['Ci'].tolist(),
            'rankings': topsis_result['rankings'].tolist(),
            'PIS': topsis_result['PIS'].tolist(),
            'NIS': topsis_result['NIS'].tolist()
        }

        # Find best scheme (rank 1)
        best_rank_idx = np.argmin(topsis_result['rankings']) - 1
        best_scheme_id = schemes[best_rank_idx]['scheme_id']
        batch_results['best_scheme'] = {
            'scheme_id': best_scheme_id,
            'Ci_score': float(topsis_result['Ci'][best_rank_idx]),
            'rank': 1
        }

        # Validate batch results
        for scheme_id, result in batch_results['individual_results'].items():
            validation = validate_evaluation_result(result, strict_mode=False)
            if not validation['is_valid']:
                batch_results['validation_results'][scheme_id] = validation

        return batch_results

    except Exception as e:
        raise EvaluationError(f"Batch evaluation failed: {e}")


def _validate_inputs(scheme_data: Dict[str, Any],
                    indicator_config: Dict[str, Any],
                    fuzzy_config: Dict[str, Any],
                    expert_judgments: Dict[str, Any]) -> None:
    """Validate all input configurations."""
    # Validate scheme configuration
    scheme_validation = validate_scheme_config(scheme_data)
    if not scheme_validation['is_valid']:
        raise ConfigurationError(f"Invalid scheme configuration: {scheme_validation['errors']}")

    # Validate indicator configuration
    if 'secondary_indicators' not in indicator_config:
        raise ConfigurationError("Missing 'secondary_indicators' in indicator configuration")

    if len(indicator_config['secondary_indicators']) != 15:
        raise ConfigurationError(f"Expected 15 secondary indicators, got {len(indicator_config['secondary_indicators'])}")

    # Validate fuzzy configuration
    if 'fuzzy_scale' not in fuzzy_config:
        raise ConfigurationError("Missing 'fuzzy_scale' in fuzzy configuration")

    # Validate expert judgments (can be file path string or dict)
    if not expert_judgments:
        raise ConfigurationError("Expert judgments cannot be empty")


def _calculate_ahp_weights(indicator_config: Dict[str, Any],
                          expert_judgments: Dict[str, Any],
                          audit_logger: AuditLogger) -> Dict[str, Any]:
    """Calculate AHP weights from expert judgments."""
    try:
        # Get file paths from expert_judgments parameter
        if isinstance(expert_judgments, str):
            # If it's a string, treat it as the primary capabilities file
            primary_matrix_file = expert_judgments
            secondary_matrices_dir = os.path.dirname(expert_judgments)
        else:
            # If it's a dict, extract paths
            primary_matrix_file = expert_judgments.get('primary_capabilities_file')
            secondary_matrices_dir = expert_judgments.get('secondary_indicators_dir')

        if not primary_matrix_file:
            raise ConfigurationError("Missing primary capabilities matrix file")

        if not secondary_matrices_dir:
            secondary_matrices_dir = os.path.dirname(primary_matrix_file)

        # Calculate weights
        weights_result = calculate_primary_weights(primary_matrix_file, secondary_matrices_dir)

        audit_logger.log_transformation(
            stage="AHP Weight Calculation",
            input_data={"primary_matrix": primary_matrix_file},
            output_data={"global_weights": weights_result['global_weights']},
            metadata={"errors": weights_result.get('errors', [])}
        )

        if weights_result.get('errors'):
            raise EvaluationError(f"AHP calculation errors: {weights_result['errors']}")

        return weights_result

    except Exception as e:
        raise EvaluationError(f"AHP weight calculation failed: {e}")


def _generate_scenario_aware_indicator_values(scheme_data: Dict[str, Any],
                                             indicator_config: Dict[str, Any],
                                             scenario_integrator,
                                             audit_logger: AuditLogger) -> Dict[str, float]:
    """Generate scenario-aware indicator values from scheme configuration."""
    indicator_values = {}
    indicators = indicator_config['secondary_indicators']

    # Get simulation parameters
    sim_params = scheme_data.get('simulation_parameters', {})

    # Apply scenario-based adjustments to base values
    base_values = {
        'C1_1': 50.0,  # Detection range (km)
        'C1_3': 500.0,  # Search coverage (km²/h)
        'C2_1': 30.0,   # Response time (seconds)
        'C2_3': 100.0,  # Information processing (data_units/min)
        'C3_1': 100.0,  # Weapon range (km)
        'C3_3': 5.0,    # Fire density (engagements/min)
        'C4_1': 100.0,  # Communication bandwidth (Mbps)
        'C4_3': 50.0,   # Data latency (ms)
        'C5_2': 20.0    # Mobility (knots)
    }

    # Get scenario-adjusted base values and multipliers
    adjusted_base_values = scenario_integrator.get_scenario_adjusted_base_values(base_values)
    adjusted_multipliers = scenario_integrator.get_scenario_adjusted_multipliers({})

    # Generate values for each indicator
    for indicator_id, indicator_config in indicators.items():
        # Use scenario-adjusted base value if available
        if indicator_id in adjusted_base_values:
            base_value = adjusted_base_values[indicator_id]
        else:
            base_value = base_values.get(indicator_id, 50.0)

        value = _calculate_scenario_aware_indicator_value(
            indicator_id, indicator_config, scheme_data, sim_params, base_value, adjusted_multipliers
        )
        indicator_values[indicator_id] = value

    audit_logger.log_transformation(
        stage="Scenario-Aware Indicator Value Generation",
        input_data={"scheme_id": scheme_data['scheme_id'], "sim_params": sim_params, "scenario": scenario_integrator.scenario_id},
        output_data={"indicator_values": indicator_values}
    )

    return indicator_values


def _generate_indicator_values(scheme_data: Dict[str, Any],
                             indicator_config: Dict[str, Any],
                             audit_logger: AuditLogger) -> Dict[str, float]:
    """Generate indicator values from scheme configuration (legacy function for compatibility)."""
    indicator_values = {}
    indicators = indicator_config['secondary_indicators']

    # Get simulation parameters
    sim_params = scheme_data.get('simulation_parameters', {})

    # Use original base values
    base_values = {
        'C1_1': 50.0,  # Detection range (km)
        'C1_3': 500.0,  # Search coverage (km²/h)
        'C2_1': 30.0,   # Response time (seconds)
        'C2_3': 100.0,  # Information processing (data_units/min)
        'C3_1': 100.0,  # Weapon range (km)
        'C3_3': 5.0,    # Fire density (engagements/min)
        'C4_1': 100.0,  # Communication bandwidth (Mbps)
        'C4_3': 50.0,   # Data latency (ms)
        'C5_2': 20.0    # Mobility (knots)
    }

    # Generate values for each indicator using original logic
    for indicator_id, indicator_config in indicators.items():
        if indicator_id in base_values:
            base_value = base_values[indicator_id]
        else:
            base_value = 50.0

        value = _calculate_indicator_value(indicator_id, indicator_config, scheme_data, sim_params)
        indicator_values[indicator_id] = value

    audit_logger.log_transformation(
        stage="Standard Indicator Value Generation",
        input_data={"scheme_id": scheme_data['scheme_id'], "sim_params": sim_params},
        output_data={"indicator_values": indicator_values}
    )

    return indicator_values


def _calculate_indicator_value(indicator_id: str,
                             indicator_config: Dict[str, Any],
                             scheme_data: Dict[str, Any],
                             sim_params: Dict[str, Any]) -> float:
    """Calculate value for a single indicator."""
    # Base values from simulation parameters
    base_values = {
        'C1_1': 50.0,  # Detection range (km)
        'C1_3': 500.0,  # Search coverage (km²/h)
        'C2_1': 30.0,   # Response time (seconds)
        'C2_3': 100.0,  # Information processing (data_units/min)
        'C3_1': 100.0,  # Weapon range (km)
        'C3_3': 5.0,    # Fire density (engagements/min)
        'C4_1': 100.0,  # Communication bandwidth (Mbps)
        'C4_3': 50.0,   # Data latency (ms)
        'C5_2': 20.0    # Mobility (knots)
    }

    # Apply simulation parameter multipliers
    multipliers = {
        'detection_range_factor': ['C1_1'],
        'coordination_efficiency': ['C2_3'],
        'weapon_effectiveness': ['C3_1', 'C3_3'],
        'network_bandwidth_mbps': ['C4_1'],
        'stealth_factor': ['C1_1'],  # Affects detection
        'mobility_factor': ['C5_2']
    }

    # Get base value
    base_value = base_values.get(indicator_id, 1.0)

    # Apply multipliers
    for param, affected_indicators in multipliers.items():
        if indicator_id in affected_indicators and param in sim_params:
            multiplier = sim_params[param]
            if param == 'stealth_factor' and indicator_id == 'C1_1':
                # Stealth reduces detection range
                base_value *= (2.0 - multiplier)  # Inverse effect
            else:
                base_value *= multiplier

    # Apply platform inventory scaling
    platform_inventory = scheme_data.get('platform_inventory', {})
    total_platforms = sum(data.get('count', 0) for data in platform_inventory.values())

    # Scale by platform count for certain indicators
    scaling_indicators = ['C1_1', 'C1_3', 'C2_3', 'C3_3', 'C4_1']
    if indicator_id in scaling_indicators:
        base_value *= (total_platforms / 10.0)  # Normalize to 10 platforms

    # Apply indicator type adjustments
    indicator_type = indicator_config.get('type', 'benefit')
    if indicator_type == 'cost':
        # For cost indicators, lower values are better
        # Invert some calculations to make them realistic
        if indicator_id == 'C2_1':  # Response time
            base_value = max(10.0, base_value)  # Minimum 10 seconds
        elif indicator_id == 'C4_3':  # Data latency
            base_value = max(10.0, base_value)  # Minimum 10ms

    return float(base_value)


def _apply_fuzzy_evaluation(indicator_values: Dict[str, float],
                           fuzzy_config: Dict[str, Any],
                           audit_logger: AuditLogger) -> Dict[str, float]:
    """Apply fuzzy evaluation to qualitative indicators."""
    fuzzy_results = {}
    fuzzy_scale = fuzzy_config['fuzzy_scale']
    applicable_indicators = fuzzy_config.get('applicable_indicators', {})

    # Apply fuzzy evaluation to applicable indicators
    for indicator_id in applicable_indicators:
        if indicator_id in indicator_values:
            # Generate default fuzzy assessment based on quantitative value
            quantitative_value = indicator_values[indicator_id]
            fuzzy_assessment = _generate_fuzzy_assessment(quantitative_value, indicator_id)

            try:
                result = fuzzy_evaluate(fuzzy_assessment, fuzzy_scale)
                fuzzy_results[indicator_id] = result['fuzzy_score']
            except Exception as e:
                # Fallback to moderate assessment
                default_assessment = {'差': 0, '中': 1, '良': 0, '优': 0}
                result = fuzzy_evaluate(default_assessment, fuzzy_scale)
                fuzzy_results[indicator_id] = result['fuzzy_score']

    audit_logger.log_transformation(
        stage="Fuzzy Evaluation",
        input_data={"applicable_indicators": list(applicable_indicators.keys())},
        output_data={"fuzzy_scores": fuzzy_results}
    )

    return fuzzy_results


def _generate_fuzzy_assessment(quantitative_value: float,
                             indicator_id: str) -> Dict[str, int]:
    """Generate fuzzy assessment from quantitative value."""
    # Simple mapping based on value ranges
    assessments = {'差': 0, '中': 0, '良': 0, '优': 0}

    # Define ranges for each indicator type
    if 'C1' in indicator_id or 'C3' in indicator_id:  # Performance indicators
        if quantitative_value < 30:
            assessments['差'] = 1
        elif quantitative_value < 60:
            assessments['中'] = 1
        elif quantitative_value < 90:
            assessments['良'] = 1
        else:
            assessments['优'] = 1
    elif 'C2' in indicator_id:  # Time-based indicators
        if quantitative_value > 60:
            assessments['差'] = 1
        elif quantitative_value > 30:
            assessments['中'] = 1
        elif quantitative_value > 15:
            assessments['良'] = 1
        else:
            assessments['优'] = 1
    else:  # Other indicators
        if quantitative_value < 20:
            assessments['差'] = 1
        elif quantitative_value < 50:
            assessments['中'] = 1
        elif quantitative_value < 80:
            assessments['良'] = 1
        else:
            assessments['优'] = 1

    return assessments


def _combine_indicator_values(indicator_values: Dict[str, float],
                            fuzzy_results: Dict[str, float],
                            audit_logger: AuditLogger) -> Dict[str, float]:
    """Combine fuzzy and quantitative indicator values."""
    combined_values = indicator_values.copy()

    # Replace quantitative values with fuzzy scores for fuzzy indicators
    for indicator_id, fuzzy_score in fuzzy_results.items():
        combined_values[indicator_id] = fuzzy_score

    audit_logger.log_transformation(
        stage="Indicator Combination",
        input_data={"quantitative": indicator_values, "fuzzy": fuzzy_results},
        output_data={"combined": combined_values}
    )

    return combined_values


def _prepare_topsis_input(indicator_values: Dict[str, Any],
                         audit_logger: AuditLogger) -> np.ndarray:
    """Prepare input matrix for TOPSIS (single scheme evaluation)."""
    # For single scheme evaluation, compare against a baseline
    # Create a 2x15 matrix: [baseline, scheme]

    # Baseline values (moderate performance)
    baseline_values = {
        'C1_1': 50.0, 'C1_2': 0.5, 'C1_3': 500.0,
        'C2_1': 30.0, 'C2_2': 0.5, 'C2_3': 100.0,
        'C3_1': 100.0, 'C3_2': 0.6, 'C3_3': 5.0,
        'C4_1': 100.0, 'C4_2': 0.7, 'C4_3': 50.0,
        'C5_1': 0.6, 'C5_2': 20.0, 'C5_3': 0.6
    }

    # Ensure consistent ordering
    indicator_order = [
        'C1_1', 'C1_2', 'C1_3', 'C2_1', 'C2_2', 'C2_3',
        'C3_1', 'C3_2', 'C3_3', 'C4_1', 'C4_2', 'C4_3',
        'C5_1', 'C5_2', 'C5_3'
    ]

    baseline_row = [baseline_values[ind_id] for ind_id in indicator_order]
    scheme_row = [indicator_values[ind_id] for ind_id in indicator_order]

    decision_matrix = np.array([baseline_row, scheme_row])

    audit_logger.log_transformation(
        stage="TOPSIS Input Preparation",
        input_data={"indicator_values": indicator_values},
        output_data={"decision_matrix_shape": decision_matrix.shape}
    )

    return decision_matrix


def _apply_topsis(decision_matrix: np.ndarray,
                 global_weights: Dict[str, float],
                 audit_logger: AuditLogger) -> Dict[str, Any]:
    """Apply TOPSIS ranking to decision matrix."""
    # Prepare weights array in consistent order
    indicator_order = [
        'C1_1', 'C1_2', 'C1_3', 'C2_1', 'C2_2', 'C2_3',
        'C3_1', 'C3_2', 'C3_3', 'C4_1', 'C4_2', 'C4_3',
        'C5_1', 'C5_2', 'C5_3'
    ]

    weights_array = np.array([global_weights[ind_id] for ind_id in indicator_order])

    # Determine indicator types
    indicator_types = ['benefit'] * 15  # Simplified for single scheme
    # Cost indicators: C2_1 (response time), C4_3 (latency)
    cost_indicators = {'C2_1', 'C4_3'}
    for i, ind_id in enumerate(indicator_order):
        if ind_id in cost_indicators:
            indicator_types[i] = 'cost'

    # Apply TOPSIS
    topsis_result = topsis_rank(decision_matrix, weights_array, indicator_types)

    audit_logger.log_transformation(
        stage="TOPSIS Ranking",
        input_data={"matrix_shape": decision_matrix.shape, "weights": weights_array},
        output_data={"Ci": topsis_result['Ci'], "rankings": topsis_result['rankings']},
        metadata={"validation": topsis_result['validation']}
    )

    return topsis_result


def _get_indicator_types(indicator_config: Dict[str, Any]) -> List[str]:
    """Get indicator types from configuration."""
    indicator_order = [
        'C1_1', 'C1_2', 'C1_3', 'C2_1', 'C2_2', 'C2_3',
        'C3_1', 'C3_2', 'C3_3', 'C4_1', 'C4_2', 'C4_3',
        'C5_1', 'C5_2', 'C5_3'
    ]

    secondary_indicators = indicator_config['secondary_indicators']
    indicator_types = []

    for ind_id in indicator_order:
        if ind_id in secondary_indicators:
            indicator_types.append(secondary_indicators[ind_id].get('type', 'benefit'))
        else:
            indicator_types.append('benefit')  # Default

    return indicator_types


def _generate_evaluation_result(scheme_data: Dict[str, Any],
                              combined_values: Dict[str, float],
                              global_weights: Dict[str, float],
                              topsis_result: Dict[str, Any],
                              audit_logger: AuditLogger) -> Dict[str, Any]:
    """Generate final evaluation result."""
    # Get scheme's Ci score (index 1, since index 0 is baseline)
    ci_score = float(topsis_result['Ci'][1])
    raw_rank = int(topsis_result['rankings'][1])

    # For single scheme evaluation, always return rank 1
    # The actual comparison with baseline is reflected in the Ci score
    rank = 1

    # Prepare result in required format
    result = {
        'scheme_id': scheme_data['scheme_id'],
        'scenario_id': scheme_data.get('scenario_context', 'unknown'),
        'ci_score': ci_score,
        'rank': rank,
        'indicator_values': combined_values,
        'normalized_values': topsis_result['normalized_matrix'][1].tolist(),
        'weighted_values': topsis_result['weighted_matrix'][1].tolist(),
        'audit_trail': audit_logger.get_audit_trail(),
        'evaluation_metadata': {
            'timestamp': datetime.now().isoformat(),
            'method': 'AHP-FCE-TOPSIS',
            'baseline_comparison': True,
            'validation_passed': topsis_result['validation']['valid'],
            'baseline_comparison_rank': raw_rank,  # Actual rank vs baseline (1=better, 2=worse)
            'baseline_ci_score': float(topsis_result['Ci'][0]),  # Baseline Ci score
            'performance_vs_baseline': 'better' if raw_rank == 1 else 'worse'
        }
    }

    # Validate result
    validation = validate_evaluation_result(result, strict_mode=False)
    if not validation['is_valid']:
        result['validation_errors'] = validation['errors']

    return result


# ==================== 场景感知评估函数 ====================

def _calculate_scenario_aware_indicator_value(indicator_id: str,
                                               indicator_config: Dict[str, Any],
                                               scheme_data: Dict[str, Any],
                                               sim_params: Dict[str, Any],
                                               base_value: float,
                                               adjusted_multipliers: Dict[str, float]) -> float:
    """Calculate scenario-aware value for a single indicator."""
    # Apply platform scaling
    platform_inventory = scheme_data.get('platform_inventory', {})
    total_platforms = sum(data.get('count', 0) for data in platform_inventory.values())
    platform_scale = total_platforms / 10.0 if total_platforms > 0 else 1.0

    # Start with base value
    value = base_value

    # Apply simulation parameter multipliers with scenario adjustments
    for param, factor in adjusted_multipliers.items():
        if param in sim_params:
            multiplier = sim_params[param]

            # Special handling for stealth factor (reverse effect on detection)
            if param == 'stealth_factor' and indicator_id == 'C1_1':
                value *= (2.0 - multiplier)  # Better stealth = harder detection
            else:
                value *= multiplier

    # Apply platform scaling for applicable indicators
    scaling_indicators = ['C1_1', 'C1_3', 'C2_3', 'C3_3', 'C4_1']
    if indicator_id in scaling_indicators:
        value *= platform_scale

    # Apply indicator type specific processing
    indicator_type = indicator_config.get('type', 'benefit')
    if indicator_type == 'cost':
        # For cost indicators, value should be minimized
        if indicator_id == 'C2_1':  # Response time
            value = max(10.0, value)  # Minimum 10 seconds
        elif indicator_id == 'C4_3':  # Data latency
            value = max(10.0, value)  # Minimum 10ms

    return float(value)


def _apply_scenario_weight_adjustments(global_weights: Dict[str, float],
                                      scenario_integrator,
                                      audit_logger: AuditLogger) -> Dict[str, float]:
    """Apply scenario-based weight adjustments to global weights."""
    adjusted_weights = global_weights.copy()

    # Get scenario objective weights
    objective_weights = getattr(scenario_integrator, 'objective_weights', {})

    # Map objectives to indicators and apply adjustments
    objective_to_indicators = {
        'surveillance_effectiveness': ['C1_1', 'C1_2', 'C1_3'],
        'target_tracking_capability': ['C1_2', 'C2_2'],
        'warning_timeliness': ['C2_1', 'C2_3'],
        'communication_reliability': ['C4_1', 'C4_2'],
        'strike_effectiveness': ['C3_1', 'C3_3'],
        'anti_submarine_capability': ['C1_1', 'C3_3'],
        'mine_clearance_effectiveness': ['C3_2', 'C2_3'],
        'obstacle_removal_capability': ['C3_2', 'C5_2'],
        'blockade_effectiveness': ['C1_1', 'C2_2', 'C3_1'],
        'interception_capability': ['C2_1', 'C3_1'],
        'surveillance_persistence': ['C1_3', 'C5_3']
    }

    # Apply weight adjustments based on scenario objectives
    for objective, weight in objective_weights.items():
        if objective in objective_to_indicators:
            adjustment_factor = 1.0 + (weight - 0.25)  # Normalize around 0.25
            for indicator_id in objective_to_indicators[objective]:
                if indicator_id in adjusted_weights:
                    adjusted_weights[indicator_id] *= adjustment_factor

    # Renormalize weights to maintain sum = 1
    total_weight = sum(adjusted_weights.values())
    if total_weight > 0:
        for indicator_id in adjusted_weights:
            adjusted_weights[indicator_id] /= total_weight

    audit_logger.log_transformation(
        stage="Scenario Weight Adjustment",
        input_data={"objective_weights": objective_weights},
        output_data={"adjusted_weights": adjusted_weights}
    )

    return adjusted_weights


def _apply_scenario_aware_fuzzy_evaluation(indicator_values: Dict[str, float],
                                         fuzzy_config: Dict[str, Any],
                                         scenario_integrator,
                                         audit_logger: AuditLogger) -> Dict[str, float]:
    """Apply scenario-aware fuzzy evaluation to qualitative indicators."""
    fuzzy_results = {}
    fuzzy_scale = fuzzy_config['fuzzy_scale']
    applicable_indicators = fuzzy_config.get('applicable_indicators', {})

    # Apply fuzzy evaluation to applicable indicators
    for indicator_id in applicable_indicators:
        if indicator_id in indicator_values:
            # Generate fuzzy assessment with scenario awareness
            quantitative_value = indicator_values[indicator_id]

            if hasattr(scenario_integrator, 'adjust_fuzzy_evaluation_thresholds'):
                fuzzy_assessment = scenario_integrator.adjust_fuzzy_evaluation_thresholds(
                    quantitative_value, indicator_id
                )
            else:
                fuzzy_assessment = _generate_fuzzy_assessment(quantitative_value, indicator_id)

            try:
                result = fuzzy_evaluate(fuzzy_assessment, fuzzy_scale)
                fuzzy_results[indicator_id] = result['fuzzy_score']
            except Exception as e:
                # Fallback to moderate assessment
                default_assessment = {'差': 0, '中': 1, '良': 0, '优': 0}
                result = fuzzy_evaluate(default_assessment, fuzzy_scale)
                fuzzy_results[indicator_id] = result['fuzzy_score']

    audit_logger.log_transformation(
        stage="Scenario-Aware Fuzzy Evaluation",
        input_data={"applicable_indicators": list(applicable_indicators.keys()), "scenario": scenario_integrator.scenario_id},
        output_data={"fuzzy_scores": fuzzy_results}
    )

    return fuzzy_results


def _prepare_scenario_aware_topsis_input(indicator_values: Dict[str, float],
                                         scenario_integrator,
                                         audit_logger: AuditLogger) -> np.ndarray:
    """Prepare TOPSIS input with scenario considerations."""
    # Baseline values (can be adjusted based on scenario)
    baseline_values = {
        'C1_1': 50.0, 'C1_2': 0.5, 'C1_3': 500.0,
        'C2_1': 30.0, 'C2_2': 0.5, 'C2_3': 100.0,
        'C3_1': 100.0, 'C3_2': 0.6, 'C3_3': 5.0,
        'C4_1': 100.0, 'C4_2': 0.7, 'C4_3': 50.0,
        'C5_1': 0.6, 'C5_2': 20.0, 'C5_3': 0.6
    }

    # Apply scenario adjustments to baseline
    if hasattr(scenario_integrator, 'get_scenario_adjusted_base_values'):
        adjusted_baseline = scenario_integrator.get_scenario_adjusted_base_values(baseline_values)
        # Keep only the indicators that are in our standard set
        for key in baseline_values:
            if key in adjusted_baseline:
                baseline_values[key] = adjusted_baseline[key]

    # Ensure consistent ordering
    indicator_order = [
        'C1_1', 'C1_2', 'C1_3', 'C2_1', 'C2_2', 'C2_3',
        'C3_1', 'C3_2', 'C3_3', 'C4_1', 'C4_2', 'C4_3',
        'C5_1', 'C5_2', 'C5_3'
    ]

    baseline_row = [baseline_values[ind_id] for ind_id in indicator_order]
    scheme_row = [indicator_values[ind_id] for ind_id in indicator_order]

    decision_matrix = np.array([baseline_row, scheme_row])

    audit_logger.log_transformation(
        stage="Scenario-Aware TOPSIS Input Preparation",
        input_data={"indicator_values": indicator_values, "scenario": scenario_integrator.scenario_id},
        output_data={"decision_matrix_shape": decision_matrix.shape}
    )

    return decision_matrix


def _generate_scenario_aware_evaluation_result(scheme_data: Dict[str, Any],
                                              combined_values: Dict[str, float],
                                              global_weights: Dict[str, float],
                                              topsis_result: Dict[str, Any],
                                              scenario_integrator,
                                              audit_logger: AuditLogger) -> Dict[str, Any]:
    """Generate scenario-aware final evaluation result."""
    # Get scheme's Ci score (index 1, since index 0 is baseline)
    ci_score = float(topsis_result['Ci'][1])
    raw_rank = int(topsis_result['rankings'][1])

    # For single scheme evaluation, always return rank 1
    rank = 1

    # Calculate scenario-specific success score
    if hasattr(scenario_integrator, 'calculate_scenario_success_score'):
        scenario_success_score = scenario_integrator.calculate_scenario_success_score(combined_values)
    else:
        scenario_success_score = 0.7  # Default score

    # Prepare result in required format
    result = {
        'scheme_id': scheme_data['scheme_id'],
        'scenario_id': getattr(scenario_integrator, 'scenario_id', 'unknown'),
        'scenario_type': getattr(scenario_integrator, 'scenario_type', 'generic'),
        'ci_score': ci_score,
        'rank': rank,
        'indicator_values': combined_values,
        'normalized_values': topsis_result['normalized_matrix'][1].tolist(),
        'weighted_values': topsis_result['weighted_matrix'][1].tolist(),
        'audit_trail': audit_logger.get_audit_trail(),
        'evaluation_metadata': {
            'timestamp': datetime.now().isoformat(),
            'method': 'AHP-FCE-TOPSIS',
            'baseline_comparison': True,
            'validation_passed': topsis_result['validation']['valid'],
            'baseline_comparison_rank': raw_rank,  # Actual rank vs baseline (1=better, 2=worse)
            'baseline_ci_score': float(topsis_result['Ci'][0]),  # Baseline Ci score
            'performance_vs_baseline': 'better' if raw_rank == 1 else 'worse',
            'scenario_success_score': scenario_success_score,  # NEW: scenario-specific success score
            'scenario_aware_evaluation': True  # NEW: indicates scenario-aware evaluation was applied
        }
    }

    # Validate result
    validation = validate_evaluation_result(result, strict_mode=False)
    if not validation['is_valid']:
        result['validation_errors'] = validation['errors']

    return result


if __name__ == "__main__":
    # Example usage
    print("Testing Evaluator Module")
    print("Evaluator module requires proper configuration files for testing.")
    print("Use main.py with actual configuration files to run evaluations.")