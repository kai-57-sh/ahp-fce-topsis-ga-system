#!/usr/bin/env python3
"""
Debug script for evaluation pipeline
"""

import sys
import yaml
import traceback
from modules.evaluator import evaluate_single_scheme
from modules.ahp_module import calculate_primary_weights

def main():
    print("=== Debug Evaluation Pipeline ===")

    # Load configurations
    print("\n1. Loading configurations...")
    try:
        indicator_config = yaml.safe_load(open('config/indicators.yaml'))
        fuzzy_config = yaml.safe_load(open('config/fuzzy_sets.yaml'))
        scheme_data = yaml.safe_load(open('data/schemes/baseline_scheme.yaml'))
        expert_judgments = {
            'primary_capabilities_file': 'data/expert_judgments/primary_capabilities.yaml',
            'secondary_indicators_dir': 'data/expert_judgments/secondary_indicators'
        }
        print("✓ Configurations loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load configurations: {e}")
        return

    # Test AHP weights calculation
    print("\n2. Testing AHP weights calculation...")
    try:
        weights_result = calculate_primary_weights(
            expert_judgments['primary_capabilities_file'],
            expert_judgments['secondary_indicators_dir']
        )
        print(f"✓ AHP weights calculated successfully")
        print(f"  Number of global weights: {len(weights_result['global_weights'])}")
        print(f"  Sample weights: {list(weights_result['global_weights'].items())[:3]}")
    except Exception as e:
        print(f"✗ AHP weights calculation failed: {e}")
        traceback.print_exc()
        return

    # Test indicator value generation
    print("\n3. Testing indicator value generation...")
    try:
        from modules.evaluator import _generate_indicator_values
        from utils.validation import AuditLogger

        audit_logger = AuditLogger(scheme_data['scheme_id'])
        indicator_values = _generate_indicator_values(scheme_data, indicator_config, audit_logger)
        print(f"✓ Indicator values generated successfully")
        print(f"  Number of indicators: {len(indicator_values)}")
        print(f"  Sample values: {list(indicator_values.items())[:3]}")
    except Exception as e:
        print(f"✗ Indicator value generation failed: {e}")
        traceback.print_exc()
        return

    # Test fuzzy evaluation
    print("\n4. Testing fuzzy evaluation...")
    try:
        from modules.evaluator import _apply_fuzzy_evaluation
        fuzzy_results = _apply_fuzzy_evaluation(indicator_values, fuzzy_config, audit_logger)
        print(f"✓ Fuzzy evaluation completed successfully")
        print(f"  Fuzzy indicators: {list(fuzzy_results.keys())}")
    except Exception as e:
        print(f"✗ Fuzzy evaluation failed: {e}")
        traceback.print_exc()
        return

    print("\n=== All individual tests passed ===")
    print("\n5. Testing complete evaluation pipeline...")

    try:
        result = evaluate_single_scheme(scheme_data, indicator_config, fuzzy_config, expert_judgments)
        print("✓ Complete evaluation successful!")
        print(f"  Ci Score: {result['ci_score']:.4f}")
        print(f"  Rank: {result['rank']}")
        print(f"  Validation: {'PASSED' if result.get('evaluation_metadata', {}).get('validation_passed', False) else 'FAILED'}")
    except Exception as e:
        print(f"✗ Complete evaluation failed: {e}")
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()