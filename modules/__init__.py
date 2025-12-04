"""
AHP-FCE-TOPSIS-GA Evaluation System

Core modules for multi-criteria decision analysis of combat system configurations.
"""

__version__ = "1.0.0"
__author__ = "Military Systems Analysis Team"

from .ahp_module import calculate_weights, validate_judgment_matrix
from .fce_module import fuzzy_evaluate, validate_membership_degrees
from .topsis_module import topsis_rank, identify_ideal_solutions
from .evaluator import evaluate_single_scheme, evaluate_batch

__all__ = [
    'calculate_weights',
    'validate_judgment_matrix',
    'fuzzy_evaluate',
    'validate_membership_degrees',
    'topsis_rank',
    'identify_ideal_solutions',
    'evaluate_single_scheme',
    'evaluate_batch',
]