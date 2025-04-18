import os
from openai import OpenAI
import streamlit as st

# Prompt for initial chunk processing - focused on extracting key information
CHUNK_PROMPT = """
You are an expert at summarizing non-fiction books using first principles thinking. First principles are fundamental truths or assumptions that cannot be reduced further.

Your task is to extract the key information from this section of a non-fiction book. Focus on identifying **major themes** and for each theme, summarize:

1. Core ideas and concepts
2. Key arguments or reasoning
3. Important facts, data, or examples
4. Actionable insights or takeaways

Use the format below:

# [Book Title]

## [Major Theme 1]
- [Key Point 1A]
- [Key Point 1B]
- [Key Point 1C]

## [Major Theme 2]
- [Key Point 2A]
- [Key Point 2B]
- [Key Point 2C]

Be comprehensive but concise. Do not list chapters or refer to the book's structure. Use your judgment to identify themes based on content.

# Book Content:
{chunk}

Notes:
- Think from first principles: what's the core insight behind this?
- Use clear bullet points.
- Do not write "Major Theme 1:" in your output—just use the heading for the theme name.
- Include examples or stats when mentioned, but summarize them.
- Do not make themes repetetive, make sure themes are unique and not overlapping.

Example of chunk output:
# Deep Work

## The Value of Deep Work
- Deep work enables mastery of complex tasks
- It creates more value per hour than shallow work
- Professionals who cultivate deep work thrive in a competitive economy

## Distraction is the Enemy
- Constant connectivity weakens focus
- Social media and open-plan offices increase cognitive switching costs
- Focus is a skill that must be trained

## Training the Mind
- Deep work must be scheduled deliberately
- Rituals and routines help sustain deep focus
- Mental clarity improves with practice and time-blocking
"""

# Prompt for final summary - optimized for mind mapping
FINAL_PROMPT = """
Summarize this non-fiction book in a structure that can easily be transferred to a mind map.

Focus on:
1. A **central concept** that unifies the book's message (do not make this a separate heading)
2. 5–8 major themes (branches from the central concept)
3. For each theme, include 3–5 bullet points of:
   - Core insights (from a first-principles perspective)
   - Supporting reasoning or examples
   - Actionable ideas

Use this format:

# [BOOK TITLE]

## [Major Theme 1]
- [Key Point 1A]
- [Key Point 1B]
- [Key Point 1C]

## [Major Theme 2]
- [Key Point 2A]
- [Key Point 2B]
- [Key Point 2C]

Avoid summarizing chapters. Instead, extract the **essence** of what the book teaches.

# Book Content:
{chunk}

Notes:
- Do not use "Major Theme 1" as a label—just use the actual theme name as the heading.
- Think deeply—what are the foundational truths?
- Use concise, powerful language.
- This summary is for a mind map—make connections clean and logical.
- Do not make themes repetetive, make sure themes are unique and not overlapping.

Example of output:
# Deep Work

## Focus as a Superpower
- Deep work enables learning, creativity, and output
- Most knowledge workers are stuck in shallow work
- Attention is a competitive advantage

## Dangers of Distraction
- Social media and multitasking erode cognitive ability
- Shallow habits become default in a noisy environment
- Digital minimalism supports sustained focus

## Cultivating Deep Work
- Schedule focused blocks of uninterrupted work
- Use rituals (location, time, tools) to enter deep mode
- Track deep work hours to measure progress

## Embrace Boredom
- Downtime trains the brain to resist novelty
- Boredom builds cognitive resilience
- Avoid context-switching and embrace monotony

## Make Deep Work a Lifestyle
- High performers protect time like a fortress
- Reduce shallow obligations ruthlessly
- Align deep work with life goals and identity
"""


def summarize_chunk(chunk, is_final=True):
    """
    Summarize a chunk of text using OpenAI's API.
    
    Args:
        chunk: The text to summarize
        is_final: If True, creates a polished final summary. If False, creates an intermediate summary for further processing.
    """
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("⚠️ OpenAI API key is missing. Please enter your API key in the sidebar.")
        return None
    
    # Initialize the client
    client = OpenAI(api_key=api_key)
    
    # Use GPT-4o-mini for better quality summaries
    model = "gpt-4o-mini"
    
    try:
        # Determine the appropriate prompt based on whether this is a final summary
        prompt = FINAL_PROMPT if is_final else CHUNK_PROMPT
        
        # Make the request to OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates concise and informative summaries of text while preserving the key information."},
                {"role": "user", "content": prompt.format(chunk=chunk)}
            ],
            temperature=0.5
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