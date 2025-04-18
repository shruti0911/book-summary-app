import os
from openai import OpenAI
import streamlit as st

# Prompt for initial chunk processing - focused on extracting key information
CHUNK_PROMPT = """
Extract the key information from this section of a non-fiction book. Focus on:
1. Main concepts and ideas
2. Key arguments and supporting evidence
3. Important facts, figures, and examples
4. Actionable insights and takeaways

Be comprehensive but concise. This is an intermediate summary that will be used to create a final book summary.

# Book Content
{chunk}
"""

# Prompt for final summary - optimized for mind mapping
FINAL_PROMPT = """
Create a summary of this non-fiction book that is well-structured for mind mapping. Your summary should:

1. Identify a central theme or main concept of the book
2. Extract 5-8 major themes/branches that connect to the central concept
3. For each major theme, identify 3-5 key supporting ideas, insights, or action points
4. Include specific examples, facts, or quotes that illustrate key points (when available)

Format the summary hierarchically using clear headings and bullet points:

# [BOOK TITLE/CENTRAL CONCEPT]

## Major Theme 1
- Key point 1a
- Key point 1b
- Key point 1c

## Major Theme 2
- Key point 2a
- Key point 2b
- Key point 2c

And so on. This format will make it easy to transfer to a mind mapping tool.

# Book Content
{chunk}

Notes:
- Use concise, actionable language
- Focus on ideas rather than summaries of chapters
- Maintain the book's original insights and principles
- Create clear hierarchical relationships between concepts
"""

def summarize_chunk(chunk, is_final=True):
    """
    Summarize a chunk of text using OpenAI's API.
    
    Args:
        chunk: The text to summarize
        is_final: If True, creates a polished final summary. If False, creates an intermediate summary for further processing.
    """
    try:
        # Check for API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("⚠️ OpenAI API key is missing. Please enter your API key in the sidebar.")
            return "Please enter your OpenAI API key in the sidebar first."
            
        # Initialize the client here (not at module level)
        client = OpenAI(api_key=api_key)
        
        # Select the appropriate prompt based on whether this is a final summary or not
        prompt = FINAL_PROMPT if is_final else CHUNK_PROMPT
        
        # Always use GPT-4 for better summaries
        model = "gpt-4"
        
        # Using the new OpenAI API format
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes nonfiction books in a format ideal for creating mind maps."},
                {"role": "user", "content": prompt.format(chunk=chunk)}
            ],
            temperature=0.7 if is_final else 0.5  # Lower temperature for intermediate summaries
        )
        
        # Extract the response content using the new format
        return response.choices[0].message.content
    
    except Exception as e:
        error_message = str(e)
        
        # Check for specific API key errors
        if "invalid_api_key" in error_message or "Incorrect API key" in error_message:
            st.error("⚠️ Your OpenAI API key is invalid or incorrect. Please check and enter a valid API key.")
            return "Your OpenAI API key appears to be invalid. Please check that you've entered it correctly in the sidebar."
        
        elif "insufficient_quota" in error_message or "exceeded your current quota" in error_message:
            st.error("⚠️ Your OpenAI account has insufficient credits or has reached its quota limit.")
            return "Your OpenAI account has reached its usage limit. Please check your billing status at platform.openai.com."
        
        elif "not authorized" in error_message or "does not exist" in error_message:
            st.error("⚠️ Your API key is not authorized to use this model or functionality.")
            return "Your API key doesn't have access to the required model. Please check your OpenAI account permissions."
        
        else:
            st.error(f"⚠️ Error connecting to OpenAI: {error_message}")
            return "Failed to generate summary. Please check your API key and internet connection." 