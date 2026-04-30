"""Test analytics and coverage analysis module.

This module provides tools for analyzing test analytics and coverage data from Codecov API.
"""

from nhl_scrabble.analytics.analyzer import CoverageGap, TestAnalyzer, TestPerformance
from nhl_scrabble.analytics.codecov_client import CodecovClient, CodecovConfig
from nhl_scrabble.analytics.formatters import HTMLFormatter, JSONFormatter, TextFormatter

__all__ = [
    "CodecovClient",
    "CodecovConfig",
    "CoverageGap",
    "HTMLFormatter",
    "JSONFormatter",
    "TestAnalyzer",
    "TestPerformance",
    "TextFormatter",
]
