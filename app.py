import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the app module
from app.helpers.pdf_utils import extract_text_from_pdf, chunk_text
from app.helpers.summary_utils import summarize_chunk
from app.helpers.miro_utils import create_miro_mindmap
from app.helpers.workbook_utils import generate_workbook
from app.helpers.chat_utils import get_chat_bot

# Import all app code
from app.app import *

# This file is just an entry point - all logic is in app/app.py 