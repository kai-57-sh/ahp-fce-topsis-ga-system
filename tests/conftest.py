"""
Pytest configuration and shared fixtures for the AHP-FCE-TOPSIS-GA system.

Provides common test data, mathematical validation utilities, and research-grade
testing infrastructure for comprehensive system validation.
"""

import pytest
import numpy as np
import yaml
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, List
import warnings

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.ahp_module import calculate_weights, validate_judgment_matrix
from modules.fce_module import fuzzy_evaluate
from modules.topsis_module import topsis_rank
from utils.validation import ValidationError


@pytest.fixture
def sample_ahp_matrix():
    """Sample AHP judgment matrix with known consistency ratio."""
    return np.array([
        [1.0, 2.0, 3.0],
        [0.5, 1.0, 2.0],
        [0.333, 0.5, 1.0]
    ])


@pytest.fixture
def sample_fuzzy_data():
    """Sample fuzzy evaluation data for testing."""
    return {
        'C1_2': 0.7,
        'C2_2': 0.6,
        'C3_2': 0.8,
        'C4_2': 0.5,
        'C5_1': 0.75
    }


@pytest.fixture
def sample_topsis_data():
    """Sample TOPSIS decision matrix and weights."""
    decision_matrix = np.array([
        [1.0, 2.0, 3.0, 4.0],
        [2.0, 1.5, 2.5, 3.5],
        [1.5, 2.5, 2.0, 4.5],
        [3.0, 1.0, 3.5, 2.0]
    ])
    weights = np.array([0.3, 0.2, 0.3, 0.2])
    indicator_types = ['benefit', 'cost', 'benefit', 'cost']

    return decision_matrix, weights, indicator_types


@pytest.fixture
def sample_scheme_config():
    """Sample force structure configuration for testing."""
    return {
        'scheme_id': 'test_scheme',
        'scheme_name': 'Test Configuration',
        'platform_inventory': {
            'USV_Unmanned_Surface_Vessel': {
                'count': 5,
                'types': {
                    'surveillance_usv': 2,
                    'patrol_usv': 2,
                    'mine_hunting_usv': 1
                }
            }
        },
        'deployment_plan': {
            'primary_sector': {
                'coordinates': [25.0, 121.0],
                'radius_km': 100.0
            }
        },
        'task_assignments': {
            'surveillance_operations': {
                'primary_assets': ['surveillance_usv'],
                'coverage_requirement': 0.8,
                'endurance_hours': 24
            }
        }
    }


@pytest.fixture
def expert_judgment_matrices():
    """Set of expert judgment matrices with known properties."""
    return {
        'consistent_matrix': np.array([
            [1.0, 2.0, 4.0, 3.0],
            [0.5, 1.0, 2.0, 1.5],
            [0.25, 0.5, 1.0, 0.75],
            [0.333, 0.667, 1.333, 1.0]
        ]),
        'inconsistent_matrix': np.array([
            [1.0, 5.0, 1.0, 5.0],
            [0.2, 1.0, 0.2, 1.0],
            [1.0, 5.0, 1.0, 5.0],
            [0.2, 1.0, 0.2, 1.0]
        ]),
        'identity_matrix': np.eye(4),
        'large_consistent_matrix': np.array([
            [1.0, 1.5, 2.0, 2.5, 3.0],
            [0.667, 1.0, 1.333, 1.667, 2.0],
            [0.5, 0.75, 1.0, 1.25, 1.5],
            [0.4, 0.6, 0.8, 1.0, 1.2],
            [0.333, 0.5, 0.667, 0.833, 1.0]
        ])
    }


@pytest.fixture
def precision_test_data():
    """Data for numerical precision testing."""
    return {
        'very_small_values': np.array([1e-10, 1e-9, 1e-8, 1e-7]),
        'very_large_values': np.array([1e7, 1e8, 1e9, 1e10]),
        'mixed_scale_values': np.array([1e-6, 1.0, 1e6, 1e12]),
        'near_zero_differences': np.array([1.0, 1.0000000001, 1.0000000002, 1.0000000003])
    }


@pytest.fixture
def temp_config_file():
    """Create temporary configuration files for testing."""
    def _create_temp_file(content: Dict[str, Any]) -> str:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(content, f)
            return f.name
    return _create_temp_file


@pytest.fixture
def performance_benchmark_data():
    """Data for performance benchmarking tests."""
    return {
        'small_matrix': np.random.rand(5, 10),
        'medium_matrix': np.random.rand(50, 20),
        'large_matrix': np.random.rand(500, 50),
        'very_large_matrix': np.random.rand(1000, 100)
    }


class MathematicalValidationMixin:
    """Mixin class providing mathematical validation utilities."""

    @staticmethod
    def assert_matrix_properties(matrix: np.ndarray, rtol: float = 1e-10):
        """Validate mathematical properties of matrices."""
        # Check for square matrix
        assert matrix.shape[0] == matrix.shape[1], "Matrix must be square"

        # Check for positive diagonal elements
        np.testing.assert_allclose(np.diag(matrix), 1.0, rtol=rtol,
                                   err_msg="Diagonal elements must be 1.0")

        # Check for reciprocal property
        reciprocal_matrix = 1.0 / matrix
        np.testing.assert_allclose(matrix.T, reciprocal_matrix, rtol=rtol,
                                   err_msg="Matrix must have reciprocal property")

    @staticmethod
    def assert_ahp_consistency(matrix: np.ndarray, max_cr: float = 0.1):
        """Validate AHP consistency ratio."""
        weights, cr = calculate_weights(matrix)
        assert cr < max_cr, f"Consistency ratio {cr:.6f} exceeds threshold {max_cr}"
        assert not np.isnan(cr), "Consistency ratio should not be NaN"
        assert cr >= 0, "Consistency ratio should be non-negative"

    @staticmethod
    def assert_fuzzy_properties(fuzzy_scores: Dict[str, float]):
        """Validate fuzzy evaluation properties."""
        # Check that all scores are within [0, 1]
        for key, score in fuzzy_scores.items():
            assert 0.0 <= score <= 1.0, f"Fuzzy score {key} = {score} not in [0,1]"

        # Check that scores are valid floats
        for score in fuzzy_scores.values():
            assert isinstance(score, (float, np.floating)), "Scores must be numeric"

    @staticmethod
    def assert_topsis_properties(result: Dict[str, Any]):
        """Validate TOPSIS result properties."""
        assert 'Ci' in result, "TOPSIS result must contain Ci scores"
        assert 'rankings' in result, "TOPSIS result must contain rankings"

        Ci = result['Ci']
        rankings = result['rankings']

        # Check Ci score properties
        assert len(Ci) > 0, "Ci array must not be empty"
        assert all(0.0 <= ci <= 1.0 for ci in Ci), "Ci scores must be in [0,1]"

        # Check ranking properties
        assert len(rankings) == len(Ci), "Rankings and Ci must have same length"
        assert set(rankings) == set(range(1, len(Ci) + 1)), "Rankings must be complete permutation"

        # Check that higher Ci gets better rank
        sorted_ci_indices = np.argsort(Ci)[::-1]
        expected_rankings = np.arange(1, len(Ci) + 1)
        np.testing.assert_array_equal(rankings[sorted_ci_indices], expected_rankings,
                                      err_msg="Higher Ci should get better ranking")


@pytest.fixture
def math_validator():
    """Fixture providing mathematical validation utilities."""
    return MathematicalValidationMixin()


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "mathematical: Tests focusing on mathematical precision and algorithm correctness"
    )
    config.addinivalue_line(
        "markers", "research: Research-grade validation tests for publication"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and scalability tests"
    )
    config.addinivalue_line(
        "markers", "validation: System validation and integrity tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add mathematical marker to precision and algorithm tests
        if "precision" in item.name or "mathematical" in item.name:
            item.add_marker(pytest.mark.mathematical)

        # Add research marker to publication-quality tests
        if "publication" in item.name or "research" in item.name:
            item.add_marker(pytest.mark.research)

        # Add performance marker to benchmark tests
        if "benchmark" in item.name or "performance" in item.name:
            item.add_marker(pytest.mark.performance)

        # Add validation marker to integrity tests
        if "validation" in item.name or "consistency" in item.name:
            item.add_marker(pytest.mark.validation)


@pytest.fixture
def real_expert_judgments():
    """Real expert judgments using actual data files."""
    # Use actual data files for integration testing
    return {
        'primary_capabilities_file': 'data/expert_judgments/primary_capabilities.yaml',
        'secondary_indicators_dir': 'data/expert_judgments/secondary_indicators'
    }


@pytest.fixture
def mock_expert_judgments():
    """Mock expert judgments with temporary files for isolated testing."""
    # Create temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create temporary primary matrix file
        primary_matrix = {
            'matrix_id': 'test_primary',
            'expert_id': 'test_expert',
            'comparison_scope': 'Test matrix',
            'dimension': 3,
            'matrix': [
                [1.0, 2.0, 3.0],
                [0.5, 1.0, 2.0],
                [0.333, 0.5, 1.0]
            ]
        }

        primary_file = os.path.join(temp_dir, 'primary_test.yaml')
        with open(primary_file, 'w') as f:
            yaml.dump(primary_matrix, f)

        # Create temporary secondary directory and files
        secondary_dir = os.path.join(temp_dir, 'secondary')
        os.makedirs(secondary_dir)

        # Create secondary matrices for each capability
        for cap_id in ['C1', 'C2', 'C3']:
            secondary_matrix = {
                'matrix_id': f'{cap_id.lower()}_test',
                'expert_id': 'test_expert',
                'comparison_scope': f'{cap_id} indicators',
                'dimension': 3,
                'matrix': [
                    [1.0, 1.5, 2.0],
                    [0.667, 1.0, 1.333],
                    [0.5, 0.75, 1.0]
                ]
            }

            secondary_file = os.path.join(secondary_dir, f'{cap_id.lower()}_test.yaml')
            with open(secondary_file, 'w') as f:
                yaml.dump(secondary_matrix, f)

        yield {
            'primary_capabilities_file': primary_file,
            'secondary_indicators_dir': secondary_dir,
            'temp_dir': temp_dir
        }


@pytest.fixture
def real_indicator_config():
    """Real indicator configuration from actual data files."""
    config_path = 'config/indicators.yaml'
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        # Fallback configuration if file doesn't exist
        return {
            'primary_capabilities': {
                'C1': {'name': 'Situational Awareness Capability', 'weight_placeholder': 0.25},
                'C2': {'name': 'Strike Capability', 'weight_placeholder': 0.25},
                'C3': {'name': 'Mobility Capability', 'weight_placeholder': 0.2},
                'C4': {'name': 'Survivability Capability', 'weight_placeholder': 0.15},
                'C5': {'name': 'Sustainability Capability', 'weight_placeholder': 0.15}
            },
            'secondary_indicators': {
                'C1_1': {'name': 'Detection Range', 'primary_capability': 'C1', 'type': 'benefit', 'fuzzy_flag': True},
                'C1_2': {'name': 'Coverage Area', 'primary_capability': 'C1', 'type': 'benefit', 'fuzzy_flag': True},
                'C1_3': {'name': 'Target Classification', 'primary_capability': 'C1', 'type': 'benefit', 'fuzzy_flag': True},
                'C2_1': {'name': 'Strike Range', 'primary_capability': 'C2', 'type': 'benefit', 'fuzzy_flag': False},
                'C2_2': {'name': 'Hit Probability', 'primary_capability': 'C2', 'type': 'benefit', 'fuzzy_flag': True},
                'C2_3': {'name': 'Strike Accuracy', 'primary_capability': 'C2', 'type': 'benefit', 'fuzzy_flag': True},
                'C3_1': {'name': 'Speed', 'primary_capability': 'C3', 'type': 'benefit', 'fuzzy_flag': False},
                'C3_2': {'name': 'Maneuverability', 'primary_capability': 'C3', 'type': 'benefit', 'fuzzy_flag': True},
                'C3_3': {'name': 'Endurance', 'primary_capability': 'C3', 'type': 'benefit', 'fuzzy_flag': True},
                'C4_1': {'name': 'Armor Protection', 'primary_capability': 'C4', 'type': 'benefit', 'fuzzy_flag': False},
                'C4_2': {'name': 'Stealth', 'primary_capability': 'C4', 'type': 'benefit', 'fuzzy_flag': True},
                'C4_3': {'name': 'Electronic Warfare', 'primary_capability': 'C4', 'type': 'benefit', 'fuzzy_flag': True},
                'C5_1': {'name': 'Fuel Efficiency', 'primary_capability': 'C5', 'type': 'benefit', 'fuzzy_flag': False},
                'C5_2': {'name': 'Maintenance', 'primary_capability': 'C5', 'type': 'benefit', 'fuzzy_flag': True},
                'C5_3': {'name': 'Logistics', 'primary_capability': 'C5', 'type': 'benefit', 'fuzzy_flag': True}
            }
        }


@pytest.fixture
def real_fuzzy_config():
    """Real fuzzy configuration from actual data files."""
    config_path = 'config/fuzzy_sets.yaml'
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        # Fallback configuration if file doesn't exist
        return {
            'linguistic_scale': {
                '差': {'value': 0.25, 'description': 'Poor'},
                '中': {'value': 0.50, 'description': 'Medium'},
                '良': {'value': 0.75, 'description': 'Good'},
                '优': {'value': 1.00, 'description': 'Excellent'}
            },
            'applicable_indicators': [
                'C1_1', 'C1_2', 'C1_3', 'C2_1', 'C2_2', 'C2_3',
                'C3_1', 'C3_2', 'C3_3', 'C4_1', 'C4_2', 'C4_3',
                'C5_1', 'C5_2', 'C5_3'
            ]
        }


@pytest.fixture
def working_configurations():
    """Provide working configurations for integration tests."""
    from tests.utils.test_data_loader import test_data_manager

    return {
        'expert_judgments': test_data_manager.load_real_expert_judgments(),
        'indicator_config': test_data_manager.load_real_indicator_config(),
        'fuzzy_config': test_data_manager.load_real_fuzzy_config(),
        'available_schemes': test_data_manager.load_available_schemes()
    }


@pytest.fixture
def sample_schemes():
    """Provide sample schemes for testing."""
    from tests.utils.test_data_loader import test_data_manager
    schemes = test_data_manager.load_available_schemes()

    # Return first few schemes for testing
    return {
        'baseline_scheme': next((s for s in schemes if s.get('scheme_id') == 'baseline_scheme'), None),
        'balanced_force': next((s for s in schemes if s.get('scheme_id') == 'balanced_force'), None),
        'high_endurance_force': next((s for s in schemes if s.get('scheme_id') == 'high_endurance_force'), None),
        'tech_lite_force': next((s for s in schemes if s.get('scheme_id') == 'tech_lite_force'), None)
    }


@pytest.fixture
def real_expert_judgments():
    """Real expert judgments using actual data files."""
    from tests.utils.test_data_loader import test_data_manager
    return test_data_manager.load_real_expert_judgments()


@pytest.fixture
def real_indicator_config():
    """Real indicator configuration."""
    from tests.utils.test_data_loader import test_data_manager
    return test_data_manager.load_real_indicator_config()


@pytest.fixture
def real_fuzzy_config():
    """Real fuzzy configuration."""
    from tests.utils.test_data_loader import test_data_manager
    return test_data_manager.load_real_fuzzy_config()


# Suppress specific warnings for cleaner test output
@pytest.fixture(autouse=True)
def suppress_warnings():
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=PendingDeprecationWarning)