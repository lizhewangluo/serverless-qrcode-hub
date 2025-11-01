#!/usr/bin/env python3
"""
Simple test runner that can work without all dependencies
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

def run_parser_tests():
    """Run parser tests (no external dependencies)"""
    try:
        import unittest
        from tests.test_parser import TestTaokoulingParser
        
        suite = unittest.TestLoader().loadTestsFromTestCase(TestTaokoulingParser)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    except Exception as e:
        print(f"Error running parser tests: {e}")
        return False

def run_basic_imports_test():
    """Test basic imports work"""
    try:
        from parser import TaokoulingParser, ParseResult
        print("✓ Core parser imports work")
        return True
    except Exception as e:
        print(f"✗ Core parser imports failed: {e}")
        return False

def main():
    """Run all available tests"""
    print("Running Taokouling Float Tool Tests")
    print("=" * 50)
    
    success = True
    
    # Test basic imports
    print("\n1. Testing basic imports...")
    success &= run_basic_imports_test()
    
    # Run parser tests
    print("\n2. Running parser tests...")
    success &= run_parser_tests()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All available tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())