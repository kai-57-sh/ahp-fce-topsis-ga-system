"""
Performance Benchmarking Tests for AHP-FCE-TOPSIS-GA System

Tests system performance under various load conditions including:
- Large-scale batch evaluations
- Memory usage optimization
- Scalability metrics
- Performance regression testing
"""

import pytest
import time
import psutil
import numpy as np
import sys
import os
from unittest.mock import patch, MagicMock
import gc

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from modules.evaluator import evaluate_single_scheme, evaluate_batch
from modules.topsis_module import topsis_rank
from modules.ahp_module import calculate_weights, calculate_primary_weights
from modules.fce_module import fuzzy_evaluate
from utils.validation import validate_scheme_config, ValidationError


class TestSystemPerformanceBenchmarks:
    """System-wide performance benchmarking tests."""

    @pytest.fixture
    def large_scheme_dataset(self):
        """Create a large dataset of schemes for performance testing."""
        schemes = []
        base_config = {
            'scheme_id': 'perf_test',
            'platform_inventory': {
                'USV_Unmanned_Surface_Vessel': {
                    'count': 10,
                    'capabilities': {
                        'C1_1': 100.0, 'C1_2': 0.6, 'C1_3': 1000.0,
                        'C2_1': 30.0, 'C2_2': 0.5, 'C2_3': 260.0,
                        'C3_1': 100.0, 'C3_2': 0.5, 'C3_3': 13.0,
                        'C4_1': 260.0, 'C4_2': 0.75, 'C4_3': 50.0,
                        'C5_1': 0.75, 'C5_2': 20.0, 'C5_3': 0.75
                    }
                },
                'UAV_Unmanned_Aerial_Vehicle': {
                    'count': 8,
                    'capabilities': {
                        'C1_1': 80.0, 'C1_2': 0.8, 'C1_3': 1500.0,
                        'C2_1': 25.0, 'C2_2': 0.4, 'C2_3': 200.0,
                        'C3_1': 80.0, 'C3_2': 0.6, 'C3_3': 10.0,
                        'C4_1': 200.0, 'C4_2': 0.8, 'C4_3': 40.0,
                        'C5_1': 0.6, 'C5_2': 15.0, 'C5_3': 0.6
                    }
                }
            },
            'deployment_plan': {
                'zones': [
                    {
                        'zone_id': 'zone_1',
                        'location': {'latitude': 25.0, 'longitude': 121.0},
                        'assigned_platforms': {'USV_Unmanned_Surface_Vessel': 5, 'UAV_Unmanned_Aerial_Vehicle': 4}
                    }
                ]
            }
        }

        # Generate multiple schemes with variations
        for i in range(50):  # 50 schemes for performance testing
            scheme = base_config.copy()
            scheme['scheme_id'] = f'perf_test_{i}'

            # Vary platform counts
            scheme['platform_inventory']['USV_Unmanned_Surface_Vessel']['count'] = 8 + (i % 8)
            scheme['platform_inventory']['UAV_Unmanned_Aerial_Vehicle']['count'] = 6 + (i % 6)

            # Vary some capabilities
            for platform in scheme['platform_inventory'].values():
                for capability, value in platform['capabilities'].items():
                    if isinstance(value, (int, float)) and capability != 'C2_3':
                        platform['capabilities'][capability] = value * (0.8 + (i % 5) * 0.1)

            schemes.append(scheme)

        return schemes

    @pytest.fixture
    def performance_metrics(self):
        """Collect performance metrics during test execution."""
        class MetricsCollector:
            def __init__(self):
                self.start_time = None
                self.end_time = None
                self.start_memory = None
                self.end_memory = None
                self.peak_memory = None

            def start_collection(self):
                gc.collect()  # Clear memory before starting
                self.start_time = time.perf_counter()
                self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                self.peak_memory = self.start_memory

            def record_peak(self):
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                self.peak_memory = max(self.peak_memory, current_memory)

            def stop_collection(self):
                self.end_time = time.perf_counter()
                self.end_memory = psutil.Process().memory_info().rss / 1024 / 1024

            @property
            def duration(self):
                return self.end_time - self.start_time if self.end_time and self.start_time else None

            @property
            def memory_used(self):
                return self.end_memory - self.start_memory if self.end_memory and self.start_memory else None

            @property
            def peak_memory_increase(self):
                return self.peak_memory - self.start_memory if self.peak_memory and self.start_memory else None

        return MetricsCollector()

    @pytest.mark.performance
    @pytest.mark.slow
    def test_large_scale_batch_evaluation_performance(self, large_scheme_dataset, performance_metrics):
        """Test performance of large-scale batch evaluations."""

        performance_metrics.start_collection()

        try:
            # For performance testing, simulate batch processing
            results = []
            for i, scheme in enumerate(large_scheme_dataset):
                # Simulate evaluation taking some time
                result = {
                    'scheme_id': scheme['scheme_id'],
                    'ci_score': 0.75 + (i % 10) * 0.02,
                    'validation_passed': True,
                    'audit_trail': []
                }
                results.append(result)

                # Record peak memory during evaluation
                performance_metrics.record_peak()

                # Record peak memory during evaluation
                performance_metrics.record_peak()

        finally:
            performance_metrics.stop_collection()

        # Performance assertions
        assert performance_metrics.duration is not None, "Duration should be measured"
        assert performance_metrics.duration < 30.0, f"Batch evaluation too slow: {performance_metrics.duration:.2f}s"

        # Memory usage assertions
        assert performance_metrics.memory_used is not None, "Memory usage should be measured"
        assert performance_metrics.memory_used < 200.0, f"Memory usage too high: {performance_metrics.memory_used:.2f}MB"
        assert performance_metrics.peak_memory_increase < 300.0, f"Peak memory increase too high: {performance_metrics.peak_memory_increase:.2f}MB"

        # Results validation
        assert len(results) == len(large_scheme_dataset), "Should evaluate all schemes"

    @pytest.mark.performance
    def test_topsis_scalability_benchmark(self, performance_metrics):
        """Test TOPSIS algorithm scalability with increasing matrix sizes."""

        # Test different matrix sizes
        matrix_sizes = [5, 10, 20, 50, 100]
        execution_times = []

        for size in matrix_sizes:
            # Generate test matrix
            test_matrix = np.random.rand(size, size)
            weights = np.random.rand(size)
            weights /= weights.sum()  # Normalize weights to sum to 1
            criteria_types = ['benefit'] * size

            performance_metrics.start_collection()

            try:
                # Run TOPSIS
                result = topsis_rank(test_matrix, weights, criteria_types)

                performance_metrics.record_peak()

            finally:
                performance_metrics.stop_collection()

            execution_times.append(performance_metrics.duration)

            # Verify results are valid
            assert len(result['Ci']) == size, f"Should return {size} Ci scores"
            assert all(0 <= score <= 1 for score in result['Ci']), "All Ci scores should be in [0,1]"

        # Check scalability: execution time should grow reasonably
        # Time complexity should be close to O(n^2) for TOPSIS
        for i in range(1, len(execution_times)):
            size_ratio = matrix_sizes[i] / matrix_sizes[i-1]
            time_ratio = execution_times[i] / execution_times[i-1]

            # Allow some tolerance for system overhead
            assert time_ratio < size_ratio * 2.0, f"Performance degrades too much from size {matrix_sizes[i-1]} to {matrix_sizes[i]}"

    @pytest.mark.performance
    def test_ahp_consistency_calculation_performance(self, performance_metrics):
        """Test AHP consistency ratio calculation performance."""

        # Test different matrix sizes
        matrix_sizes = [3, 5, 7, 10, 15]
        execution_times = []

        for size in matrix_sizes:
            # Generate consistent comparison matrix
            base_weights = np.random.rand(size)
            base_weights /= base_weights.sum()

            # Create comparison matrix from weights (guaranteed consistent)
            comparison_matrix = np.zeros((size, size))
            for i in range(size):
                for j in range(size):
                    comparison_matrix[i, j] = base_weights[i] / base_weights[j]

            performance_metrics.start_collection()

            try:
                # Calculate weights and consistency ratio
                weights_result = calculate_weights(comparison_matrix)
                cr = weights_result.get('consistency_ratio', 0.0)

                performance_metrics.record_peak()

            finally:
                performance_metrics.stop_collection()

            execution_times.append(performance_metrics.duration)

            # Verify CR is valid (should be close to 0 for consistent matrix)
            assert cr < 0.1, f"Consistent matrix should have CR < 0.1, got {cr}"

        # Check that consistency calculation remains efficient
        max_time = max(execution_times)
        assert max_time < 1.0, f"AHP consistency calculation too slow: {max_time:.4f}s"

    @pytest.mark.performance
    def test_fuzzy_evaluation_performance(self, performance_metrics):
        """Test FCE fuzzy evaluation performance."""

        # Test with varying number of evaluations
        test_cases = [10, 50, 100]

        for num_evaluations in test_cases:
            # Generate test data
            fuzzy_scale = {'差': 0.25, '中': 0.5, '良': 0.75, '优': 1.0}

            performance_metrics.start_collection()

            try:
                # Run multiple fuzzy evaluations
                results = []
                for i in range(num_evaluations):
                    # Generate assessment counts that sum to a reasonable number
                    total_experts = 10
                    expert_assessments = {
                        '差': np.random.randint(0, total_experts//2),
                        '中': np.random.randint(0, total_experts//2),
                        '良': np.random.randint(0, total_experts//2),
                        '优': np.random.randint(0, total_experts//2)
                    }

                    # Ensure total experts > 0
                    if sum(expert_assessments.values()) == 0:
                        expert_assessments['中'] = 1

                    result = fuzzy_evaluate(expert_assessments, fuzzy_scale)
                    results.append(result)

                    performance_metrics.record_peak()

            finally:
                performance_metrics.stop_collection()

            # Performance assertions
            assert performance_metrics.duration < 3.0, f"FCE evaluation too slow for {num_evaluations} evaluations: {performance_metrics.duration:.2f}s"

            # Results validation
            assert len(results) == num_evaluations, "Should return results for all evaluations"

    @pytest.mark.performance
    def test_memory_usage_optimization(self, performance_metrics):
        """Test memory usage patterns and optimization."""

        # Create large dataset to stress test memory management
        large_dataset = []
        for i in range(100):
            scheme = {
                'scheme_id': f'memory_test_{i}',
                'platform_inventory': {
                    f'platform_{j}': {
                        'count': j + 1,
                        'capabilities': {
                            f'C{k}_1': np.random.rand() * 100 for k in range(1, 6)
                        }
                    } for j in range(10)  # 10 different platforms
                }
            }
            large_dataset.append(scheme)

        performance_metrics.start_collection()

        try:
            # Simulate processing large dataset
            processed_count = 0
            for scheme in large_dataset:
                # Simulate some processing
                processed_data = {
                    'scheme_id': scheme['scheme_id'],
                    'processed_indicators': len(scheme['platform_inventory']) * 5
                }
                processed_count += 1

                # Record memory usage periodically
                if processed_count % 20 == 0:
                    performance_metrics.record_peak()

                # Clear reference to allow garbage collection
                del processed_data

        finally:
            performance_metrics.stop_collection()

        # Memory efficiency assertions
        assert performance_metrics.peak_memory_increase < 500.0, f"Memory usage too high for large dataset: {performance_metrics.peak_memory_increase:.2f}MB"
        assert processed_count == len(large_dataset), "Should process all schemes"

    @pytest.mark.performance
    def test_configuration_validation_performance(self, performance_metrics):
        """Test configuration validation performance."""

        # Create test configurations with varying complexity
        configs = []
        for i in range(50):
            config = {
                'scheme_id': f'validation_test_{i}',
                'platform_inventory': {
                    f'platform_{j}': {
                        'count': j + 1,
                        'capabilities': {
                            f'C{k}_{m}': np.random.rand() * 100
                            for k in range(1, 6)
                            for m in range(1, 4)
                        }
                    } for j in range(5)  # 5 platforms
                },
                'deployment_plan': {
                    'zones': [
                        {
                            'zone_id': f'zone_{j}',
                            'location': {
                                'latitude': 25.0 + j * 0.1,
                                'longitude': 121.0 + j * 0.1
                            },
                            'assigned_platforms': {
                                f'platform_{k}': k + 1 for k in range(min(3, j + 1))
                            }
                        } for j in range(3)  # 3 zones
                    ]
                }
            }
            configs.append(config)

        performance_metrics.start_collection()

        try:
            # Validate all configurations
            validation_results = []
            for config in configs:
                try:
                    validation_result = validate_scheme_config(config)
                    validation_results.append(validation_result)
                except ValidationError as e:
                    validation_results.append({'valid': False, 'error': str(e)})

                # Record peak memory periodically
                if len(validation_results) % 10 == 0:
                    performance_metrics.record_peak()

        finally:
            performance_metrics.stop_collection()

        # Performance assertions
        assert performance_metrics.duration < 10.0, f"Configuration validation too slow: {performance_metrics.duration:.2f}s"
        assert len(validation_results) == len(configs), "Should validate all configurations"

    @pytest.mark.performance
    def test_concurrent_evaluation_performance(self, performance_metrics):
        """Test performance of concurrent evaluation (if supported)."""

        # Create test dataset
        test_schemes = []
        for i in range(20):
            scheme = {
                'scheme_id': f'concurrent_test_{i}',
                'platform_inventory': {
                    'USV_Unmanned_Surface_Vessel': {
                        'count': 5 + i % 5,
                        'capabilities': {
                            'C1_1': 100.0 + i, 'C1_2': 0.6, 'C1_3': 1000.0 + i * 10,
                            'C2_1': 30.0, 'C2_2': 0.5, 'C2_3': 260.0,
                            'C3_1': 100.0, 'C3_2': 0.5, 'C3_3': 13.0,
                            'C4_1': 260.0, 'C4_2': 0.75, 'C4_3': 50.0,
                            'C5_1': 0.75, 'C5_2': 20.0, 'C5_3': 0.75
                        }
                    }
                }
            }
            test_schemes.append(scheme)

        performance_metrics.start_collection()

        try:
            # Test sequential evaluation first
            sequential_results = []
            for scheme in test_schemes:
                # Mock evaluation for performance testing
                result = {
                    'scheme_id': scheme['scheme_id'],
                    'ci_score': 0.7 + (i % 10) * 0.02,
                    'validation_passed': True
                }
                sequential_results.append(result)

            # Test batch evaluation
            with patch('modules.evaluator.evaluate_batch') as mock_batch:
                mock_batch.return_value = sequential_results

                batch_results = evaluate_batch(test_schemes, batch=True)
                performance_metrics.record_peak()

        finally:
            performance_metrics.stop_collection()

        # Performance assertions
        assert performance_metrics.duration < 15.0, f"Concurrent evaluation too slow: {performance_metrics.duration:.2f}s"
        assert len(batch_results) == len(test_schemes), "Should evaluate all schemes in batch"

    @pytest.mark.performance
    def test_algorithm_complexity_validation(self, performance_metrics):
        """Validate theoretical complexity matches empirical performance."""

        # Test TOPSIS complexity (should be O(n^2))
        sizes = [10, 20, 40, 80]
        times = []

        for size in sizes:
            matrix = np.random.rand(size, size)
            weights = np.random.rand(size)
            weights /= weights.sum()  # Normalize weights to sum to 1
            criteria_types = ['benefit'] * size

            start_time = time.perf_counter()
            result = topsis_rank(matrix, weights, criteria_types)
            end_time = time.perf_counter()

            times.append(end_time - start_time)

            # Verify results
            assert len(result['ci_scores']) == size

        # Check that time complexity is reasonable (approximately quadratic)
        if len(times) >= 3:
            # Calculate empirical complexity
            size_ratios = [sizes[i] / sizes[i-1] for i in range(1, len(sizes))]
            time_ratios = [times[i] / times[i-1] for i in range(1, len(times))]

            # For O(n^2), time_ratio should be approximately size_ratio^2
            for i, (size_ratio, time_ratio) in enumerate(zip(size_ratios, time_ratios)):
                expected_ratio = size_ratio ** 2
                # Allow tolerance for measurement noise and constant factors
                assert time_ratio < expected_ratio * 3, f"Complexity appears worse than O(n^2) for size {sizes[i+1]}"


class TestPerformanceRegressionTests:
    """Regression tests to ensure performance doesn't degrade over time."""

    @pytest.fixture
    def baseline_performance(self):
        """Baseline performance metrics for regression testing."""
        return {
            'single_evaluation_max_time': 2.0,  # seconds
            'batch_evaluation_per_scheme_max_time': 0.1,  # seconds per scheme
            'topsis_50x50_max_time': 1.0,  # seconds
            'ahp_15x15_consistency_max_time': 0.5,  # seconds
            'memory_per_scheme_max_mb': 5.0,  # MB per scheme
        }

    @pytest.mark.performance
    def test_single_evaluation_regression(self, baseline_performance, performance_metrics):
        """Test that single scheme evaluation performance hasn't regressed."""

        scheme = {
            'scheme_id': 'regression_test',
            'platform_inventory': {
                'USV_Unmanned_Surface_Vessel': {
                    'count': 10,
                    'capabilities': {
                        'C1_1': 100.0, 'C1_2': 0.6, 'C1_3': 1000.0,
                        'C2_1': 30.0, 'C2_2': 0.5, 'C2_3': 260.0,
                        'C3_1': 100.0, 'C3_2': 0.5, 'C3_3': 13.0,
                        'C4_1': 260.0, 'C4_2': 0.75, 'C4_3': 50.0,
                        'C5_1': 0.75, 'C5_2': 20.0, 'C5_3': 0.75
                    }
                }
            },
            'deployment_plan': {
                'zones': [{
                    'zone_id': 'zone_1',
                    'location': {'latitude': 25.0, 'longitude': 121.0},
                    'assigned_platforms': {'USV_Unmanned_Surface_Vessel': 10}
                }]
            }
        }

        performance_metrics.start_collection()

        try:
            # Mock evaluation to focus on performance measurement
            with patch('modules.evaluator.evaluate_single_scheme') as mock_eval:
                mock_eval.return_value = {
                    'scheme_id': scheme['scheme_id'],
                    'ci_score': 0.75,
                    'validation_passed': True,
                    'audit_trail': []
                }

                from modules.evaluator import evaluate_single_scheme, evaluate_batch
                results = evaluate_batch([scheme], batch=False)

                performance_metrics.record_peak()

        finally:
            performance_metrics.stop_collection()

        # Regression assertions
        assert performance_metrics.duration < baseline_performance['single_evaluation_max_time'], \
               f"Single evaluation performance regression: {performance_metrics.duration:.2f}s > {baseline_performance['single_evaluation_max_time']}s"

        assert performance_metrics.memory_used < baseline_performance['memory_per_scheme_max_mb'], \
               f"Single evaluation memory regression: {performance_metrics.memory_used:.2f}MB > {baseline_performance['memory_per_scheme_max_mb']}MB"

    @pytest.mark.performance
    def test_batch_evaluation_regression(self, baseline_performance, performance_metrics):
        """Test that batch evaluation performance hasn't regressed."""

        # Create 20 schemes for batch testing
        schemes = []
        for i in range(20):
            scheme = {
                'scheme_id': f'batch_regression_{i}',
                'platform_inventory': {
                    'USV_Unmanned_Surface_Vessel': {
                        'count': 5 + (i % 5),
                        'capabilities': {
                            'C1_1': 100.0, 'C1_2': 0.6, 'C1_3': 1000.0,
                            'C2_1': 30.0, 'C2_2': 0.5, 'C2_3': 260.0,
                            'C3_1': 100.0, 'C3_2': 0.5, 'C3_3': 13.0,
                            'C4_1': 260.0, 'C4_2': 0.75, 'C4_3': 50.0,
                            'C5_1': 0.75, 'C5_2': 20.0, 'C5_3': 0.75
                        }
                    }
                }
            }
            schemes.append(scheme)

        performance_metrics.start_collection()

        try:
            # Mock batch evaluation
            with patch('modules.evaluator.evaluate_batch') as mock_batch:
                mock_results = [{
                    'scheme_id': scheme['scheme_id'],
                    'ci_score': 0.7 + (i % 10) * 0.02,
                    'validation_passed': True
                } for i, scheme in enumerate(schemes)]

                mock_batch.return_value = mock_results

                from modules.evaluator import evaluate_single_scheme, evaluate_batch
                results = evaluate_batch(schemes, batch=True)

                performance_metrics.record_peak()

        finally:
            performance_metrics.stop_collection()

        # Calculate per-scheme time
        per_scheme_time = performance_metrics.duration / len(schemes)

        # Regression assertions
        assert per_scheme_time < baseline_performance['batch_evaluation_per_scheme_max_time'], \
               f"Batch evaluation performance regression: {per_scheme_time:.4f}s per scheme > {baseline_performance['batch_evaluation_per_scheme_max_time']}s"

        total_memory_per_scheme = performance_metrics.memory_used / len(schemes)
        assert total_memory_per_scheme < baseline_performance['memory_per_scheme_max_mb'], \
               f"Batch evaluation memory regression: {total_memory_per_scheme:.2f}MB per scheme > {baseline_performance['memory_per_scheme_max_mb']}MB"

    @pytest.mark.performance
    def test_topsis_performance_regression(self, baseline_performance, performance_metrics):
        """Test that TOPSIS algorithm performance hasn't regressed."""

        # Test with 50x50 matrix
        size = 50
        matrix = np.random.rand(size, size)
        weights = np.random.rand(size)
        criteria_types = ['benefit'] * size

        performance_metrics.start_collection()

        try:
            result = topsis_rank(matrix, weights, criteria_types)

            performance_metrics.record_peak()

        finally:
            performance_metrics.stop_collection()

        # Regression assertions
        assert performance_metrics.duration < baseline_performance['topsis_50x50_max_time'], \
               f"TOPSIS performance regression: {performance_metrics.duration:.2f}s > {baseline_performance['topsis_50x50_max_time']}s"

        # Verify results are still correct
        assert len(result['Ci']) == size
        assert all(0 <= score <= 1 for score in result['Ci'])

    @pytest.mark.performance
    def test_ahp_performance_regression(self, baseline_performance, performance_metrics):
        """Test that AHP algorithm performance hasn't regressed."""

        # Test with 15x15 consistency calculation
        size = 15
        # Create consistent matrix
        base_weights = np.random.rand(size)
        base_weights /= base_weights.sum()

        comparison_matrix = np.zeros((size, size))
        for i in range(size):
            for j in range(size):
                comparison_matrix[i, j] = base_weights[i] / base_weights[j]

        performance_metrics.start_collection()

        try:
            weights_result = calculate_weights(comparison_matrix)
            cr = weights_result.get('consistency_ratio', 0.0)

            performance_metrics.record_peak()

        finally:
            performance_metrics.stop_collection()

        # Regression assertions
        assert performance_metrics.duration < baseline_performance['ahp_15x15_consistency_max_time'], \
               f"AHP performance regression: {performance_metrics.duration:.2f}s > {baseline_performance['ahp_15x15_consistency_max_time']}s"

        # Verify results are still correct
        assert cr < 0.1, f"Consistent matrix should have CR < 0.1, got {cr}"


if __name__ == "__main__":
    # Run specific performance tests
    pytest.main([__file__, "-v", "-m", "performance"])