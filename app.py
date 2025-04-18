import os
import sys
import streamlit.web.bootstrap as bootstrap

# Run the app in the app directory
filename = os.path.join(os.path.dirname(__file__), "app", "app.py")
bootstrap.run(filename, "", [], {}) 