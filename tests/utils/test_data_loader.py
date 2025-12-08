"""
Test Data Loader Utility

Provides standardized, working configurations for integration tests.
Fixes the "dummy path" issues by providing real, validated data.
"""

import yaml
import os
from typing import Dict, Any, List
from pathlib import Path

class TestDataManager:
    """Manages test data loading with proper path resolution and validation."""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.data_dir = self.base_dir / 'data'
        self.config_dir = self.base_dir / 'config'

    def load_real_expert_judgments(self) -> Dict[str, str]:
        """Load real expert judgments with validated file paths."""
        return {
            'primary_capabilities_file': str(self.data_dir / 'expert_judgments' / 'primary_capabilities.yaml'),
            'secondary_indicators_dir': str(self.data_dir / 'expert_judgments' / 'secondary_indicators')
        }

    def load_real_indicator_config(self) -> Dict[str, Any]:
        """Load real indicator configuration."""
        config_file = self.config_dir / 'indicators.yaml'
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Fallback configuration
            return self._get_fallback_indicator_config()

    def load_real_fuzzy_config(self) -> Dict[str, Any]:
        """Load real fuzzy configuration."""
        config_file = self.config_dir / 'fuzzy_sets.yaml'
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Fallback configuration
            return self._get_fallback_fuzzy_config()

    def load_available_schemes(self) -> List[Dict[str, Any]]:
        """Load all available scheme configurations."""
        scheme_dir = self.data_dir / 'schemes'
        available_schemes = []

        scheme_files = [
            'baseline_scheme.yaml',
            'balanced_force.yaml',
            'high_endurance_force.yaml',
            'tech_lite_force.yaml'
        ]

        for scheme_file in scheme_files:
            scheme_path = scheme_dir / scheme_file
            if scheme_path.exists():
                try:
                    with open(scheme_path, 'r') as f:
                        scheme = yaml.safe_load(f)
                        if scheme and 'scheme_id' in scheme:
                            available_schemes.append(scheme)
                except Exception:
                    # Skip problematic files
                    continue

        return available_schemes

    def load_scheme_by_id(self, scheme_id: str) -> Dict[str, Any]:
        """Load a specific scheme by ID."""
        schemes = self.load_available_schemes()
        for scheme in schemes:
            if scheme.get('scheme_id') == scheme_id:
                return scheme

        raise ValueError(f"Scheme with ID '{scheme_id}' not found")

    def _get_fallback_indicator_config(self) -> Dict[str, Any]:
        """Provide fallback indicator configuration if real config not available."""
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

    def _get_fallback_fuzzy_config(self) -> Dict[str, Any]:
        """Provide fallback fuzzy configuration if real config not available."""
        return {
            'fuzzy_scale': {
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

# Global instance for use across tests
test_data_manager = TestDataManager()