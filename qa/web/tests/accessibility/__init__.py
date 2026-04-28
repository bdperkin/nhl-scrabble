"""Accessibility tests for WCAG 2.1 compliance.

This package contains automated accessibility tests using axe-core,
keyboard navigation tests, and specific WCAG 2.1 success criteria tests.

Test Modules:
- test_axe_scans: Automated axe-core scans for all pages
- test_keyboard_navigation: Keyboard accessibility tests
- test_wcag_compliance: Specific WCAG 2.1 criteria tests

Usage:
    pytest tests/accessibility/ -v
    pytest -m accessibility
    pytest -m keyboard
"""
