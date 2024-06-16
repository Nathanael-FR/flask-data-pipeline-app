# Add parent directory to PYTHONPATH to avoid ImportError

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))