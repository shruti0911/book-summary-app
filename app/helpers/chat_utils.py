import os
import numpy as np
from openai import OpenAI
import streamlit as st
from typing import List, Dict, Tuple

# In-memory storage for embeddings
class SimpleVectorStore:
    def __init__(self):
        self.embeddings = []
        self.texts = []
        
    def add(self, embedding, text):
        self.embeddings.append(embedding)
        self.texts.append(text)
        
    def search(self, query_embedding, top_k=3):
        if not self.embeddings:
            return []
        
        # Convert list to numpy array for efficient computation
        embeddings_array = np.array(self.embeddings)
        query_array = np.array(query_embedding)
        
        # Compute cosine similarity
        dot_products = np.dot(embeddings_array, query_array)
        norms = np.linalg.norm(embeddings_array, axis=1) * np.linalg.norm(query_array)
        similarities = dot_products / norms
        
        # Get indices of top k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Return top k text chunks and their similarity scores
        results = [(self.texts[i], float(similarities[i])) for i in top_indices]
        return results

class BookChatBot:
    def __init__(self, api_key=None):
        if not api_key:
            api_key = st.session_state.get('openai_api_key') or os.getenv("OPENAI_API_KEY")
            if not api_key:
                st.error("OpenAI API key not found. Please enter your API key in the sidebar.")
                self.is_initialized = False
                return
                
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)
        self.vector_store = SimpleVectorStore()
        self.chunks = []
        self.is_initialized = False
        self.embedding_cache = {}  # Cache to store embeddings and avoid recomputation
        
    def initialize_from_chunks(self, chunks: List[str], max_chunks=200) -> None:
        """Process and store book chunks for retrieval with optimization for large books"""
        # Verify we have a valid API key before proceeding
        if not self.api_key:
            st.error("OpenAI API key is required to initialize the chat assistant.")
            return
        
        st.info(f"Initializing chat engine with book content ({len(chunks)} chunks)...")
        
        # Optimize for very large books by selecting representative chunks
        if len(chunks) > max_chunks:
            st.warning(f"Book is very large. Optimizing by selecting {max_chunks} representative chunks.")
            # Select chunks evenly distributed throughout the book
            step = len(chunks) // max_chunks
            optimized_chunks = [chunks[i] for i in range(0, len(chunks), step)]
            # If we still have too many, truncate
            optimized_chunks = optimized_chunks[:max_chunks]
            chunks = optimized_chunks
            
        progress_bar = st.progress(0)
        
        self.chunks = chunks
        batch_size = min(20, len(chunks))  # Process in batches of 20 or fewer
        
        # Process chunks in batches to improve efficiency
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            batch_texts = [chunk for chunk in batch]
            
            try:
                # Create embeddings for the batch (more efficient than one at a time)
                response = self.client.embeddings.create(
                    model="text-embedding-3-small",
                    input=batch_texts
                )
                
                # Store each embedding in the vector store
                for j, embedding_data in enumerate(response.data):
                    chunk_idx = i + j
                    if chunk_idx < len(chunks):
                        embedding = embedding_data.embedding
                        self.vector_store.add(embedding, chunks[chunk_idx])
                        # Cache the embedding to avoid recomputation
                        self.embedding_cache[chunks[chunk_idx][:100]] = embedding  # Use first 100 chars as key
                
            except Exception as e:
                st.error(f"Error creating embeddings for batch {i//batch_size + 1}: {str(e)}")
                # Continue with the next batch despite errors
            
            # Update progress
            progress = min(1.0, (i + batch_size) / len(chunks))
            progress_bar.progress(progress)
            
        self.is_initialized = True
        st.success(f"Chat engine ready! Processed {len(chunks)} chunks.")
        
    def create_embedding(self, text: str) -> List[float]:
        """Create an embedding vector for the given text with caching"""
        # Check cache first using first 100 chars as key (for query text)
        cache_key = text[:100] if len(text) > 100 else text
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
            
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            embedding = response.data[0].embedding
            # Cache the result
            self.embedding_cache[cache_key] = embedding
            return embedding
        except Exception as e:
            st.error(f"Error creating embedding: {str(e)}")
            # Return empty vector as fallback
            return [0.0] * 1536  # Default embedding size
        
    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """Retrieve relevant context for a query with optimized context length"""
        # Create query embedding
        query_embedding = self.create_embedding(query)
        
        # Search for relevant chunks
        results = self.vector_store.search(query_embedding, top_k=top_k)
        
        # Calculate total context length
        total_length = sum(len(text) for text, score in results)
        
        # If context is too large, reduce it by keeping higher-scoring chunks
        max_context_chars = 8000  # Reasonable limit for context
        if total_length > max_context_chars:
            # Sort by score and keep only the highest-scoring chunks
            results.sort(key=lambda x: x[1], reverse=True)
            
            # Keep adding chunks until we hit the limit
            pruned_results = []
            current_length = 0
            for text, score in results:
                if current_length + len(text) <= max_context_chars:
                    pruned_results.append((text, score))
                    current_length += len(text)
                else:
                    # If adding this chunk would exceed the limit, truncate it
                    remaining_space = max_context_chars - current_length
                    if remaining_space > 500:  # Only add if we can include a meaningful amount
                        pruned_results.append((text[:remaining_space], score))
                    break
                    
            results = pruned_results
        
        # Combine top chunks as context
        context = "\n\n---\n\n".join([text for text, score in results])
        return context
    
    def answer_question(self, query: str, chat_history: List[Dict] = None) -> str:
        """Answer a question based on the book content"""
        if not self.is_initialized:
            return "Please upload a book first so I can answer questions about it."
        
        # Get relevant context
        context = self.retrieve_context(query)
        
        # Prepare messages with chat history if provided
        messages = [
            {"role": "system", "content": 
             """You are a helpful assistant that answers questions based on the book content provided. 
             Use only the provided book excerpts to answer questions - if the answer cannot be found in the excerpts, 
             acknowledge that you don't know rather than making up information. 
             When answering, cite specific parts from the book when relevant, and use a helpful, 
             conversational tone. Your goal is to help the user deeply understand the book's content."""},
            {"role": "user", "content": 
             f"""Here are relevant excerpts from the book:
             
             {context}
             
             Based on these excerpts, please answer the following question:
             {query}"""}
        ]
        
        # Add chat history if provided
        if chat_history:
            # Insert history before the latest user question
            messages = messages[:1] + chat_history + messages[1:]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.5
            )
            answer = response.choices[0].message.content
            return answer
        except Exception as e:
            st.error(f"Error generating answer: {str(e)}")
            return "I encountered an error when trying to answer your question. Please try again."

# Helper function to create or get the chat bot from session state
def get_chat_bot():
    if 'book_chat_bot' not in st.session_state:
        # Get API key from session state or environment
        api_key = st.session_state.get('openai_api_key') or os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("OpenAI API key not found. Please enter your API key in the sidebar.")
            return None
        st.session_state.book_chat_bot = BookChatBot(api_key)
    
    return st.session_state.book_chat_bot 