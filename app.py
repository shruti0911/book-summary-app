import sys
import os

# Add the current directory to the Python path so we can import app module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the app from the app directory
from app.app import *

# This ensures all content from app/app.py is executed
