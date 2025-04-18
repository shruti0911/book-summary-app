import os
from openai import OpenAI
import streamlit as st

# Prompt for extracting workbook exercises from book summaries
WORKBOOK_PROMPT = """
Create a practical workbook based on this non-fiction book summary. Focus on extracting and developing:

1. Actionable exercises explicitly mentioned in the book
2. Practical implementation strategies for the book's key concepts
3. Reflection questions that help readers apply the ideas to their daily lives
4. Habit-building activities based on the book's principles
5. Self-assessment tools to track progress with the book's teachings

Format the workbook in a clear, structured way with:
- Exercise name/title
- Purpose of the exercise
- Step-by-step instructions
- Time required (if applicable)
- Materials needed (if applicable)
- Expected outcomes

Make these exercises highly practical and specific, not vague or theoretical. The reader should be able to start implementing them immediately.

# Book Summary:
{summary}
"""

def generate_workbook(summary):
    """
    Generate a practical workbook with exercises based on the book summary.
    
    Args:
        summary: The book summary text
    
    Returns:
        A formatted workbook with practical exercises
    """
    try:
        # Check for API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("⚠️ OpenAI API key is missing. Please enter your API key in the sidebar.")
            return "Please enter your OpenAI API key in the sidebar first."
            
        # Initialize the client
        client = OpenAI(api_key=api_key)
        
        # Use GPT-4 for better quality workbooks
        model = "gpt-4"
        
        with st.spinner("Creating workbook exercises..."):
            # Make the API call
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates practical workbooks from non-fiction books, focusing on extracting actionable exercises that readers can implement in their daily lives."},
                    {"role": "user", "content": WORKBOOK_PROMPT.format(summary=summary)}
                ],
                temperature=0.7
            )
            
            # Extract the response content
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
        
        # Check for model-specific errors
        elif "model_not_found" in error_message or "does not exist" in error_message:
            # Fall back to standard GPT-4 if specific version isn't available
            st.warning("Specified GPT-4 version not available. Falling back to standard GPT-4...")
            
            try:
                # Try again with standard GPT-4
                fallback_response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that creates practical workbooks from non-fiction books, focusing on extracting actionable exercises that readers can implement in their daily lives."},
                        {"role": "user", "content": WORKBOOK_PROMPT.format(summary=summary)}
                    ],
                    temperature=0.7
                )
                return fallback_response.choices[0].message.content
            except Exception as fallback_error:
                st.error(f"⚠️ Error creating workbook with fallback model: {str(fallback_error)}")
                return "Failed to generate workbook exercises. Please check your API key and internet connection."
        
        else:
            st.error(f"⚠️ Error connecting to OpenAI: {error_message}")
            return "Failed to generate workbook exercises. Please check your API key and internet connection." 