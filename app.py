import os
import sys

# Add the project root to the Python path
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_dir)

# Import the app module
from app.app import * 