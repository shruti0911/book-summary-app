#!/bin/bash

# Print current directory for debugging
echo "Current directory: $(pwd)"

# Install dependencies
pip install -r requirements.txt

# Set Python version if file doesn't exist
if [ ! -f "runtime.txt" ]; then
  echo "Creating runtime.txt"
  echo "python-3.9" > runtime.txt
fi

# Create an empty __init__.py file in the app directory if it doesn't exist
if [ ! -f "app/__init__.py" ]; then
  echo "Creating app/__init__.py"
  touch app/__init__.py
fi

# Setup Streamlit config
mkdir -p ~/.streamlit
if [ -f ".streamlit/config.toml" ]; then
  echo "Copying .streamlit/config.toml to ~/.streamlit/"
  cp .streamlit/config.toml ~/.streamlit/
else
  echo "Warning: .streamlit/config.toml not found"
fi

echo "Setup completed." 