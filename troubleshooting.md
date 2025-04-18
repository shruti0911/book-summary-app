# Troubleshooting Dependencies

If you continue to experience dependency resolution issues in your container environment, try these approaches:

## Solution 1: Install packages individually
```bash
pip install streamlit==1.32.0
pip install openai==1.74.0
pip install tiktoken==0.9.0
pip install PyMuPDF==1.25.5
pip install PyPDF2==3.0.1
pip install requests==2.32.3
pip install numpy==1.25.0
```

## Solution 2: Use pip's --no-deps flag to avoid dependency conflicts
```bash
pip install -r requirements.txt --no-deps
pip install -r requirements.txt
```

## Solution 3: Try a compatibility mode
```bash
pip install -r requirements.txt --use-deprecated=legacy-resolver
```

## Solution 4: Ensure Python version compatibility
The application has been tested with Python 3.11. If using Python 3.12 in your container, you might encounter compatibility issues with some packages.

If possible, modify your container to use Python 3.11:
```
FROM python:3.11-slim
```

## Solution 5: Update pip
```bash
pip install --upgrade pip
```

## Solution 6: Fix distutils missing in Python 3.12
The `distutils` module was removed from the standard library in Python 3.12. If you encounter a `ModuleNotFoundError: No module named 'distutils'` error, you need to install setuptools first:

```bash
# Install setuptools before any other packages
pip install setuptools>=69.0.0

# Then install the rest of your requirements
pip install -r requirements.txt
```

Alternatively, you can manually create a virtual environment with the system packages included:
```bash
python -m venv --system-site-packages venv
source venv/bin/activate
pip install -r requirements.txt
``` 