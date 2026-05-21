#!/usr/bin/env python3
"""
Run the full test suite for yDrinks code.
Usage: from the 'code' directory, run:  python run_tests.py
Or:  python -m unittest discover -s tests -p "test_*.py" -v
"""

import sys
import unittest

if __name__ == "__main__":
    # Ensure we can import from parent (xlsx_reader, ydrinks_file_merge)
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests")
    suite = loader.discover(start_dir, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
