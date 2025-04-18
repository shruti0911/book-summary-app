import os
import sys
import streamlit.web.bootstrap as bootstrap

# Add the current directory to path so relative imports work
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_dir)

# Run the app from the app directory
filename = os.path.join(root_dir, "app", "app.py")
bootstrap.run(filename, "", [], {}) 