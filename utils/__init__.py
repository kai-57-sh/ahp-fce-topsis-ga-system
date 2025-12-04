"""
Utility functions for AHP-FCE-TOPSIS-GA Evaluation System

Helper functions for consistency checking, normalization, and validation.
"""

from .consistency_check import calculate_cr
from .normalization import vector_normalize
from .validation import log_transformation, validate_evaluation_result

__all__ = [
    'calculate_cr',
    'vector_normalize',
    'log_transformation',
    'validate_evaluation_result',
]