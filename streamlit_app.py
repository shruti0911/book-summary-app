import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Simply import everything from app.py (which itself imports from app/app.py)
from app import * 