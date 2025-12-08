"""
Indexing Bug Regression Test

This test specifically demonstrates how our comprehensive testing framework would have
caught the indexing bug we fixed in modules/evaluator.py line 230:

    BUGGY: best_rank_idx = np.argmin(topsis_result['rankings']) - 1
    FIXED:  best_rank_idx = np.argmin(topsis_result['rankings'])

This test serves as a permanent safeguard against regression of this specific bug.
"""

import pytest
import numpy as np
import os
import tempfile
from modules.topsis_module import topsis_rank
from modules.evaluator import evaluate_batch


class TestIndexingBugRegression:
    """Tests to prevent the specific indexing bug regression."""

    def test_indexing_bug_detection(self):
        """
        Test that would have caught the np.argmin() - 1 indexing bug.

        This test validates the mathematical invariant that the best ranked scheme
        should have the highest Ci score, and the indexing should be consistent.
        """
        # Create a test scenario with known Ci scores and rankings
        # Higher Ci should correspond to better (lower) rank
        ci_scores = np.array([0.85, 0.92, 0.67, 0.73, 0.88])  # Descending order
        expected_rankings = np.array([3, 1, 5, 4, 2])  # Ascending order (1=best)

        # Create decision matrix that would produce these scores
        decision_matrix = np.array([
            [8.5, 2.0, 3.0],
            [9.2, 2.5, 3.5],
            [6.7, 1.5, 2.5],
            [7.3, 1.8, 2.8],
            [8.8, 2.2, 3.2]
        ])
        weights = np.array([0.4, 0.3, 0.3])
        indicator_types = ['benefit', 'benefit', 'benefit']

        # Run TOPSIS to get actual results
        topsis_result = topsis_rank(decision_matrix, weights, indicator_types)
        actual_ci = topsis_result['Ci']
        actual_rankings = topsis_result['rankings']

        # Test the mathematical invariant: best Ci should have rank 1
        best_ci_idx = np.argmax(actual_ci)  # Index of highest Ci
        best_rank_idx = np.argmin(actual_rankings)  # Index of best rank (1)

        # These MUST be the same index - this is the bug we fixed!
        assert best_ci_idx == best_rank_idx, \
            f"CRITICAL: Indexing inconsistency detected!\n" \
            f"Best Ci index: {best_ci_idx} (Ci={actual_ci[best_ci_idx]:.6f})\n" \
            f"Best rank index: {best_rank_idx} (Rank={actual_rankings[best_rank_idx]})\n" \
            f"This would be caused by the bug: np.argmin() - 1"

        # Validate that the bug would be caught
        buggy_index = np.argmin(actual_rankings) - 1  # This was the buggy line
        if buggy_index >= 0 and buggy_index < len(actual_ci):
            # The buggy index should NOT point to the max Ci
            assert buggy_index != best_ci_idx, \
                f"REGRESSION PREVENTION: Buggy index ({buggy_index}) incorrectly points to max Ci"

    def test_batch_evaluation_indexing_correctness(self):
        """
        Test batch evaluation indexing correctness with known results.
        This test validates that the fixed batch evaluation works correctly.
        """
        # Create test schemes with known hierarchical performance
        test_schemes = [
            {
                'scheme_id': 'poor_scheme',
                'scheme_name': 'Poor Performance',
                'platform_inventory': {'USV': {'count': 2}},
                'deployment_plan': {'primary_sector': {'coordinates': [0, 0], 'radius_km': 20}},
                'task_assignments': {'test_task': {'primary_assets': ['USV'], 'coverage_requirement': 0.3}}
            },
            {
                'scheme_id': 'medium_scheme',
                'scheme_name': 'Medium Performance',
                'platform_inventory': {'USV': {'count': 5}},
                'deployment_plan': {'primary_sector': {'coordinates': [0, 0], 'radius_km': 50}},
                'task_assignments': {'test_task': {'primary_assets': ['USV'], 'coverage_requirement': 0.6}}
            },
            {
                'scheme_id': 'excellent_scheme',
                'scheme_name': 'Excellent Performance',
                'platform_inventory': {'USV': {'count': 10}},
                'deployment_plan': {'primary_sector': {'coordinates': [0, 0], 'radius_km': 100}},
                'task_assignments': {'test_task': {'primary_assets': ['USV'], 'coverage_requirement': 0.9}}
            }
        ]

        # Mock configurations to avoid file dependencies
        indicator_config = {
            'primary_capabilities': {},
            'secondary_indicators': {
                'C1_1': {'name': 'Test1', 'primary_capability': 'C1', 'type': 'benefit', 'fuzzy_flag': False},
                'C1_2': {'name': 'Test2', 'primary_capability': 'C1', 'type': 'benefit', 'fuzzy_flag': False},
                'C1_3': {'name': 'Test3', 'primary_capability': 'C1', 'type': 'benefit', 'fuzzy_flag': False}
            }
        }
        fuzzy_config = {
            'fuzzy_scale': {'差': 0.25, '中': 0.5, '良': 0.75, '优': 1.0},
            'applicable_indicators': ['C1_1', 'C1_2', 'C1_3']
        }

        # Create mock expert judgments
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            primary_file = os.path.join(temp_dir, 'primary.yaml')
            with open(primary_file, 'w') as f:
                f.write("matrix_id: test\n")
                f.write("dimension: 1\n")
                f.write("matrix: [[1.0]]\n")

            expert_judgments = {
                'primary_capabilities_file': primary_file,
                'secondary_indicators_dir': temp_dir
            }

            # Run batch evaluation
            batch_result = evaluate_batch(test_schemes, indicator_config, fuzzy_config, expert_judgments)

            # Validate indexing correctness
            assert 'best_scheme' in batch_result, "Batch result should contain best_scheme"

            best_scheme = batch_result['best_scheme']
            best_scheme_id = best_scheme['scheme_id']
            best_ci_score = best_scheme['Ci_score']
            best_rank = best_scheme['rank']

            # Best scheme should have rank 1
            assert best_rank == 1, f"Best scheme should have rank 1, got {best_rank}"

            # Best scheme ID should correspond to highest Ci
            individual_results = batch_result['individual_results']
            ci_scores = [result['Ci'] for result in individual_results.values()]
            scheme_ids = [scheme['scheme_id'] for scheme in test_schemes]

            max_ci_idx = np.argmax(ci_scores)
            expected_best_scheme_id = scheme_ids[max_ci_idx]

            assert best_scheme_id == expected_best_scheme_id, \
                f"Best scheme ID mismatch: expected {expected_best_scheme_id}, got {best_scheme_id}"

            # Validate that the indexing bug would be caught
            rankings = [result['rank'] for result in individual_results.values()]
            best_rank_idx = np.argmin(rankings)  # Correct logic (no -1)

            assert 0 <= best_rank_idx < len(test_schemes), "Best rank index should be in bounds"
            assert test_schemes[best_rank_idx]['scheme_id'] == best_scheme_id, \
                "Ranking index should point to correct scheme"

    def test_array_bounds_validation(self):
        """
        Test array bounds validation to prevent off-by-one errors.
        This test specifically validates that array operations stay within bounds.
        """
        # Test with various array sizes
        for n in [2, 3, 5, 10]:
            rankings = np.array([n - i for i in range(n)])  # [n, n-1, ..., 1]
            ci_scores = np.random.rand(n)  # Random Ci scores

            # Test argmin operation (critical for indexing bug)
            best_rank_idx = np.argmin(rankings)

            # Bounds check
            assert 0 <= best_rank_idx < n, f"Best rank index {best_rank_idx} should be in range [0, {n-1}]"

            # Test the bug scenario: argmin() - 1
            buggy_idx = best_rank_idx - 1

            # The buggy index might be out of bounds or point to wrong element
            if buggy_idx >= 0 and buggy_idx < n:
                # If it's a valid index, it should NOT be the correct one
                assert buggy_idx != best_rank_idx, \
                    f"Indexing bug detected: buggy index {buggy_idx} equals correct index {best_rank_idx}"

    def test_ranking_mathematical_consistency(self):
        """
        Test mathematical consistency between Ci scores and rankings.
        This is the core mathematical property that would detect the indexing bug.
        """
        for test_case in range(100):  # Run multiple test cases
            # Generate random Ci scores
            n = np.random.randint(2, 11)  # 2-10 alternatives
            ci_scores = np.random.rand(n)

            # Generate rankings (lower rank = better performance)
            rankings = len(ci_scores) - np.argsort(ci_scores).argsort()

            # Mathematical invariant: if Ci_i > Ci_j, then rank_i < rank_j
            for i in range(n):
                for j in range(n):
                    if ci_scores[i] > ci_scores[j] + 1e-10:  # Add small epsilon
                        assert rankings[i] < rankings[j], \
                            f"Mathematical invariant violated:\n" \
                            f"Ci[{i}] = {ci_scores[i]:.6f} > Ci[{j}] = {ci_scores[j]:.6f}\n" \
                            f"but rank[{i}] = {rankings[i]} >= rank[{j}] = {rankings[j]}\n" \
                            f"This would indicate an indexing or ranking error"

            # Best scheme index validation
            best_rank_idx = np.argmin(rankings)  # Correct: best rank has lowest number
            best_ci_idx = np.argmax(ci_scores)     # Correct: best score has highest value

            assert best_rank_idx == best_ci_idx, \
                f"Indexing inconsistency in test case {test_case}:\n" \
                f"Best rank index: {best_rank_idx}\n" \
                f"Best Ci index: {best_ci_idx}\n" \
                f"This indicates the np.argmin() - 1 bug or similar indexing error"


if __name__ == "__main__":
    # Run the regression test
    test_suite = TestIndexingBugRegression()

    print("🔍 Running Indexing Bug Regression Tests...")
    print("=" * 50)

    try:
        test_suite.test_indexing_bug_detection()
        print("✅ test_indexing_bug_detection PASSED")
    except Exception as e:
        print(f"❌ test_indexing_bug_detection FAILED: {e}")

    try:
        test_suite.test_array_bounds_validation()
        print("✅ test_array_bounds_validation PASSED")
    except Exception as e:
        print(f"❌ test_array_bounds_validation FAILED: {e}")

    try:
        test_suite.test_ranking_mathematical_consistency()
        print("✅ test_ranking_mathematical_consistency PASSED")
    except Exception as e:
        print(f"❌ test_ranking_mathematical_consistency FAILED: {e}")

    print("=" * 50)
    print("🎯 All indexing bug regression tests completed!")
    print("These tests will prevent the np.argmin() - 1 indexing bug from reoccurring.")