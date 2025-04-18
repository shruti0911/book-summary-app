import os
import sys

# Add the project root to the Python path
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_dir)

# Make sure the app directory can be imported 
try:
    import app
except ImportError:
    print("Error importing the app package")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Import the app module - this will run the Streamlit app
from app.app import * 