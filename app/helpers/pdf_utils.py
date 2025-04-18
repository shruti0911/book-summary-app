import os
import io
import streamlit as st
import sys

# Try multiple ways to import PyMuPDF
PYMUPDF_AVAILABLE = False
try:
    # Attempt standard import
    import fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    try:
        # Try alternate import from PyMuPDF package
        from PyMuPDF import fitz
        PYMUPDF_AVAILABLE = True
    except ImportError:
        pass  # Will handle the error in the extraction function

# Try to import PyPDF2 as a fallback
PYPDF2_AVAILABLE = False
try:
    from PyPDF2 import PdfReader
    PYPDF2_AVAILABLE = True
except ImportError:
    pass  # Will handle the error in the extraction function

# Import tokenizer for chunking
import tiktoken

def extract_text_from_pdf(uploaded_file):
    """Extract text from a PDF file uploaded through Streamlit."""
    try:
        # Read the file as bytes
        pdf_bytes = uploaded_file.getvalue()
        text = ""
        
        # Try PyMuPDF first (faster and better quality)
        if PYMUPDF_AVAILABLE:
            try:
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text += page.get_text()
                doc.close()
                return text
            except Exception as e:
                st.warning(f"PyMuPDF failed: {str(e)}. Trying PyPDF2...")
        
        # Fall back to PyPDF2
        if PYPDF2_AVAILABLE:
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n\n"
            return text
        
        # If no libraries are available, show an error
        if not PYMUPDF_AVAILABLE and not PYPDF2_AVAILABLE:
            st.error("Neither PyMuPDF nor PyPDF2 is available. Please install one of them.")
        
        raise Exception("No PDF extraction library available")
        
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def chunk_text(text, max_tokens=1000, overlap=100, aggressive_chunking=False):
    """
    Split text into chunks of specified token size with overlap.
    
    Args:
        text: The text to chunk
        max_tokens: Maximum number of tokens per chunk
        overlap: Number of overlapping tokens between chunks
        aggressive_chunking: If True, use much larger chunks for very large documents
    """
    try:
        # For very large documents, use more aggressive chunking to reduce API costs
        if aggressive_chunking:
            # Calculate text size in characters as a rough proxy for tokens
            text_size = len(text)
            
            # Adjust chunk size based on text size to keep total chunks manageable
            if text_size > 500000:  # Very large book (>500K chars)
                max_tokens = 8000  # Much larger chunks
                overlap = 200       # Smaller relative overlap
            elif text_size > 200000:  # Large book (>200K chars)
                max_tokens = 4000    # Larger chunks
                overlap = 150        # Moderate overlap
            
            st.info(f"Using optimized chunking for large document: {max_tokens} tokens per chunk")
        
        # Initialize tokenizer for GPT-4o-mini for more accurate token counting
        tokenizer = tiktoken.encoding_for_model("gpt-4o-mini")
        tokens = tokenizer.encode(text)
        
        chunks = []
        start = 0
        
        # Handle empty text case
        if not tokens:
            return ["No text content found in document."]
            
        while start < len(tokens):
            end = min(start + max_tokens, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
            
            # Move start position for next chunk, with overlap
            start += max_tokens - overlap
            
        # If we still have too many chunks, combine some adjacent ones
        max_chunks = 100  # Target maximum number of chunks
        if aggressive_chunking and len(chunks) > max_chunks:
            st.warning(f"Document produced {len(chunks)} chunks, combining to reduce API costs...")
            combined_chunks = []
            
            # Combine adjacent chunks to reduce the total number
            combine_factor = len(chunks) // max_chunks + 1
            for i in range(0, len(chunks), combine_factor):
                combined_chunk = " ".join(chunks[i:i+combine_factor])
                combined_chunks.append(combined_chunk)
            
            chunks = combined_chunks
            st.info(f"Reduced to {len(chunks)} chunks")
        
        return chunks
    except Exception as e:
        raise Exception(f"Error chunking text: {str(e)}")
