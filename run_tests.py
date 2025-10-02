#!/usr/bin/env python3
"""
Test runner script for the workflow execution system.
Run this script to execute all tests.
"""

import unittest
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import test modules
from tests.test_run_workflow import TestWorkflowExecutor, TestRunWorkflowFunction, TestWorkflowExecutionIntegration

def run_tests():
    """Run all tests and display results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowExecutor))
    suite.addTests(loader.loadTestsFromTestCase(TestRunWorkflowFunction))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowExecutionIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)
