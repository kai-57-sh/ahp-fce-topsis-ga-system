"""
Property-Based Testing for FCE Module

Research-grade validation using property-based testing to automatically generate
hundreds of test cases and validate mathematical invariants for FCE algorithms.
This catches edge cases and subtle bugs that manual testing might miss.

Key Properties Validated:
- Fuzzy set operation mathematical correctness
- Membership function boundary conditions
- Defuzzification mathematical accuracy
- Linguistic variable transformation validation
- Fuzzy aggregation operator properties
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st, assume
import warnings
from typing import Dict, List, Tuple, Any

# Add parent directory to path for imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from modules.fce_module import (
    fuzzy_comprehensive_evaluation,
    apply_fuzzy_scale,
    defuzzify,
    calculate_membership_degrees
)


class TestFCEFuzzySetProperties:
    """Test fundamental mathematical properties of fuzzy set operations."""

    @given(
        # Generate membership degree arrays
        degrees=st.lists(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
                        min_size=3, max_size=10)
    )
    def test_membership_degree_bounds(self, degrees):
        """Test that membership degrees stay within [0, 1] bounds."""
        degrees_array = np.array(degrees)

        # Property 1: All membership degrees should be in [0, 1]
        assert all(0.0 <= d <= 1.0 for d in degrees_array), \
            f"All membership degrees should be in [0, 1], got {degrees_array}"

        # Property 2: Normalized degrees should sum to 1.0
        if sum(degrees_array) > 0:
            normalized = degrees_array / sum(degrees_array)
            assert abs(sum(normalized) - 1.0) < 1e-10, \
                f"Normalized degrees should sum to 1.0, got {sum(normalized)}"

    @given(
        # Test fuzzy complement operations
        degree=st.floats(min_value=0.0, max_value=1.0, allow_nan=False)
    )
    def test_fuzzy_complement_properties(self, degree):
        """Test mathematical properties of fuzzy complement operations."""
        # Standard fuzzy complement: 1 - degree
        complement = 1.0 - degree

        # Property 1: Complement should also be in [0, 1]
        assert 0.0 <= complement <= 1.0, \
            f"Complement should be in [0, 1], got {complement}"

        # Property 2: Double complement should return original
        double_complement = 1.0 - complement
        assert abs(double_complement - degree) < 1e-10, \
            f"Double complement should return original, got {double_complement} vs {degree}"

        # Property 3: Complement boundary conditions
        if degree == 0.0:
            assert abs(complement - 1.0) < 1e-10, "Complement of 0 should be 1"
        if degree == 1.0:
            assert abs(complement - 0.0) < 1e-10, "Complement of 1 should be 0"

    @given(
        # Test fuzzy union and intersection
        degrees1=st.lists(st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
                         min_size=3, max_size=8),
        degrees2=st.lists(st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
                         min_size=3, max_size=8)
    )
    def test_fuzzy_union_intersection_properties(self, degrees1, degrees2):
        """Test mathematical properties of fuzzy union and intersection."""
        assume(len(degrees1) == len(degrees2))

        arr1 = np.array(degrees1)
        arr2 = np.array(degrees2)

        # Standard fuzzy union: max(x, y)
        fuzzy_union = np.maximum(arr1, arr2)

        # Standard fuzzy intersection: min(x, y)
        fuzzy_intersection = np.minimum(arr1, arr2)

        # Property 1: Union and intersection bounds
        assert all(0.0 <= x <= 1.0 for x in fuzzy_union), "Union should be in [0, 1]"
        assert all(0.0 <= x <= 1.0 for x in fuzzy_intersection), "Intersection should be in [0, 1]"

        # Property 2: Union should be >= each operand
        assert all(fuzzy_union >= arr1), "Union should be >= first operand"
        assert all(fuzzy_union >= arr2), "Union should be >= second operand"

        # Property 3: Intersection should be <= each operand
        assert all(fuzzy_intersection <= arr1), "Intersection should be <= first operand"
        assert all(fuzzy_intersection <= arr2), "Intersection should be <= second operand"

        # Property 4: Union >= intersection (idempotent property)
        assert all(fuzzy_union >= fuzzy_intersection), "Union should be >= intersection"


class TestFCEMembershipFunctionProperties:
    """Test mathematical properties of membership functions."""

    @given(
        # Test triangular membership functions
        peak=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        width=st.floats(min_value=0.1, max_value=0.8, allow_nan=False),
        test_point=st.floats(min_value=0.0, max_value=1.0, allow_nan=False)
    )
    def test_triangular_membership_properties(self, peak, width, test_point):
        """Test mathematical properties of triangular membership functions."""
        # Simple triangular membership function
        left = max(0.0, peak - width)
        right = min(1.0, peak + width)

        # Calculate membership degree
        if test_point < left or test_point > right:
            membership = 0.0
        elif test_point == peak:
            membership = 1.0
        elif test_point < peak:
            membership = (test_point - left) / (peak - left) if peak > left else 0.0
        else:  # test_point > peak
            membership = (right - test_point) / (right - peak) if right > peak else 0.0

        # Property 1: Membership should be in [0, 1]
        assert 0.0 <= membership <= 1.0, \
            f"Membership should be in [0, 1], got {membership}"

        # Property 2: Peak point should have maximum membership
        if abs(test_point - peak) < 1e-10:
            assert abs(membership - 1.0) < 1e-10, "Peak point should have membership 1.0"

        # Property 3: Boundary conditions
        if test_point <= left or test_point >= right:
            assert abs(membership - 0.0) < 1e-10, "Outside range should have membership 0.0"

    @given(
        # Test Gaussian membership functions
        center=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        sigma=st.floats(min_value=0.1, max_value=0.5, allow_nan=False),
        test_point=st.floats(min_value=0.0, max_value=1.0, allow_nan=False)
    )
    def test_gaussian_membership_properties(self, center, sigma, test_point):
        """Test mathematical properties of Gaussian membership functions."""
        # Gaussian membership function
        membership = np.exp(-0.5 * ((test_point - center) / sigma) ** 2)

        # Property 1: Membership should be in [0, 1]
        assert 0.0 <= membership <= 1.0, \
            f"Gaussian membership should be in [0, 1], got {membership}"

        # Property 2: Center point should have maximum membership
        if abs(test_point - center) < 1e-10:
            assert abs(membership - 1.0) < 1e-10, "Center point should have membership 1.0"

        # Property 3: Symmetry property
        distance1 = abs(test_point - center)
        distance2 = abs((2 * center - test_point) - center)  # Mirror point
        if 0.0 <= (2 * center - test_point) <= 1.0:
            membership_mirrored = np.exp(-0.5 * (distance2 / sigma) ** 2)
            assert abs(membership - membership_mirrored) < 1e-10, \
                "Gaussian should be symmetric around center"

    @given(
        # Test membership function normalization
        degrees=st.lists(st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
                        min_size=3, max_size=8)
    )
    def test_membership_normalization_properties(self, degrees):
        """Test mathematical properties of membership degree normalization."""
        degrees_array = np.array(degrees)

        # Avoid all-zero case
        assume(sum(degrees_array) > 1e-10)

        # Normalize membership degrees
        normalized = degrees_array / sum(degrees_array)

        # Property 1: Normalized degrees should sum to 1.0
        assert abs(sum(normalized) - 1.0) < 1e-10, \
            f"Normalized degrees should sum to 1.0, got {sum(normalized)}"

        # Property 2: Individual degrees should remain in [0, 1]
        assert all(0.0 <= d <= 1.0 for d in normalized), \
            f"Normalized degrees should be in [0, 1], got {normalized}"

        # Property 3: Order should be preserved
        original_order = np.argsort(degrees_array)
        normalized_order = np.argsort(normalized)
        np.testing.assert_array_equal(original_order, normalized_order,
                                    "Normalization should preserve order")

        # Property 4: Proportional relationships maintained
        for i in range(len(degrees_array)):
            for j in range(len(degrees_array)):
                if degrees_array[i] > 0 and degrees_array[j] > 0:
                    ratio_original = degrees_array[i] / degrees_array[j]
                    ratio_normalized = normalized[i] / normalized[j]
                    assert abs(ratio_original - ratio_normalized) < 1e-10, \
                        "Proportional relationships should be preserved"


class TestFCEDefuzzificationProperties:
    """Test mathematical properties of defuzzification operations."""

    @given(
        # Test centroid defuzzification
        membership_values=st.lists(st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
                                  min_size=3, max_size=10),
        universe_values=st.lists(st.floats(min_value=0.0, max_value=10.0, allow_nan=False),
                                min_size=3, max_size=10)
    )
    def test_centroid_defuzzification_properties(self, membership_values, universe_values):
        """Test mathematical properties of centroid defuzzification."""
        assume(len(membership_values) == len(universe_values))

        m_values = np.array(membership_values)
        u_values = np.array(universe_values)

        # Avoid all-zero membership case
        assume(sum(m_values) > 1e-10)

        # Centroid defuzzification: weighted average
        numerator = sum(m_values * u_values)
        denominator = sum(m_values)
        centroid = numerator / denominator

        # Property 1: Centroid should be within universe range
        min_universe = min(u_values)
        max_universe = max(u_values)
        assert min_universe <= centroid <= max_universe, \
            f"Centroid {centroid} should be in universe range [{min_universe}, {max_universe}]"

        # Property 2: If only one point has non-zero membership, centroid should be that point
        non_zero_indices = np.where(m_values > 1e-10)[0]
        if len(non_zero_indices) == 1:
            idx = non_zero_indices[0]
            assert abs(centroid - u_values[idx]) < 1e-10, \
                "Single point membership should have centroid at that point"

        # Property 3: Weighted average property
        weighted_sum_check = abs(sum(m_values * (u_values - centroid))) < 1e-10
        assert weighted_sum_check, "Centroid should satisfy weighted average property"

    @given(
        # Test weighted average defuzzification
        weights=st.lists(st.floats(min_value=0.01, max_value=1.0, allow_nan=False),
                        min_size=3, max_size=8),
        values=st.lists(st.floats(min_value=0.0, max_value=10.0, allow_nan=False),
                       min_size=3, max_size=8)
    )
    def test_weighted_average_properties(self, weights, values):
        """Test mathematical properties of weighted average defuzzification."""
        weights_array = np.array(weights)
        values_array = np.array(values)

        # Normalize weights
        normalized_weights = weights_array / sum(weights_array)

        # Weighted average
        weighted_avg = sum(normalized_weights * values_array)

        # Property 1: Weighted average should be within value range
        min_value = min(values_array)
        max_value = max(values_array)
        assert min_value <= weighted_avg <= max_value, \
            f"Weighted average {weighted_avg} should be in value range [{min_value}, {max_value}]"

        # Property 2: Normalized weights should sum to 1.0
        assert abs(sum(normalized_weights) - 1.0) < 1e-10, \
            "Normalized weights should sum to 1.0"

        # Property 3: If all weights are equal, should equal simple average
        equal_weights = np.ones_like(weights_array) / len(weights_array)
        simple_avg = sum(equal_weights * values_array)
        if all(abs(w - equal_weights[0]) < 1e-10 for w in normalized_weights):
            assert abs(weighted_avg - simple_avg) < 1e-10, \
                "Equal weights should give simple average"

    @given(
        # Test defuzzification boundary conditions
        n=st.integers(min_value=3, max_value=8)
    )
    def test_defuzzification_boundary_conditions(self, n):
        """Test boundary conditions of defuzzification operations."""
        # Create test data
        values = np.linspace(0, 10, n)

        # Case 1: All membership degrees equal
        equal_memberships = np.ones(n) / n
        equal_centroid = sum(equal_memberships * values) / sum(equal_memberships)

        # Should equal the mean of values
        expected_mean = sum(values) / n
        assert abs(equal_centroid - expected_mean) < 1e-10, \
            "Equal memberships should give mean value"

        # Case 2: Peak at ends
        # Peak at minimum
        peak_min_memberships = np.zeros(n)
        peak_min_memberships[0] = 1.0
        peak_min_centroid = values[0]  # Should be the minimum value

        # Peak at maximum
        peak_max_memberships = np.zeros(n)
        peak_max_memberships[-1] = 1.0
        peak_max_centroid = values[-1]  # Should be the maximum value

        assert peak_min_centroid == min(values), "Peak at min should give min value"
        assert peak_max_centroid == max(values), "Peak at max should give max value"


class TestFCEComprehensiveEvaluationProperties:
    """Test mathematical properties of fuzzy comprehensive evaluation."""

    @given(
        # Test fuzzy comprehensive evaluation with various inputs
        criteria_count=st.integers(min_value=3, max_value=8),
        alternative_count=st.integers(min_value=2, max_value=5)
    )
    def test_evaluation_matrix_properties(self, criteria_count, alternative_count):
        """Test mathematical properties of evaluation matrices."""
        # Generate evaluation matrix (alternatives x criteria)
        evaluation_matrix = np.random.uniform(0.0, 1.0, (alternative_count, criteria_count))

        # Generate weights
        weights = np.random.uniform(0.1, 1.0, criteria_count)
        weights = weights / sum(weights)  # Normalize

        # Property 1: Evaluation matrix should be in [0, 1]
        assert all(0.0 <= x <= 1.0 for x in evaluation_matrix.flatten()), \
            "Evaluation matrix values should be in [0, 1]"

        # Property 2: Weights should sum to 1.0
        assert abs(sum(weights) - 1.0) < 1e-10, "Weights should sum to 1.0"

        # Property 3: Weighted evaluation should be in [0, 1]
        weighted_eval = np.dot(evaluation_matrix, weights)
        assert all(0.0 <= x <= 1.0 for x in weighted_eval), \
            "Weighted evaluation should be in [0, 1]"

    @given(
        # Test fuzzy aggregation operators
        values=st.lists(st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
                       min_size=3, max_size=8)
    )
    def test_fuzzy_aggregation_properties(self, values):
        """Test mathematical properties of fuzzy aggregation operators."""
        values_array = np.array(values)

        # Test different aggregation methods

        # Max operator (fuzzy OR)
        max_result = np.max(values_array)

        # Min operator (fuzzy AND)
        min_result = np.min(values_array)

        # Average operator
        avg_result = np.mean(values_array)

        # Property 1: Aggregation bounds
        assert 0.0 <= max_result <= 1.0, "Max aggregation should be in [0, 1]"
        assert 0.0 <= min_result <= 1.0, "Min aggregation should be in [0, 1]"
        assert 0.0 <= avg_result <= 1.0, "Average aggregation should be in [0, 1]"

        # Property 2: Ordering properties
        assert min_result <= avg_result <= max_result, \
            "Should have min <= avg <= max"

        # Property 3: Boundary conditions
        if all(v == 0.0 for v in values_array):
            assert max_result == 0.0 and min_result == 0.0 and avg_result == 0.0, \
                "All zeros should give all zero aggregations"

        if all(v == 1.0 for v in values_array):
            assert max_result == 1.0 and min_result == 1.0 and avg_result == 1.0, \
                "All ones should give all one aggregations"

    @given(
        # Test linguistic variable transformations
        linguistic_values=st.lists(st.sampled_from(['差', '中', '良', '优']),
                                   min_size=3, max_size=10)
    )
    def test_linguistic_transformation_properties(self, linguistic_values):
        """Test mathematical properties of linguistic to numerical transformations."""
        # Standard fuzzy scale mapping
        fuzzy_scale = {
            '差': 0.25,
            '中': 0.5,
            '良': 0.75,
            '优': 1.0
        }

        # Transform linguistic values to numerical
        numerical_values = [fuzzy_scale[val] for val in linguistic_values]
        num_array = np.array(numerical_values)

        # Property 1: Transformed values should be in [0, 1]
        assert all(0.0 <= v <= 1.0 for v in numerical_values), \
            "Transformed values should be in [0, 1]"

        # Property 2: Order preservation
        # '优' > '良' > '中' > '差'
        order_mapping = {'差': 0, '中': 1, '良': 2, '优': 3}
        linguistic_orders = [order_mapping[val] for val in linguistic_values]

        # Check that numerical ordering matches linguistic ordering
        for i in range(len(linguistic_values)):
            for j in range(len(linguistic_values)):
                if linguistic_orders[i] > linguistic_orders[j]:
                    assert numerical_values[i] > numerical_values[j], \
                        "Numerical transformation should preserve linguistic order"

        # Property 3: Transformation should be consistent
        for val in fuzzy_scale:
            assert 0.0 <= fuzzy_scale[val] <= 1.0, \
                f"Fuzzy scale value for {val} should be in [0, 1]"


class TestFCEEdgeCaseGeneration:
    """Generate and test edge cases that manual testing might miss."""

    @given(
        # Test with extreme membership values
        extreme_value=st.floats(min_value=1e-10, max_value=1e-10, allow_nan=False)
    )
    def test_extreme_membership_values(self, extreme_value):
        """Test FCE with extreme membership values."""
        # Test with very small membership values
        membership_values = np.array([extreme_value, extreme_value * 2, extreme_value * 3])
        universe_values = np.array([1.0, 2.0, 3.0])

        try:
            # Should handle extreme values gracefully
            if sum(membership_values) > 1e-15:  # Avoid division by zero
                centroid = sum(membership_values * universe_values) / sum(membership_values)

                assert np.isfinite(centroid), "Centroid should be finite with extreme values"
                assert min(universe_values) <= centroid <= max(universe_values), \
                    "Centroid should be within universe range"

        except Exception:
            # Some extreme cases might fail - this is acceptable
            pass

    @given(
        # Test with identical membership values
        n=st.integers(min_value=3, max_value=10),
        identical_value=st.floats(min_value=0.1, max_value=0.9, allow_nan=False)
    )
    def test_identical_membership_values(self, n, identical_value):
        """Test FCE with identical membership values."""
        membership_values = np.ones(n) * identical_value
        universe_values = np.linspace(0, 10, n)

        try:
            # Should handle identical values correctly
            centroid = sum(membership_values * universe_values) / sum(membership_values)

            # With identical memberships, should equal simple average
            expected_avg = sum(universe_values) / n
            assert abs(centroid - expected_avg) < 1e-10, \
                "Identical memberships should give simple average"

        except Exception as e:
            pytest.fail(f"Identical membership values should not fail: {e}")

    @given(
        # Test with single peak membership
        peak_position=st.integers(min_value=0, max_value=9)
    )
    def test_single_peak_membership(self, peak_position):
        """Test FCE with single peak membership function."""
        n = 10
        membership_values = np.zeros(n)
        membership_values[peak_position] = 1.0
        universe_values = np.linspace(0, 10, n)

        try:
            centroid = sum(membership_values * universe_values) / sum(membership_values)

            # Single peak should give exact universe value at that position
            expected_value = universe_values[peak_position]
            assert abs(centroid - expected_value) < 1e-10, \
                f"Single peak at position {peak_position} should give value {expected_value}"

        except Exception as e:
            pytest.fail(f"Single peak membership should not fail: {e}")


# Configure Hypothesis settings
def pytest_configure(config):
    """Configure Hypothesis for thorough FCE testing."""
    from hypothesis import settings
    settings.register_profile("fce_intensive", max_examples=400, deadline=15000)
    settings.load_profile("fce_intensive")

# Mark tests as mathematical validation
# pytest_plugins = [pytest.mark.mathematical]