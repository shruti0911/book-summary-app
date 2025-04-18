import streamlit as st
import os

# Set page config must be the first Streamlit command called
st.set_page_config(
    page_title="Non-fiction Summarizer", 
    layout="wide",
    page_icon="📘"
)

# Hide footer "Made with Streamlit"
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        footer:after {
            content:''; 
            visibility: hidden;
        }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Import other modules after set_page_config
from .helpers.pdf_utils import extract_text_from_pdf, chunk_text
from .helpers.summary_utils import summarize_chunk
from .helpers.miro_utils import create_miro_mindmap
from .helpers.workbook_utils import generate_workbook
from .helpers.chat_utils import get_chat_bot

# Initialize session state to store generated summaries
if 'final_summary' not in st.session_state:
    st.session_state.final_summary = None
if 'text_extracted' not in st.session_state:
    st.session_state.text_extracted = False
if 'pdf_processed' not in st.session_state:
    st.session_state.pdf_processed = False
if 'miro_mindmap_url' not in st.session_state:
    st.session_state.miro_mindmap_url = None
if 'workbook_exercises' not in st.session_state:
    st.session_state.workbook_exercises = None
if 'chat_initialized' not in st.session_state:
    st.session_state.chat_initialized = False
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# Initialize session state for checkbox values if they don't exist
if 'summary_selected' not in st.session_state:
    st.session_state.summary_selected = True
if 'mindmap_selected' not in st.session_state:
    st.session_state.mindmap_selected = False
if 'workbook_selected' not in st.session_state:
    st.session_state.workbook_selected = False
if 'assistant_selected' not in st.session_state:
    st.session_state.assistant_selected = False

st.title("📘 Non-fiction Book Summarizer")
st.markdown("Upload a non-fiction book PDF and get summaries, mind maps, and workbooks!")

# API key input
with st.sidebar:
    st.header("Settings")
    
    # OpenAI API Key with better instructions
    api_key = st.text_input("Enter your OpenAI API key", type="password",
                          help="Required for generating summaries, workbooks, and chat functionality")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        st.session_state.openai_api_key = api_key  # Store in session state too
        st.success("API key set successfully!")
    else:
        st.warning("Please enter your OpenAI API key to use the summarization feature.")
    
    with st.expander("How to get an OpenAI API Key"):
        st.markdown("""
        1. Go to [OpenAI API Keys page](https://platform.openai.com/account/api-keys)
        2. Sign up or log in to your OpenAI account
        3. Click on "Create new secret key"
        4. Give your key a name (e.g., "Book Summarizer")
        5. Copy the key and paste it in the field above
        
        **Note:** OpenAI may change their process. If these instructions are outdated, visit [OpenAI's documentation](https://platform.openai.com/docs/quickstart) for the most current information.
        
        **Cost:** Using this app will consume OpenAI API credits. The app uses GPT-4o-mini for all features (summaries, workbooks, and chat). Check OpenAI's [pricing page](https://openai.com/pricing) for current rates.
        """)
    
    # Feature selection with explanations
    st.header("Choose what to generate:")
    
    # Summary option
    summary = st.checkbox("📌 Summary", value=True, 
                         help="Creates a concise summary of the book highlighting key concepts and takeaways",
                         on_change=lambda: setattr(st.session_state, 'summary_selected', not st.session_state.summary_selected))
    
    # Mind map option
    mindmap = st.checkbox("🗺️ Mind Map", 
                         help="Generates a visual mind map in Miro showing the book's main ideas and how they connect",
                         on_change=lambda: setattr(st.session_state, 'mindmap_selected', not st.session_state.mindmap_selected))
    
    # Show Miro token input only if mind map is selected
    if mindmap:
        st.subheader("Miro Integration")
        miro_token = st.text_input("Enter your Miro Access Token", type="password", 
                               help="Required to create mind maps in Miro")
        if miro_token:
            st.success("Miro token set!")
            
        with st.expander("How to get a Miro Access Token"):
            st.markdown("""
            1. Go to [Miro Developer Dashboard](https://miro.com/app/settings/user-profile/apps)
            2. Sign up or log in to your Miro account
            3. Click on "Create new app"
            4. Fill in the app details:
               - App name: "Book Summarizer"
               - Description: "Creates mind maps from book summaries"
            5. In the "Permissions" tab, enable:
               - boards:read, boards:write
               - boards:create
            6. Click "Install app and get OAuth token"
            7. Copy the access token and paste it in the field above
            
            **Note:** Miro may update their developer platform. If these instructions are outdated, visit [Miro's API documentation](https://developers.miro.com/docs) for current information.
            """)
    else:
        miro_token = None
    
    # Workbook option (renamed from Workbook/Questions)
    workbook = st.checkbox("📓 Workbook", 
                          help="Creates practical exercises and implementations based on the book's concepts",
                          on_change=lambda: setattr(st.session_state, 'workbook_selected', not st.session_state.workbook_selected))
    
    # Chat option
    assistant = st.checkbox("💬 Chat with Book", 
                           help="Lets you ask questions about the book's content in an interactive chat",
                           on_change=lambda: setattr(st.session_state, 'assistant_selected', not st.session_state.assistant_selected))

    # Feature explanations
    with st.expander("About These Features"):
        st.markdown("""
        ### Summary
        Extracts the main ideas, key concepts, and insights from the book into a concise summary. 
        The summary captures the essence of the book and its most important takeaways.
        
        ### Mind Map
        Creates a visual representation of the book's main concepts and their relationships.
        Mind maps help visualize the structure of the book's ideas and how they connect.
        
        ### Workbook
        Generates practical exercises based on the book's principles. 
        Includes actionable tasks, reflection questions, and implementation strategies to apply the book's concepts in real life.
        
        ### Chat with Book
        Allows you to have a conversation with an AI that has processed the book. 
        Ask specific questions about the content, request clarification, or explore ideas in depth.
        """)

# Create a reset button to clear cache and allow regenerating summaries
if st.session_state.pdf_processed:
    if st.button("Generate New Summary"):
        st.session_state.final_summary = None
        st.session_state.pdf_processed = False
        st.session_state.miro_mindmap_url = None
        st.session_state.workbook_exercises = None
        st.session_state.chat_initialized = False
        st.session_state.chat_messages = []
        st.experimental_rerun()

# File uploader
uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"], key="pdf_uploader")

# Reset text_extracted state when a new file is uploaded (without debug info)
if uploaded_file:
    st.session_state.text_extracted = False

if uploaded_file and api_key:
    if not st.session_state.text_extracted:
        st.success("PDF uploaded successfully!")
        
        try:
            # Extract text from PDF
            with st.spinner("Extracting text from PDF..."):
                text = extract_text_from_pdf(uploaded_file)
                if not text.strip():
                    st.error("No text could be extracted from this PDF. It may be scanned or protected.")
                    st.stop()
                st.info(f"Extracted {len(text)} characters from PDF.")
                st.session_state.text = text
                st.session_state.text_extracted = True
        
        except Exception as e:
            st.error(f"An error occurred while extracting PDF text: {str(e)}")
            st.info("Please check your PDF file and try again.")
            st.stop()
    else:
        text = st.session_state.text
    
    # Process according to selected options
    if summary and not st.session_state.final_summary:
        try:
            with st.spinner("Preparing text for processing..."):
                # Implement direct chunking instead of using the function
                # Define larger chunk size for big books
                LARGE_CHUNK_SIZE = 4000  # tokens
                OVERLAP_SIZE = 150  # tokens
                
                try:
                    import tiktoken
                    tokenizer = tiktoken.encoding_for_model("gpt-4o-mini")
                    tokens = tokenizer.encode(st.session_state.text)
                    
                    # Create chunks with large size (no debug messages)
                    chunks = []
                    start = 0
                    
                    while start < len(tokens):
                        end = min(start + LARGE_CHUNK_SIZE, len(tokens))
                        chunk_tokens = tokens[start:end]
                        chunk_text = tokenizer.decode(chunk_tokens)
                        chunks.append(chunk_text)
                        
                        # Move start position for next chunk, with overlap
                        start += LARGE_CHUNK_SIZE - OVERLAP_SIZE
                    
                    # Limit to max 100 chunks if needed (no debug messages)
                    MAX_CHUNKS = 50  # Lower for even better efficiency
                    if len(chunks) > MAX_CHUNKS:
                        combined_chunks = []
                        combine_factor = len(chunks) // MAX_CHUNKS + 1
                        
                        for i in range(0, len(chunks), combine_factor):
                            end_idx = min(i+combine_factor, len(chunks))
                            combined_text = " ".join(chunks[i:end_idx])
                            combined_chunks.append(combined_text)
                        
                        chunks = combined_chunks
                    
                except Exception as e:
                    # Fallback to original function without debug messages
                    chunks = chunk_text(st.session_state.text, max_tokens=2000, overlap=100)

            # Process the chunks to create a unified summary
            if len(chunks) > 1:  # If we have multiple chunks
                with st.spinner("Generating summary..."):
                    # Show progress bar during generation
                    progress_bar = st.progress(0)
                    
                    # First pass: Get individual chunk summaries
                    chunk_summaries = []
                    for i, chunk in enumerate(chunks):
                        summary_text = summarize_chunk(chunk, is_final=False)
                        chunk_summaries.append(summary_text)
                        # Update progress bar
                        progress = (i + 1) / (len(chunks) + 1)  # +1 for final pass
                        progress_bar.progress(progress)
                    
                    # Second pass: Generate a unified summary from the individual summaries
                    combined_summaries = "\n\n".join(chunk_summaries)
                    # Generate the final summary
                    final_summary = summarize_chunk(combined_summaries, is_final=True)
                    # Complete the progress bar
                    progress_bar.progress(1.0)
            else:
                # Direct summarization for smaller texts
                with st.spinner("Generating summary..."):
                    final_summary = summarize_chunk(text, is_final=True)
            
            # Store the final summary in session state
            st.session_state.final_summary = final_summary
            st.session_state.pdf_processed = True
        
        except Exception as e:
            st.error(f"An error occurred during summarization: {str(e)}")
            st.info("Please check your API key and try again.")
            
    # Display the summary if it exists in session state
    if summary and st.session_state.final_summary:
        st.subheader("📌 Book Summary")
        st.markdown(st.session_state.final_summary)
        
        # Option to download summary without regenerating it
        st.download_button(
            label="Download Summary (TXT)",
            data=st.session_state.final_summary,
            file_name="book_summary.txt",
            mime="text/plain",
            key="download_summary"
        )

    if mindmap:
        st.subheader("🗺️ Mind Map")
        
        # Check if we already have a mind map URL
        if st.session_state.miro_mindmap_url:
            st.success(f"Mind map created! [View your mind map in Miro]({st.session_state.miro_mindmap_url})")
            st.markdown(f"<iframe src='{st.session_state.miro_mindmap_url}' width='100%' height='500px'></iframe>", unsafe_allow_html=True)
            
            # Add button to regenerate mind map with a new board
            if miro_token and st.session_state.final_summary:
                if st.button("Create New Mind Map Board"):
                    with st.spinner("Creating new mind map in Miro..."):
                        try:
                            # Clear previous URL to force new board creation
                            st.session_state.miro_mindmap_url = None
                            
                            # Create a new mind map
                            result = create_miro_mindmap(st.session_state.final_summary, miro_token)
                            
                            if result["success"]:
                                st.session_state.miro_mindmap_url = result["board_url"]
                                st.success(f"New mind map created! [View your mind map in Miro]({result['board_url']})")
                                st.markdown(f"<iframe src='{result['board_url']}' width='100%' height='500px'></iframe>", unsafe_allow_html=True)
                                st.experimental_rerun()  # Refresh the UI
                            else:
                                st.error(f"Failed to create new mind map: {result.get('error', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"Error creating new mind map: {str(e)}")
        
        # Check for Miro token
        elif miro_token and st.session_state.final_summary:
            if st.button("Generate Mind Map in Miro"):
                with st.spinner("Creating mind map in Miro..."):
                    try:
                        result = create_miro_mindmap(st.session_state.final_summary, miro_token)
                        
                        if result["success"]:
                            st.session_state.miro_mindmap_url = result["board_url"]
                            st.success(f"Mind map created! [View your mind map in Miro]({result['board_url']})")
                            st.markdown(f"<iframe src='{result['board_url']}' width='100%' height='500px'></iframe>", unsafe_allow_html=True)
                        else:
                            st.error(f"Failed to create mind map: {result.get('error', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Error creating mind map: {str(e)}")
        
        elif not miro_token:
            st.warning("Please enter your Miro Access Token in the sidebar to create a mind map automatically.")
            
            # Provide information on getting a Miro token
            with st.expander("How to get a Miro Access Token"):
                st.markdown("""
                1. Go to [Miro Developer Dashboard](https://miro.com/app/settings/user-profile/apps)
                2. Click on "Create new app"
                3. Fill in the app details:
                   - App name: "Book Summarizer"
                   - Description: "Creates mind maps from book summaries"
                4. In the "Permissions" tab, enable:
                   - boards:read, boards:write
                   - boards:create
                5. Click "Install app and get OAuth token"
                6. Copy the access token and paste it in the sidebar
                """)
                
        elif not st.session_state.final_summary:
            st.info("Generate a summary first before creating a mind map.")

    if workbook:
        st.subheader("📓 Workbook")
        
        # Initialize workbook generation state if not exists
        if 'generating_workbook' not in st.session_state:
            st.session_state.generating_workbook = False
        
        # Check if we already have a workbook
        if st.session_state.workbook_exercises:
            st.markdown(st.session_state.workbook_exercises)
            
            # Option to download workbook
            st.download_button(
                label="Download Workbook (TXT)",
                data=st.session_state.workbook_exercises,
                file_name="book_workbook.txt",
                mime="text/plain",
                key="download_workbook"
            )
            
            # Add a regenerate button
            if st.button("Regenerate Workbook") and not st.session_state.generating_workbook:
                # Set generating flag to prevent duplicate spinners
                st.session_state.generating_workbook = True
                st.experimental_rerun()
                
        # If we're in the middle of generating, do the actual work
        elif st.session_state.generating_workbook:
            with st.spinner("Creating workbook exercises..."):
                workbook_text = generate_workbook(st.session_state.final_summary)
                st.session_state.workbook_exercises = workbook_text
                st.session_state.generating_workbook = False  # Reset the flag
                st.experimental_rerun()
        
        # Generate workbook if we have a summary but no workbook yet
        elif st.session_state.final_summary:
            if st.button("Generate Workbook") and not st.session_state.generating_workbook:
                # Set generating flag to prevent duplicate spinners
                st.session_state.generating_workbook = True
                st.experimental_rerun()
        
        else:
            st.info("Generate a summary first before creating a workbook.")

    if assistant:
        st.subheader("💬 Chat with BookGPT")
        
        # Initialize chat bot if we have PDF text but not initialized yet
        if st.session_state.text_extracted and not st.session_state.chat_initialized:
            if st.button("Initialize Chat Assistant"):
                with st.spinner("Preparing chat assistant..."):
                    # Get the chat bot instance
                    chat_bot = get_chat_bot()
                    
                    # Check if we got a valid chat bot
                    if not chat_bot:
                        st.error("Failed to initialize chat assistant. Please check your API key.")
                        st.stop()
                    
                    # Define larger chunk size for big books (without debug messages)
                    LARGE_CHUNK_SIZE = 4000  # tokens
                    OVERLAP_SIZE = 150  # tokens
                    
                    try:
                        import tiktoken
                        tokenizer = tiktoken.encoding_for_model("gpt-4o-mini")
                        tokens = tokenizer.encode(st.session_state.text)
                        
                        # Create chunks with large size
                        chunks = []
                        start = 0
                        
                        while start < len(tokens):
                            end = min(start + LARGE_CHUNK_SIZE, len(tokens))
                            chunk_tokens = tokens[start:end]
                            chunk_text = tokenizer.decode(chunk_tokens)
                            chunks.append(chunk_text)
                            
                            # Move start position for next chunk, with overlap
                            start += LARGE_CHUNK_SIZE - OVERLAP_SIZE
                        
                        # Limit to max 50 chunks if needed
                        MAX_CHUNKS = 50  # Lower for efficiency
                        if len(chunks) > MAX_CHUNKS:
                            combined_chunks = []
                            combine_factor = len(chunks) // MAX_CHUNKS + 1
                            
                            for i in range(0, len(chunks), combine_factor):
                                end_idx = min(i+combine_factor, len(chunks))
                                combined_text = " ".join(chunks[i:end_idx])
                                combined_chunks.append(combined_text)
                            
                            chunks = combined_chunks
                    
                    except Exception as e:
                        # Fallback to standard chunking
                        chunks = chunk_text(st.session_state.text, max_tokens=1000)
                    
                    # Initialize the chat bot with chunks
                    chat_bot.initialize_from_chunks(chunks)
                    
                    # Check if initialization was successful
                    if chat_bot.is_initialized:
                        # Mark as initialized
                        st.session_state.chat_initialized = True
                        
                        # Add welcome message
                        if not st.session_state.chat_messages:
                            st.session_state.chat_messages.append({
                                "role": "assistant",
                                "content": "Hello! I'm BookGPT. Ask me any questions about the book you've uploaded."
                            })
                        
                        st.experimental_rerun()
                    else:
                        st.error("Chat assistant initialization failed. Please check your API key and try again.")
        
        # Display chat interface if chat is initialized
        elif st.session_state.chat_initialized:
            # Create a clean chat container without any dividers
            chat_container = st.container()
            with chat_container:
                # Use a clean chat display without horizontal lines
                for i, message in enumerate(st.session_state.chat_messages):
                    # Create different styling based on message role
                    if message["role"] == "assistant":
                        st.markdown(f"**BookGPT:** {message['content']}")
                    else:
                        st.markdown(f"**You:** {message['content']}")
                    
                    # Add slight padding between messages
                    st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
            
            # Simplified chat input form with auto-submission
            # Initialize chat input if not exists
            if 'chat_input' not in st.session_state:
                st.session_state.chat_input = ""
                
            # Function to handle form submission
            def handle_submit():
                user_query = st.session_state.chat_input
                if user_query:
                    # Add user message to chat history
                    st.session_state.chat_messages.append({"role": "user", "content": user_query})
                    # Clear input after submission
                    st.session_state.chat_input = ""
                    # Trigger message processing
                    st.session_state.process_message = True
            
            # Simple text input with on_change callback to handle Enter
            user_query = st.text_input("Ask a question about the book:", 
                                        key="chat_input", 
                                        on_change=handle_submit)
            
            # Process message if needed
            if 'process_message' not in st.session_state:
                st.session_state.process_message = False
                
            if st.session_state.process_message and len(st.session_state.chat_messages) > 0:
                # Get the last user message
                user_message = st.session_state.chat_messages[-1]["content"]
                
                # Get the chat bot and generate response
                chat_bot = get_chat_bot()
                
                # Prepare chat history for context (exclude the latest user message)
                chat_history = st.session_state.chat_messages[:-1] if len(st.session_state.chat_messages) > 1 else None
                
                # Generate response
                with st.spinner("Searching book content..."):
                    response = chat_bot.answer_question(user_message, chat_history)
                
                # Add assistant message to chat history
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
                
                # Reset processing flag
                st.session_state.process_message = False
                
                # Refresh the UI
                st.experimental_rerun()
        
        # If no book has been uploaded yet
        elif not st.session_state.text_extracted:
            st.info("Please upload a book first to chat with the assistant.")
            
elif uploaded_file and not api_key:
    st.warning("Please enter your OpenAI API key in the sidebar to process the PDF.")
else:
    st.info("Please upload a PDF to get started.")
