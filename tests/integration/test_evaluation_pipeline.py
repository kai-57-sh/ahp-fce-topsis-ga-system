"""
Integration Tests for Evaluation Pipeline

Tests end-to-end evaluation workflow combining AHP, FCE, and TOPSIS modules.
"""

import pytest
import numpy as np
import yaml
import sys
import os
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from modules.evaluator import evaluate_single_scheme, evaluate_batch
from modules.ahp_module import AHPConsistencyError
from modules.fce_module import FCEError
from modules.topsis_module import TOPSISError
from utils.validation import ValidationError, AuditLogger


class TestEvaluationPipeline:
    """Integration tests for complete evaluation pipeline."""

    @pytest.fixture
    def sample_configurations(self):
        """Load sample configurations from fixtures."""
        fixture_path = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'sample_schemes.yaml')
        with open(fixture_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def sample_matrices(self):
        """Load sample AHP matrices from fixtures."""
        fixture_path = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'sample_matrices.yaml')
        with open(fixture_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def indicator_config(self):
        """Sample indicator configuration."""
        return {
            'primary_capabilities': {
                'C1': {
                    'name': 'Surveillance Capability',
                    'description': 'ISR and surveillance capabilities',
                    'weight_placeholder': 0.25,
                    'literature_reference': 'Alberts 2000'
                },
                'C2': {
                    'name': 'Anti-Submarine Capability',
                    'description': 'ASW and underwater warfare',
                    'weight_placeholder': 0.25,
                    'literature_reference': 'Boyd 1987'
                },
                'C3': {
                    'name': 'Mine Countermeasures',
                    'description': 'Mine detection and clearance',
                    'weight_placeholder': 0.25,
                    'literature_reference': 'NATO MCM Doctrine'
                },
                'C4': {
                    'name': 'Command & Control',
                    'description': 'C4I and network capabilities',
                    'weight_placeholder': 0.15,
                    'literature_reference': 'Alberts 2000'
                },
                'C5': {
                    'name': 'Logistics & Sustainment',
                    'description': 'Support and sustainability',
                    'weight_placeholder': 0.10,
                    'literature_reference': 'Joint Publication 4-0'
                }
            },
            'secondary_indicators': {
                'C1_1': {
                    'name': 'Detection Range',
                    'description': 'Maximum detection range in km',
                    'primary_capability': 'C1',
                    'unit': 'km',
                    'type': 'benefit',
                    'weight_placeholder': 0.08,
                    'fuzzy_flag': True
                },
                'C1_2': {
                    'name': 'Coverage Area',
                    'description': 'Area coverage in square km',
                    'primary_capability': 'C1',
                    'unit': 'km²',
                    'type': 'benefit',
                    'weight_placeholder': 0.09,
                    'fuzzy_flag': True
                },
                'C1_3': {
                    'name': 'Target Classification',
                    'description': 'Target classification accuracy',
                    'primary_capability': 'C1',
                    'unit': 'percentage',
                    'type': 'benefit',
                    'weight_placeholder': 0.08,
                    'fuzzy_flag': True
                }
                # ... (would include all 15 indicators in full implementation)
            }
        }

    @pytest.fixture
    def fuzzy_config(self):
        """Sample fuzzy evaluation configuration."""
        return {
            'linguistic_scale': {
                '差': {'value': 0.25, 'description': 'Poor'},
                '中': {'value': 0.50, 'description': 'Medium'},
                '良': {'value': 0.75, 'description': 'Good'},
                '优': {'value': 1.00, 'description': 'Excellent'}
            },
            'applicable_indicators': [
                'C1_1', 'C1_2', 'C1_3',
                'C2_1', 'C2_2', 'C2_3',
                'C3_1', 'C3_2', 'C3_3',
                'C4_1', 'C4_2', 'C4_3',
                'C5_1', 'C5_2', 'C5_3'
            ]
        }

    @pytest.fixture
    def expert_judgments(self):
        """Sample expert judgments for AHP using real data files."""
        # Use real expert judgments to avoid file not found errors
        return {
            'primary_capabilities_file': 'data/expert_judgments/primary_capabilities.yaml',
            'secondary_indicators_dir': 'data/expert_judgments/secondary_indicators'
        }

    def test_evaluate_single_scheme_end_to_end(self, working_configurations):
        """Test complete single scheme evaluation workflow."""
        # Use working configurations from our test data loader
        scheme = working_configurations['available_schemes'][0]  # Use first available scheme
        indicator_config = working_configurations['indicator_config']
        fuzzy_config = working_configurations['fuzzy_config']
        expert_judgments = working_configurations['expert_judgments']

        # Record start time for performance testing
        start_time = time.time()

        # Evaluate single scheme
        result = evaluate_single_scheme(
            scheme, indicator_config, fuzzy_config, expert_judgments
        )

        # Record end time
        end_time = time.time()
        execution_time = end_time - start_time

        # Performance validation (SC-004: <0.5s per scheme evaluation)
        assert execution_time < 0.5, f"Evaluation took {execution_time:.3f}s, should be <0.5s"

        # Structure validation
        assert 'scheme_id' in result
        assert 'ci_score' in result
        assert 'rank' in result
        assert 'indicator_values' in result
        assert 'normalized_values' in result
        assert 'weighted_values' in result
        assert 'audit_trail' in result

        # Content validation
        assert result['scheme_id'] == scheme['scheme_id']
        assert 0.0 <= result['ci_score'] <= 1.0
        assert isinstance(result['rank'], int)
        assert result['rank'] > 0

        # Audit trail validation
        audit_trail = result['audit_trail']
        assert 'transformation_count' in audit_trail
        assert 'transformations' in audit_trail
        assert len(audit_trail['transformations']) > 0

        # Check transformation stages
        transformation_stages = [t['stage'] for t in audit_trail['transformations']]
        expected_stages = ['AHP Weight Calculation', 'Fuzzy Evaluation', 'TOPSIS Ranking']
        for stage in expected_stages:
            assert any(stage in ts for ts in transformation_stages), f"Missing {stage} transformation in audit trail. Found: {transformation_stages}"

    def test_evaluate_batch_ranking_consistency(self, working_configurations):
        """Test batch evaluation and ranking consistency."""
        # Use working configurations from our test data loader
        schemes = working_configurations['available_schemes'][:3]  # Use first 3 available schemes
        indicator_config = working_configurations['indicator_config']
        fuzzy_config = working_configurations['fuzzy_config']
        expert_judgments = working_configurations['expert_judgments']

        # Evaluate batch
        batch_result = evaluate_batch(
            schemes, indicator_config, fuzzy_config, expert_judgments
        )

        # Structure validation
        assert 'num_schemes' in batch_result
        assert 'individual_results' in batch_result
        assert 'best_scheme' in batch_result

        assert batch_result['num_schemes'] == len(schemes)
        assert len(batch_result['individual_results']) == len(schemes)

        # Ranking consistency validation
        individual_results = batch_result['individual_results']
        ci_scores = [result['ci_score'] for result in individual_results.values()]
        ranks = [result['rank'] for result in individual_results.values()]

        # Best scheme should have highest Ci score and rank 1
        best_scheme_id = batch_result['best_scheme']['scheme_id']
        best_result = individual_results[best_scheme_id]
        assert best_result['rank'] == 1
        assert best_result['ci_score'] == max(ci_scores)

        # Rankings should be unique and sequential
        expected_ranks = set(range(1, len(schemes) + 1))
        actual_ranks = set(ranks)
        assert actual_ranks == expected_ranks, f"Missing or duplicate ranks: {expected_ranks - actual_ranks}"

        # Higher Ci score should correspond to better (lower) rank
        sorted_by_ci = sorted(individual_results.items(), key=lambda x: x[1]['ci_score'], reverse=True)
        sorted_by_rank = sorted(individual_results.items(), key=lambda x: x[1]['rank'])

        for i, ((ci_id, ci_result), (rank_id, rank_result)) in enumerate(zip(sorted_by_ci, sorted_by_rank)):
            assert ci_id == rank_id, f"Scheme ordering mismatch at position {i}"

    def test_evaluation_pipeline_error_handling(self, indicator_config, fuzzy_config, expert_judgments):
        """Test error handling in evaluation pipeline."""
        # Test with invalid scheme (missing required fields)
        invalid_scheme = {
            'scheme_id': 'invalid_test',
            # Missing required fields
        }

        # Should handle invalid scheme gracefully
        with pytest.raises((ValidationError, ValueError, KeyError)):
            evaluate_single_scheme(invalid_scheme, indicator_config, fuzzy_config, expert_judgments)

    def test_evaluation_pipeline_data_integrity(self, sample_configurations, indicator_config, fuzzy_config, expert_judgments):
        """Test data integrity throughout evaluation pipeline."""
        scheme = sample_configurations['baseline_scheme']

        result = evaluate_single_scheme(
            scheme, indicator_config, fuzzy_config, expert_judgments
        )

        # Check numerical precision and consistency
        indicator_values = result['indicator_values']
        normalized_values = result['normalized_values']
        weighted_values = result['weighted_values']

        # All arrays should have same length
        assert len(indicator_values) == len(normalized_values) == len(weighted_values)

        # Normalized values should be non-negative
        assert all(val >= 0 for val in normalized_values), "Normalized values should be non-negative"

        # Weighted values should be non-negative
        assert all(val >= 0 for val in weighted_values), "Weighted values should be non-negative"

        # Check that transformations preserve data relationships
        audit_trail = result['audit_trail']
        for transformation in audit_trail['transformations']:
            assert 'stage' in transformation
            assert 'timestamp' in transformation
            assert 'input_data' in transformation
            assert 'output_data' in transformation

    def test_evaluation_pipeline_reproducibility(self, sample_configurations, indicator_config, fuzzy_config, expert_judgments):
        """Test evaluation pipeline produces reproducible results."""
        scheme = sample_configurations['baseline_scheme']

        # Evaluate same scheme twice
        result1 = evaluate_single_scheme(scheme, indicator_config, fuzzy_config, expert_judgments)
        result2 = evaluate_single_scheme(scheme, indicator_config, fuzzy_config, expert_judgments)

        # Results should be identical
        assert result1['ci_score'] == result2['ci_score'], "Ci scores should be reproducible"
        assert result1['rank'] == result2['rank'], "Ranks should be reproducible"

        # Audit trails should have same structure
        assert result1['audit_trail']['transformation_count'] == result2['audit_trail']['transformation_count']

    def test_evaluation_pipeline_performance_benchmark(self, sample_configurations, indicator_config, fuzzy_config, expert_judgments):
        """Test evaluation pipeline performance benchmarks."""
        schemes = [
            sample_configurations['baseline_scheme'],
            sample_configurations['high_capability_scheme'],
            sample_configurations['minimal_scheme']
        ]

        # Performance test for batch evaluation
        start_time = time.time()
        batch_result = evaluate_batch(schemes, indicator_config, fuzzy_config, expert_judgments)
        end_time = time.time()

        batch_execution_time = end_time - start_time
        avg_time_per_scheme = batch_execution_time / len(schemes)

        # Performance validation
        assert avg_time_per_scheme < 0.5, f"Average time per scheme: {avg_time_per_scheme:.3f}s, should be <0.5s"
        assert batch_execution_time < 2.0, f"Batch evaluation took {batch_execution_time:.3f}s, should be <2.0s"

        # Memory usage check (basic)
        result_size = len(str(batch_result))
        assert result_size > 1000, "Result should contain substantial data"
        assert result_size < 1000000, "Result should not be excessively large"

    def test_evaluation_pipeline_validation_success(self, sample_configurations, indicator_config, fuzzy_config, expert_judgments):
        """Test validation success in evaluation pipeline."""
        scheme = sample_configurations['baseline_scheme']

        result = evaluate_single_scheme(
            scheme, indicator_config, fuzzy_config, expert_judgments
        )

        # Check validation metadata
        if 'evaluation_metadata' in result:
            metadata = result['evaluation_metadata']
            assert 'validation_passed' in metadata

            # In successful evaluation, validation should pass
            if metadata['validation_passed']:
                # Check that no critical validation errors occurred
                audit_trail = result['audit_trail']
                for transformation in audit_trail['transformations']:
                    if 'metadata' in transformation and 'validation' in transformation['metadata']:
                        validation = transformation['metadata']['validation']
                        if 'errors' in validation:
                            assert len(validation['errors']) == 0, f"Validation errors in {transformation['stage']} stage"

    def test_evaluation_pipeline_comprehensive_workflow(self, sample_configurations, indicator_config, fuzzy_config, expert_judgments):
        """Test comprehensive evaluation workflow with multiple validation points."""
        schemes = [
            sample_configurations['baseline_scheme'],
            sample_configurations['high_capability_scheme']
        ]

        # Step 1: Individual evaluations
        individual_results = []
        for scheme in schemes:
            result = evaluate_single_scheme(scheme, indicator_config, fuzzy_config, expert_judgments)
            individual_results.append(result)

            # Validate each result
            assert 'ci_score' in result
            assert 'rank' in result
            assert 'audit_trail' in result

        # Step 2: Batch evaluation
        batch_result = evaluate_batch(schemes, indicator_config, fuzzy_config, expert_judgments)

        # Step 3: Cross-validate results
        for scheme_result in individual_results:
            scheme_id = scheme_result['scheme_id']
            assert scheme_id in batch_result['individual_results']
            batch_individual = batch_result['individual_results'][scheme_id]

            # Results should match between individual and batch evaluation
            assert scheme_result['ci_score'] == batch_individual['ci_score']
            assert scheme_result['rank'] == batch_individual['rank']

        # Step 4: Validate overall consistency
        best_scheme = batch_result['best_scheme']
        assert best_scheme['scheme_id'] in [scheme['scheme_id'] for scheme in schemes]
        assert best_scheme['rank'] == 1

    def test_evaluation_pipeline_edge_cases(self, indicator_config, fuzzy_config, expert_judgments):
        """Test evaluation pipeline with edge cases."""
        # Test with minimal valid configuration
        minimal_scheme = {
            'scheme_id': 'minimal_test',
            'scheme_name': 'Minimal Test Configuration',
            'platform_inventory': {
                'USV_Unmanned_Surface_Vessel': {'count': 1, 'types': {}}
            },
            'deployment_plan': {
                'primary_sector': {'coordinates': [50.0, 45.0], 'radius_km': 50}
            },
            'task_assignments': {},
            'operational_constraints': {
                'total_platforms': 1,
                'max_budget_million_usd': 2.5,
                'deployment_area_km2': 1000,
                'endurance_hours': 24,
                'communication_range_km': 50
            }
        }

        # Should handle minimal configuration
        result = evaluate_single_scheme(minimal_scheme, indicator_config, fuzzy_config, expert_judgments)

        # Should still produce valid result structure
        assert 'ci_score' in result
        assert 0.0 <= result['ci_score'] <= 1.0
        assert 'audit_trail' in result


if __name__ == '__main__':
    # Run tests if executed directly
    pytest.main([__file__, '-v'])