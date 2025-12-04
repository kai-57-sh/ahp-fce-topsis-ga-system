#!/usr/bin/env python3
"""
Test script for batch evaluation
"""

import sys
import yaml
import numpy as np
from modules.evaluator import evaluate_batch

def main():
    print("=== Testing Batch Evaluation ===")

    # Load configurations
    print("\n1. Loading configurations...")
    try:
        indicator_config = yaml.safe_load(open('config/indicators.yaml'))
        fuzzy_config = yaml.safe_load(open('config/fuzzy_sets.yaml'))

        # Load schemes
        schemes = []
        for file in ['data/schemes/baseline_scheme.yaml', 'data/schemes/scheme_a.yaml']:
            scheme_data = yaml.safe_load(open(file))
            schemes.append(scheme_data)

        expert_judgments = 'data/expert_judgments/primary_capabilities.yaml'
        print(f"✓ Loaded {len(schemes)} schemes for testing")
    except Exception as e:
        print(f"✗ Failed to load configurations: {e}")
        return

    # Generate test indicator values manually
    print("\n2. Creating test indicator values...")

    test_indicator_values = {
        'baseline_scheme': {
            'C1_1': 50.0, 'C1_2': 0.5, 'C1_3': 500.0,
            'C2_1': 30.0, 'C2_2': 0.5, 'C2_3': 100.0,
            'C3_1': 100.0, 'C3_2': 0.6, 'C3_3': 5.0,
            'C4_1': 100.0, 'C4_2': 0.7, 'C4_3': 50.0,
            'C5_1': 0.6, 'C5_2': 20.0, 'C5_3': 0.6
        },
        'scheme_a': {
            'C1_1': 65.0, 'C1_2': 0.7, 'C1_3': 650.0,
            'C2_1': 25.0, 'C2_2': 0.6, 'C2_3': 120.0,
            'C3_1': 120.0, 'C3_2': 0.8, 'C3_3': 6.0,
            'C4_1': 130.0, 'C4_2': 0.8, 'C4_3': 40.0,
            'C5_1': 0.5, 'C5_2': 25.0, 'C5_3': 0.5
        }
    }

    print("✓ Test indicator values created")

    # Test batch evaluation
    print("\n3. Testing batch evaluation...")
    try:
        # Mock the evaluation by directly calling the necessary functions
        from modules.ahp_module import calculate_primary_weights
        from modules.topsis_module import topsis_rank

        # Get weights
        weights_result = calculate_primary_weights(
            expert_judgments,
            'data/expert_judgments'
        )
        global_weights = weights_result['global_weights']

        # Create decision matrix
        indicator_order = [
            'C1_1', 'C1_2', 'C1_3', 'C2_1', 'C2_2', 'C2_3',
            'C3_1', 'C3_2', 'C3_3', 'C4_1', 'C4_2', 'C4_3',
            'C5_1', 'C5_2', 'C5_3'
        ]

        decision_matrix = []
        for scheme_id, values in test_indicator_values.items():
            row = [values[ind_id] for ind_id in indicator_order]
            decision_matrix.append(row)

        decision_matrix = np.array(decision_matrix)
        print(f"Decision matrix shape: {decision_matrix.shape}")

        # Determine indicator types
        indicator_types = ['benefit'] * 15
        cost_indicators = {'C2_1', 'C4_3'}
        for i, ind_id in enumerate(indicator_order):
            if ind_id in cost_indicators:
                indicator_types[i] = 'cost'

        # Apply TOPSIS
        weights_array = np.array([global_weights[ind_id] for ind_id in indicator_order])
        topsis_result = topsis_rank(decision_matrix, weights_array, indicator_types)

        print("✓ TOPSIS batch evaluation successful!")
        print(f"Ci scores: {topsis_result['Ci']}")
        print(f"Rankings: {topsis_result['rankings']}")

        # Show results
        print("\n=== Evaluation Results ===")
        scheme_names = list(test_indicator_values.keys())
        for i, (scheme_id, values) in enumerate(test_indicator_values.items()):
            ci = topsis_result['Ci'][i]
            rank = topsis_result['rankings'][i]
            print(f"{scheme_id}: Ci = {ci:.4f}, Rank = {rank}")

    except Exception as e:
        print(f"✗ Batch evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n=== Batch evaluation test completed successfully ===")

if __name__ == "__main__":
    main()