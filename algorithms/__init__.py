"""
Railway AI - Algorithms Package
Contains all optimization algorithms for train scheduling
"""

from .comprehensive_hybrid_optimizer import (
    ComprehensiveHybridOptimizer,
    ACOOptimizer,
    GAOptimizer,
    SimpleHeuristicOptimizer as ComprehensiveHeuristicOptimizer,
    OptimizationResult
)

__version__ = "1.0.0"
__author__ = "Team Railway AI"

__all__ = [
    'ComprehensiveHybridOptimizer',
    'ACOOptimizer',
    'GAOptimizer',
    'ComprehensiveHeuristicOptimizer',
    'OptimizationResult'
]
