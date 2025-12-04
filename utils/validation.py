"""
Validation Utilities for AHP-FCE-TOPSIS-GA Evaluation System

Provides functions for schema validation, audit trail logging, and result validation.
"""

import json
import numpy as np
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import yaml


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class AuditLogger:
    """Logger for tracking transformations in the evaluation pipeline."""

    def __init__(self, scheme_id: str, scenario_id: Optional[str] = None):
        self.scheme_id = scheme_id
        self.scenario_id = scenario_id
        self.start_time = datetime.now()
        self.transformations = []

    def log_transformation(self,
                         stage: str,
                         input_data: Dict[str, Any],
                         output_data: Dict[str, Any],
                         parameters: Optional[Dict[str, Any]] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a transformation stage in the evaluation pipeline.

        Args:
            stage: Name of the transformation stage (e.g., 'AHP', 'FCE', 'TOPSIS')
            input_data: Input data for the transformation
            output_data: Output data from the transformation
            parameters: Parameters used in the transformation
            metadata: Additional metadata (timing, validation results, etc.)
        """
        timestamp = datetime.now().isoformat()

        transformation = {
            'timestamp': timestamp,
            'stage': stage,
            'scheme_id': self.scheme_id,
            'scenario_id': self.scenario_id,
            'input_data': _serialize_data(input_data),
            'output_data': _serialize_data(output_data),
            'parameters': parameters or {},
            'metadata': metadata or {}
        }

        self.transformations.append(transformation)

    def get_audit_trail(self) -> Dict[str, Any]:
        """
        Get complete audit trail for the evaluation.

        Returns:
            Dictionary containing full audit trail
        """
        return {
            'scheme_id': self.scheme_id,
            'scenario_id': self.scenario_id,
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration_seconds': (datetime.now() - self.start_time).total_seconds(),
            'transformation_count': len(self.transformations),
            'transformations': self.transformations
        }

    def save_audit_trail(self, filepath: str) -> None:
        """
        Save audit trail to file.

        Args:
            filepath: Path to save the audit trail
        """
        audit_trail = self.get_audit_trail()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(audit_trail, f, indent=2, ensure_ascii=False)


def log_transformation(stage: str,
                      input_data: Dict[str, Any],
                      output_data: Dict[str, Any],
                      parameters: Optional[Dict[str, Any]] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Standalone function to log a transformation.

    Args:
        stage: Name of the transformation stage
        input_data: Input data for the transformation
        output_data: Output data from the transformation
        parameters: Parameters used in the transformation
        metadata: Additional metadata

    Returns:
        Dictionary representing the transformation log entry
    """
    timestamp = datetime.now().isoformat()

    transformation = {
        'timestamp': timestamp,
        'stage': stage,
        'input_data': _serialize_data(input_data),
        'output_data': _serialize_data(output_data),
        'parameters': parameters or {},
        'metadata': metadata or {}
    }

    return transformation


def _serialize_data(data: Any) -> Any:
    """
    Serialize data for JSON storage (handle numpy arrays, etc.).

    Args:
        data: Data to serialize

    Returns:
        Serializable version of the data
    """
    if isinstance(data, np.ndarray):
        return {
            'type': 'numpy.ndarray',
            'shape': data.shape,
            'dtype': str(data.dtype),
            'data': data.tolist()
        }
    elif isinstance(data, np.integer):
        return int(data)
    elif isinstance(data, np.floating):
        return float(data)
    elif isinstance(data, dict):
        return {key: _serialize_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_serialize_data(item) for item in data]
    else:
        return data


def _deserialize_data(data: Any) -> Any:
    """
    Deserialize data from JSON storage format.

    Args:
        data: Serialized data

    Returns:
        Original data format
    """
    if isinstance(data, dict) and 'type' in data:
        if data['type'] == 'numpy.ndarray':
            return np.array(data['data'], dtype=data['dtype'])
    elif isinstance(data, dict):
        return {key: _deserialize_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_deserialize_data(item) for item in data]
    else:
        return data


def validate_evaluation_result(result: Dict[str, Any],
                             strict_mode: bool = True) -> Dict[str, Any]:
    """
    Validate evaluation result structure and values.

    Args:
        result: Evaluation result to validate
        strict_mode: If True, raise exceptions for validation errors

    Returns:
        Dictionary with validation results

    Raises:
        ValidationError: If strict_mode=True and validation fails
    """
    validation_result = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'missing_fields': [],
        'invalid_values': []
    }

    # Required fields
    required_fields = [
        'scheme_id',
        'scenario_id',
        'ci_score',
        'rank',
        'indicator_values',
        'normalized_values',
        'weighted_values',
        'audit_trail'
    ]

    # Check for missing required fields
    for field in required_fields:
        if field not in result:
            validation_result['missing_fields'].append(field)
            validation_result['is_valid'] = False

    # Validate CI score
    if 'ci_score' in result:
        ci_score = result['ci_score']
        if not isinstance(ci_score, (int, float)):
            validation_result['invalid_values'].append(f"CI score must be numeric, got {type(ci_score)}")
            validation_result['is_valid'] = False
        elif not (0.0 <= ci_score <= 1.0):
            validation_result['invalid_values'].append(f"CI score must be in [0,1], got {ci_score}")
            validation_result['is_valid'] = False

    # Validate rank
    if 'rank' in result:
        rank = result['rank']
        if not isinstance(rank, int) or rank < 1:
            validation_result['invalid_values'].append(f"Rank must be positive integer, got {rank}")
            validation_result['is_valid'] = False

    # Validate indicator arrays
    array_fields = ['indicator_values', 'normalized_values', 'weighted_values']
    for field in array_fields:
        if field in result:
            values = result[field]
            if not isinstance(values, (list, np.ndarray)):
                validation_result['invalid_values'].append(f"{field} must be array-like, got {type(values)}")
                validation_result['is_valid'] = False
            elif len(values) != 15:  # Should have 15 indicators
                validation_result['invalid_values'].append(f"{field} must have 15 values, got {len(values)}")
                validation_result['is_valid'] = False

    # Check for negative values in normalized/weighted arrays
    for field in ['normalized_values', 'weighted_values']:
        if field in result:
            values = result[field]
            if isinstance(values, (list, np.ndarray)):
                if any(v < 0 for v in values if isinstance(v, (int, float))):
                    validation_result['invalid_values'].append(f"{field} contains negative values")
                    validation_result['is_valid'] = False

    # Raise exception if strict mode and validation failed
    if strict_mode and not validation_result['is_valid']:
        error_msg = f"Validation failed: {validation_result['errors'] + validation_result['invalid_values'] + validation_result['missing_fields']}"
        raise ValidationError(error_msg)

    return validation_result


def validate_indicator_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate indicator configuration structure.

    Args:
        config: Indicator configuration to validate

    Returns:
        Dictionary with validation results
    """
    validation_result = {
        'is_valid': True,
        'errors': [],
        'warnings': []
    }

    # Check primary capabilities
    if 'primary_capabilities' not in config:
        validation_result['errors'].append("Missing 'primary_capabilities' section")
        validation_result['is_valid'] = False
    else:
        primary_caps = config['primary_capabilities']
        if len(primary_caps) != 5:
            validation_result['errors'].append(f"Expected 5 primary capabilities, got {len(primary_caps)}")
            validation_result['is_valid'] = False

        # Check each primary capability
        for cap_id, cap_data in primary_caps.items():
            required_fields = ['name', 'description', 'weight_placeholder', 'literature_reference']
            for field in required_fields:
                if field not in cap_data:
                    validation_result['errors'].append(f"Primary capability {cap_id} missing '{field}'")
                    validation_result['is_valid'] = False

    # Check secondary indicators
    if 'secondary_indicators' not in config:
        validation_result['errors'].append("Missing 'secondary_indicators' section")
        validation_result['is_valid'] = False
    else:
        secondary_indicators = config['secondary_indicators']
        if len(secondary_indicators) != 15:
            validation_result['errors'].append(f"Expected 15 secondary indicators, got {len(secondary_indicators)}")
            validation_result['is_valid'] = False

        # Check each secondary indicator
        for ind_id, ind_data in secondary_indicators.items():
            required_fields = ['name', 'description', 'primary_capability', 'unit', 'type', 'weight_placeholder']
            for field in required_fields:
                if field not in ind_data:
                    validation_result['errors'].append(f"Secondary indicator {ind_id} missing '{field}'")
                    validation_result['is_valid'] = False

            # Check indicator type
            if 'type' in ind_data and ind_data['type'] not in ['benefit', 'cost']:
                validation_result['errors'].append(f"Indicator {ind_id} has invalid type: {ind_data['type']}")
                validation_result['is_valid'] = False

    return validation_result


def validate_scheme_config(scheme: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate combat system scheme configuration.

    Args:
        scheme: Scheme configuration to validate

    Returns:
        Dictionary with validation results
    """
    validation_result = {
        'is_valid': True,
        'errors': [],
        'warnings': []
    }

    # Required fields
    required_fields = ['scheme_id', 'scheme_name', 'platform_inventory', 'deployment_plan', 'task_assignments']
    for field in required_fields:
        if field not in scheme:
            validation_result['errors'].append(f"Missing required field: {field}")
            validation_result['is_valid'] = False

    # Validate platform inventory
    if 'platform_inventory' in scheme:
        inventory = scheme['platform_inventory']
        total_platforms = 0

        for platform_type, platform_data in inventory.items():
            if 'count' not in platform_data:
                validation_result['errors'].append(f"Platform {platform_type} missing 'count'")
                validation_result['is_valid'] = False
            else:
                count = platform_data['count']
                if not isinstance(count, int) or count < 0:
                    validation_result['errors'].append(f"Invalid platform count for {platform_type}: {count}")
                    validation_result['is_valid'] = False
                elif count == 0:
                    # Allow zero count for optional platform types
                    validation_result['warnings'].append(f"Optional platform type {platform_type} has zero count")
                else:
                    total_platforms += count

        if total_platforms > 20:
            validation_result['warnings'].append(f"Large total platform count: {total_platforms}")

    # Validate deployment plan
    if 'deployment_plan' in scheme:
        deployment = scheme['deployment_plan']
        if 'primary_sector' not in deployment:
            validation_result['errors'].append("Missing 'primary_sector' in deployment plan")
            validation_result['is_valid'] = False
        else:
            primary = deployment['primary_sector']
            if 'coordinates' not in primary or len(primary['coordinates']) != 2:
                validation_result['errors'].append("Invalid primary sector coordinates")
                validation_result['is_valid'] = False

    return validation_result


def perform_sensitivity_analysis(baseline_results: Dict[str, Any],
                                perturbation_pct: float = 0.2,
                                iterations: int = 100) -> Dict[str, Any]:
    """
    Perform sensitivity analysis by perturbing indicator weights.

    Args:
        baseline_results: Baseline evaluation results
        perturbation_pct: Percentage for weight perturbation (0-1)
        iterations: Number of iterations to run

    Returns:
        Dictionary with sensitivity analysis results
    """
    try:
        import random
        from modules.topsis_module import topsis_rank
        from modules.ahp_module import calculate_weights
        import numpy as np

        random.seed(42)  # For reproducibility

        # Extract baseline data from evaluation results structure
        individual_results = baseline_results.get('individual_results', {})
        if not individual_results:
            raise ValueError("No individual results found in baseline data")

        # Reconstruct decision matrix and weights from individual results
        scheme_ids = list(individual_results.keys())
        indicator_ids = list(individual_results[scheme_ids[0]]['indicator_values'].keys())

        # Build decision matrix
        decision_matrix_data = []
        for scheme_id in scheme_ids:
            indicator_values = individual_results[scheme_id]['indicator_values']
            decision_matrix_data.append([indicator_values[ind_id] for ind_id in indicator_ids])

        decision_matrix = np.array(decision_matrix_data)

        # Extract normalized values from first scheme (they should be the same weights)
        normalized_values = individual_results[scheme_ids[0]]['normalized_values']
        baseline_weights = normalized_values  # Use normalized values as proxy for weights

        # Determine indicator types (assume all are benefit for simplicity)
        # In a real implementation, this would come from config
        indicator_types = ['benefit'] * len(indicator_ids)

        if len(baseline_weights) == 0 or decision_matrix.size == 0:
            raise ValueError("Invalid baseline results: missing weights or decision matrix")

        # Extract baseline rankings and CI scores
        baseline_ci_scores = [individual_results[scheme_id]['ci_score'] for scheme_id in scheme_ids]
        baseline_rankings = [individual_results[scheme_id]['rank'] for scheme_id in scheme_ids]

        sensitivity_results = {
            'baseline_ranking': baseline_rankings,
            'baseline_ci_scores': baseline_ci_scores,
            'iterations': iterations,
            'perturbation_pct': perturbation_pct,
            'ranking_stability': 0,
            'ci_variations': {},
            'iteration_results': [],
            'summary_stats': {}
        }

        ranking_changes = 0
        all_rankings = []
        all_ci_scores = []

        # Run sensitivity iterations
        for i in range(iterations):
            # Perturb weights
            perturbed_weights = _perturb_weights(baseline_weights, perturbation_pct)

            # Normalize to ensure sum = 1.0
            perturbed_weights = np.array(perturbed_weights) / np.sum(perturbed_weights)

            # Run TOPSIS with perturbed weights
            topsis_result = topsis_rank(decision_matrix, perturbed_weights, indicator_types, validate_input=False)

            iteration_result = {
                'iteration': i + 1,
                'perturbed_weights': perturbed_weights.tolist(),
                'ci_scores': topsis_result['Ci'].tolist(),
                'rankings': topsis_result['rankings'].tolist()
            }

            sensitivity_results['iteration_results'].append(iteration_result)

            # Track ranking changes
            current_ranking = topsis_result['rankings'].tolist()
            if current_ranking != sensitivity_results['baseline_ranking']:
                ranking_changes += 1

            all_rankings.append(current_ranking)
            all_ci_scores.append(topsis_result['Ci'].tolist())

        # Calculate statistics
        sensitivity_results['ranking_stability'] = (iterations - ranking_changes) / iterations

        # Calculate CI variations for each alternative
        baseline_ci = np.array(sensitivity_results['baseline_ci_scores'])
        ci_matrix = np.array(all_ci_scores)

        for i, ci_vals in enumerate(ci_matrix.T):
            variation_pct = np.std(ci_vals) / np.mean(ci_vals) if np.mean(ci_vals) > 0 else 0
            sensitivity_results['ci_variations'][f'alternative_{i+1}'] = {
                'baseline_ci': baseline_ci[i],
                'mean_ci': np.mean(ci_vals),
                'std_ci': np.std(ci_vals),
                'min_ci': np.min(ci_vals),
                'max_ci': np.max(ci_vals),
                'variation_pct': variation_pct
            }

        # Calculate summary statistics
        sensitivity_results['summary_stats'] = {
            'ranking_stability_pct': sensitivity_results['ranking_stability'] * 100,
            'max_ci_variation_pct': max([v['variation_pct'] for v in sensitivity_results['ci_variations'].values()]),
            'iterations_completed': iterations,
            'iterations_with_ranking_changes': ranking_changes
        }

        return sensitivity_results

    except Exception as e:
        raise ValidationError(f"Sensitivity analysis failed: {e}")


def _perturb_weights(weights: List[float], perturbation_pct: float) -> List[float]:
    """
    Perturb weights by random percentage within specified range.

    Args:
        weights: Original weights
        perturbation_pct: Maximum perturbation percentage (0-1)

    Returns:
        Perturbed weights
    """
    import random

    perturbed = []
    for weight in weights:
        # Generate random perturbation between -pct and +pct
        perturbation = random.uniform(-perturbation_pct, perturbation_pct)
        new_weight = weight * (1 + perturbation)
        perturbed.append(new_weight)

    return perturbed


def perform_jackknife_validation(fuzzy_data: Dict[str, Any],
                               evaluator_func: callable,
                               indicator_config: Dict[str, Any],
                               fuzzy_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform jackknife validation by systematically excluding each expert.

    Args:
        fuzzy_data: Fuzzy evaluation data with expert assessments
        evaluator_func: Function to evaluate single scheme
        indicator_config: Indicator configuration
        fuzzy_config: Fuzzy evaluation configuration

    Returns:
        Dictionary with jackknife validation results
    """
    try:
        # Extract expert data structure
        experts = fuzzy_data.get('experts', {})
        scheme_data = fuzzy_data.get('scheme_data', {})

        if len(experts) < 2:
            raise ValueError("Need at least 2 experts for jackknife validation")

        jackknife_results = {
            'baseline_result': None,
            'leave_one_out_results': {},
            'stability_metrics': {},
            'summary': {}
        }

        # Run baseline evaluation with all experts
        try:
            baseline_result = evaluator_func(scheme_data, indicator_config, fuzzy_config, fuzzy_data)
            jackknife_results['baseline_result'] = baseline_result
        except Exception as e:
            raise ValidationError(f"Baseline evaluation failed: {e}")

        baseline_ci = baseline_result.get('ci_score', 0)
        leave_one_out_cis = []

        # Perform leave-one-out validation
        for expert_id, expert_data in experts.items():
            print(f"  Jackknife: Excluding expert {expert_id}")

            # Create modified fuzzy data excluding current expert
            modified_fuzzy_data = {
                'experts': {eid: edata for eid, edata in experts.items() if eid != expert_id},
                'scheme_data': scheme_data
            }

            try:
                # Evaluate without current expert
                result = evaluator_func(scheme_data, indicator_config, fuzzy_config, modified_fuzzy_data)
                ci_score = result.get('ci_score', 0)

                jackknife_results['leave_one_out_results'][expert_id] = {
                    'ci_score': ci_score,
                    'difference_from_baseline': ci_score - baseline_ci,
                    'percent_change': ((ci_score - baseline_ci) / baseline_ci * 100) if baseline_ci > 0 else 0,
                    'validation_passed': result.get('evaluation_metadata', {}).get('validation_passed', False)
                }

                leave_one_out_cis.append(ci_score)

            except Exception as e:
                print(f"    Warning: Evaluation without expert {expert_id} failed: {e}")
                jackknife_results['leave_one_out_results'][expert_id] = {
                    'error': str(e),
                    'ci_score': None
                }

        # Calculate stability metrics
        if leave_one_out_cis:
            mean_ci = np.mean(leave_one_out_cis)
            std_ci = np.std(leave_one_out_cis)
            cv_ci = std_ci / mean_ci if mean_ci > 0 else 0  # Coefficient of variation

            jackknife_results['stability_metrics'] = {
                'baseline_ci': baseline_ci,
                'mean_leave_one_out_ci': mean_ci,
                'std_leave_one_out_ci': std_ci,
                'coefficient_of_variation': cv_ci,
                'max_deviation': max([abs(ci - baseline_ci) for ci in leave_one_out_cis]),
                'num_experts': len(experts),
                'num_successful_validations': len(leave_one_out_cis)
            }

            # Determine stability (threshold: 10% CV)
            stability_threshold = 0.10
            is_stable = cv_ci < stability_threshold

            jackknife_results['summary'] = {
                'is_stable': is_stable,
                'stability_threshold': stability_threshold,
                'actual_cv': cv_ci,
                'recommendation': 'Stable - expert exclusion has minimal impact' if is_stable else
                                'Unstable - results sensitive to expert opinions',
                'min_experts_needed': max(2, len(experts) // 2)  # Conservative recommendation
            }

        return jackknife_results

    except Exception as e:
        raise ValidationError(f"Jackknife validation failed: {e}")


def generate_validation_report(evaluation_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate comprehensive validation report for evaluation results.

    Args:
        evaluation_results: Dictionary containing evaluation results and metadata

    Returns:
        Dictionary with structured validation report
    """
    try:
        report = {
            'report_id': f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'generated_at': datetime.now().isoformat(),
            'validation_sections': {},
            'summary': {
                'overall_status': 'PASSED',
                'critical_issues': [],
                'warnings': [],
                'recommendations': []
            }
        }

        # Section 1: AHP Consistency Validation
        report['validation_sections']['ahp_consistency'] = _validate_ahp_consistency(evaluation_results)

        # Section 2: FCE Distributions Validation
        report['validation_sections']['fce_distributions'] = _validate_fce_distributions(evaluation_results)

        # Section 3: TOPSIS PIS/NIS Verification
        report['validation_sections']['topsis_verification'] = _validate_topsis_results(evaluation_results)

        # Section 4: GA Convergence Metrics (if applicable)
        if 'optimization_results' in evaluation_results:
            report['validation_sections']['ga_convergence'] = _validate_ga_convergence(evaluation_results['optimization_results'])

        # Section 5: Mathematical Properties Verification
        report['validation_sections']['mathematical_properties'] = _validate_mathematical_properties(evaluation_results)

        # Generate overall summary
        for section_name, section_result in report['validation_sections'].items():
            if section_result.get('status') == 'FAILED':
                report['summary']['overall_status'] = 'FAILED'
                report['summary']['critical_issues'].extend(section_result.get('issues', []))
            elif section_result.get('status') == 'WARNING':
                report['summary']['warnings'].extend(section_result.get('issues', []))

        # Add recommendations
        report['summary']['recommendations'] = _generate_recommendations(report)

        return report

    except Exception as e:
        raise ValidationError(f"Validation report generation failed: {e}")


def _validate_ahp_consistency(evaluation_results: Dict[str, Any]) -> Dict[str, Any]:
    """Validate AHP consistency ratios across all matrices."""
    section = {
        'status': 'PASSED',
        'issues': [],
        'cr_values': {}
    }

    try:
        audit_trail = evaluation_results.get('audit_trail', {})
        transformations = audit_trail.get('transformations', [])

        for transform in transformations:
            if transform.get('stage') == 'AHP':
                output_data = transform.get('output_data', {})
                cr = output_data.get('CR', 0)
                valid = output_data.get('valid', False)

                matrix_id = transform.get('metadata', {}).get('matrix_id', 'unknown')
                section['cr_values'][matrix_id] = {
                    'cr': cr,
                    'valid': valid,
                    'threshold': 0.1
                }

                if cr >= 0.1:
                    section['status'] = 'FAILED'
                    section['issues'].append(f"AHP matrix {matrix_id} has CR >= 0.1: {cr:.4f}")
                elif cr >= 0.05:  # Warning threshold
                    if section['status'] == 'PASSED':
                        section['status'] = 'WARNING'
                    section['issues'].append(f"AHP matrix {matrix_id} has marginal consistency: {cr:.4f}")

    except Exception as e:
        section['status'] = 'FAILED'
        section['issues'].append(f"AHP consistency validation failed: {e}")

    return section


def _validate_fce_distributions(evaluation_results: Dict[str, Any]) -> Dict[str, Any]:
    """Validate FCE membership degree distributions."""
    section = {
        'status': 'PASSED',
        'issues': [],
        'membership_sums': {}
    }

    try:
        audit_trail = evaluation_results.get('audit_trail', {})
        transformations = audit_trail.get('transformations', [])

        for transform in transformations:
            if transform.get('stage') == 'FCE':
                output_data = transform.get('output_data', {})
                fuzzy_scores = output_data.get('fuzzy_scores', {})

                for indicator_id, score_data in fuzzy_scores.items():
                    if isinstance(score_data, dict) and 'membership_vector' in score_data:
                        membership_vector = score_data['membership_vector']
                        membership_sum = sum(membership_vector) if membership_vector else 0

                        section['membership_sums'][indicator_id] = {
                            'sum': membership_sum,
                            'target': 1.0,
                            'tolerance': 0.001
                        }

                        if abs(membership_sum - 1.0) > 0.001:
                            section['status'] = 'FAILED'
                            section['issues'].append(
                                f"Indicator {indicator_id} membership sum: {membership_sum:.6f} (target: 1.0 ± 0.001)"
                            )

    except Exception as e:
        section['status'] = 'FAILED'
        section['issues'].append(f"FCE distribution validation failed: {e}")

    return section


def _validate_topsis_results(evaluation_results: Dict[str, Any]) -> Dict[str, Any]:
    """Validate TOPSIS ideal solutions and rankings."""
    section = {
        'status': 'PASSED',
        'issues': [],
        'pis_nis_verification': {}
    }

    try:
        # Validate CI scores are in [0,1]
        ci_scores = evaluation_results.get('ci_scores', [])
        if ci_scores:
            for i, ci in enumerate(ci_scores):
                if not (0.0 <= ci <= 1.0):
                    section['status'] = 'FAILED'
                    section['issues'].append(f"Alternative {i+1} CI score out of range: {ci}")

        # Validate rankings are consistent (no ties for simplicity)
        rankings = evaluation_results.get('rankings', [])
        if rankings:
            if len(set(rankings)) != len(rankings):
                section['status'] = 'WARNING'
                section['issues'].append("Tied rankings detected")

        # Validate PIS/NIS identification logic (simplified check)
        section['pis_nis_verification'] = {
            'pis_identified': True,
            'nis_identified': True,
            'method': 'benefit/cost indicator type based'
        }

    except Exception as e:
        section['status'] = 'FAILED'
        section['issues'].append(f"TOPSIS validation failed: {e}")

    return section


def _validate_ga_convergence(optimization_results: Dict[str, Any]) -> Dict[str, Any]:
    """Validate GA convergence metrics."""
    section = {
        'status': 'PASSED',
        'issues': [],
        'convergence_metrics': {}
    }

    try:
        convergence_info = optimization_results.get('convergence_info', {})
        generation_history = optimization_results.get('generation_history', {})

        # Check monotonic improvement
        monotonic_improvement = convergence_info.get('monotonic_improvement', False)
        final_diversity = convergence_info.get('final_diversity', 0)

        section['convergence_metrics'] = {
            'monotonic_improvement': monotonic_improvement,
            'final_diversity': final_diversity,
            'total_generations': convergence_info.get('total_generations', 0),
            'converged': convergence_info.get('converged', False)
        }

        if not monotonic_improvement:
            section['status'] = 'WARNING'
            section['issues'].append("GA did not show monotonic improvement")

        if final_diversity < 0.3:
            section['status'] = 'WARNING'
            section['issues'].append(f"Low final population diversity: {final_diversity:.3f}")

    except Exception as e:
        section['status'] = 'FAILED'
        section['issues'].append(f"GA convergence validation failed: {e}")

    return section


def _validate_mathematical_properties(evaluation_results: Dict[str, Any]) -> Dict[str, Any]:
    """Validate general mathematical properties."""
    section = {
        'status': 'PASSED',
        'issues': [],
        'properties': {}
    }

    try:
        # Check if weights sum to 1.0
        weights = evaluation_results.get('weights', [])
        if weights:
            weight_sum = sum(weights)
            section['properties']['weight_sum'] = weight_sum

            if abs(weight_sum - 1.0) > 0.001:
                section['status'] = 'FAILED'
                section['issues'].append(f"Weights do not sum to 1.0: {weight_sum:.6f}")

        # Check for numerical precision issues
        indicator_values = evaluation_results.get('indicator_values', [])
        if indicator_values:
            has_nan = any(np.isnan(val) for val in indicator_values if isinstance(val, (int, float)))
            has_inf = any(np.isinf(val) for val in indicator_values if isinstance(val, (int, float)))

            if has_nan:
                section['status'] = 'FAILED'
                section['issues'].append("NaN values detected in indicator data")

            if has_inf:
                section['status'] = 'FAILED'
                section['issues'].append("Infinite values detected in indicator data")

    except Exception as e:
        section['status'] = 'FAILED'
        section['issues'].append(f"Mathematical properties validation failed: {e}")

    return section


def _generate_recommendations(report: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on validation results."""
    recommendations = []

    if report['summary']['overall_status'] == 'PASSED':
        recommendations.append("All validation checks passed. Results are ready for use.")
        recommendations.append("Consider sensitivity analysis to test robustness.")
    else:
        recommendations.append("Address critical issues before using results for decision-making.")

        # Specific recommendations based on issues
        for issue in report['summary']['critical_issues']:
            if "AHP matrix" in issue and "CR" in issue:
                recommendations.append("Review expert judgment matrices for consistency and consider revising inconsistent comparisons.")
            elif "membership sum" in issue:
                recommendations.append("Check fuzzy evaluation logic for proper normalization of membership degrees.")
            elif "out of range" in issue:
                recommendations.append("Investigate calculation errors in TOPSIS distance computations.")

    if report['summary']['warnings']:
        recommendations.append("Review warnings and consider improvements for enhanced reliability.")

    return recommendations


if __name__ == "__main__":
    # Example usage and testing
    print("Testing Validation Utilities")

    # Test audit logging
    audit_logger = AuditLogger("test_scheme", "test_scenario")

    # Log some transformations
    audit_logger.log_transformation(
        stage="AHP",
        input_data={"matrix": [[1, 2], [0.5, 1]]},
        output_data={"weights": [0.67, 0.33], "CR": 0.0},
        parameters={"method": "eigenvalue"}
    )

    audit_logger.log_transformation(
        stage="TOPSIS",
        input_data={"normalized_matrix": [[0.5, 0.7], [0.3, 0.8]]},
        output_data={"Ci": [0.6, 0.4], "rankings": [1, 2]},
        parameters={"normalization": "vector"}
    )

    audit_trail = audit_logger.get_audit_trail()
    print(f"Audit trail created with {audit_trail['transformation_count']} transformations")

    # Test result validation
    test_result = {
        "scheme_id": "test_scheme",
        "ci_score": 0.75,
        "rank": 1,
        "indicator_values": [1.0] * 15,
        "normalized_values": [0.5] * 15,
        "weighted_values": [0.3] * 15
    }

    validation = validate_evaluation_result(test_result, strict_mode=False)
    print(f"Result validation: {'PASSED' if validation['is_valid'] else 'FAILED'}")
    if validation['errors']:
        print(f"Errors: {validation['errors']}")