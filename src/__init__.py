"""
Value-Aligned Confabulation (VAC) Research Package

This package provides tools and frameworks for evaluating Value-Aligned Confabulation
in Large Language Models, distinguishing between harmful hallucination and beneficial
confabulation that serves human values.
"""

__version__ = "0.1.0"
__author__ = "VAC Research Team"
__email__ = "research@vac-project.org"

from .evaluation.vac_evaluator import (
    ValueAlignedConfabulationEvaluator,
    VACScore,
    Domain,
    EvaluationContext
)

from .evaluation.metrics.alignment_metrics import AlignmentMetrics
from .evaluation.metrics.truthfulness_metrics import TruthfulnessMetrics
from .evaluation.metrics.utility_metrics import UtilityMetrics

__all__ = [
    "ValueAlignedConfabulationEvaluator",
    "VACScore", 
    "Domain",
    "EvaluationContext",
    "AlignmentMetrics",
    "TruthfulnessMetrics",
    "UtilityMetrics"
]
