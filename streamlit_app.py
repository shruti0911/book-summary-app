import os
import sys
import streamlit.web.bootstrap as bootstrap

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set the file to run
filename = os.path.join(os.path.dirname(__file__), "app", "app.py")

# Run the app
bootstrap.run(filename, "", [], {}) 