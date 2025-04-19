# streamlit_app.py

import streamlit as st
import time
import os
import sys
from typing import List

# Add project root to path and import modules
try:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    from agent import run_search_session
    from web_tools import perform_web_search
    from config import DDG_MAX_RESULTS, MAX_SEARCH_ATTEMPTS
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()
except FileNotFoundError:
    st.error("Error: Required project files missing")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="WebMind",
    page_icon="🔎",
    layout="wide"
)

# Initialize session state
for key, default_value in {
    'search_running': False,
    'status_messages': [],
    'final_result': "",
    'tried_urls_summary': []
}.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

def add_status_message(message: str) -> None:
    """Add timestamped status message to session state"""
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.status_messages.append(f"[{timestamp}] {message}")

# UI Layout
st.title("🔎 Advanced AI Search Tool")
st.caption(f"Enter your query. The AI will search up to {DDG_MAX_RESULTS} web results (max {MAX_SEARCH_ATTEMPTS} attempts).")

query = st.text_input(
    "Enter your search query:", 
    key="query_input", 
    disabled=st.session_state.search_running
)

search_button = st.button(
    "Search", 
    key="search_button", 
    disabled=st.session_state.search_running or not query
)

# Placeholders for dynamic content
status_placeholder = st.empty()
result_placeholder = st.empty()

# Search execution logic
if search_button and query:
    # Reset state
    st.session_state.search_running = True
    st.session_state.status_messages = []
    st.session_state.final_result = ""
    st.session_state.tried_urls_summary = []
    result_placeholder.empty()
    
    add_status_message("Starting search...")
    status_placeholder.info("\n".join(st.session_state.status_messages))
    
    try:
        # Get initial URLs
        add_status_message(f"Searching for top {DDG_MAX_RESULTS} results...")
        status_placeholder.info("\n".join(st.session_state.status_messages))
        
        search_urls = perform_web_search(query, num_results=DDG_MAX_RESULTS)
        
        if not search_urls:
            add_status_message("❌ Web search returned no results.")
            st.session_state.final_result = "Could not find any relevant web pages for the query."
        else:
            add_status_message(f"Found {len(search_urls)} potential URLs. Starting analysis...")
            status_placeholder.info("\n".join(st.session_state.status_messages))
            
            # Run main search process
            final_answer, tried_urls = run_search_session(
                query=query,
                urls=search_urls,
                max_attempts=MAX_SEARCH_ATTEMPTS,
                status_callback=add_status_message,
                status_placeholder=status_placeholder
            )
            
            # Store results
            st.session_state.final_result = final_answer
            st.session_state.tried_urls_summary = tried_urls
            add_status_message("✅ Search finished.")
            
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        add_status_message(f"❌ Search error: {e}")
        st.session_state.final_result = "An error occurred. Please try again."
    
    finally:
        st.session_state.search_running = False

# Display UI updates
if st.session_state.search_running:
    with st.spinner("Processing..."):
        status_placeholder.info("\n".join(st.session_state.status_messages))

# Display results when search complete
if not st.session_state.search_running and st.session_state.final_result:
    status_placeholder.info("\n".join(st.session_state.status_messages))
    result_placeholder.markdown("--- \n**Result:**")
    result_placeholder.markdown(st.session_state.final_result)
    
    # Show attempted URLs on failure
    if ("Could not find a sufficient answer" in st.session_state.final_result and 
            st.session_state.tried_urls_summary):
        with st.expander("URLs Attempted"):
            for url in st.session_state.tried_urls_summary:
                st.write(url)

# Footer
st.markdown("---")
st.caption("Powered by Ollama and Streamlit.")














#--------------------------------------------------------------------------------------------------------------
# # streamlit_app.py

# import streamlit as st
# import time # For simulating delays if needed, remove later
# import os
# import sys

# # --- Configuration and Module Imports ---

# # Add project root to sys.path to allow importing modules
# # Adjust the path depth ('..') based on where this file is relative to the project root
# try:
#     project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#     if project_root not in sys.path:
#         sys.path.insert(0, project_root)

#     # Import necessary functions/classes from other modules
#     from agent import run_search_session # Handles the core search loop
#     from web_tools import perform_web_search # Gets initial URLs from DDG
#     from config import DDG_MAX_RESULTS, MAX_SEARCH_ATTEMPTS # Configuration variables

# except ImportError as e:
#     st.error(f"Error importing modules: {e}. Make sure agent.py, web_tools.py, and config.py are in the correct location and the Python path is set up if necessary.")
#     st.stop() # Stop execution if core modules can't be imported
# except FileNotFoundError:
#     st.error("Error: One of the required project files (agent.py, web_tools.py, config.py) might be missing.")
#     st.stop()

# # --- Streamlit Page Configuration ---
# st.set_page_config(
#     page_title="AI Search Tool",
#     page_icon="🔎",
#     layout="wide"
# )

# # --- Session State Initialization ---
# # Persists variables across reruns within the same user session

# if 'search_running' not in st.session_state:
#     st.session_state.search_running = False # Flag to indicate if a search is active
# if 'status_messages' not in st.session_state:
#     st.session_state.status_messages = [] # List to show progress updates
# if 'final_result' not in st.session_state:
#     st.session_state.final_result = "" # Stores the final answer or failure message
# if 'tried_urls_summary' not in st.session_state:
#     st.session_state.tried_urls_summary = [] # Stores URLs tried in case of failure

# # --- Helper Function for Status Updates ---
# def add_status_message(message):
#     """Appends a message to the status list in session state."""
#     timestamp = time.strftime("%H:%M:%S")
#     st.session_state.status_messages.append(f"[{timestamp}] {message}")
#     # Force a rerun to update the display - use cautiously
#     # st.experimental_rerun() # May cause issues if overused

# # --- Streamlit UI Layout ---

# st.title("🔎 Advanced AI Search Tool")
# st.caption(f"Enter your query. The AI will search up to {DDG_MAX_RESULTS} web results sequentially (max {MAX_SEARCH_ATTEMPTS} attempts) to find an answer.")

# query = st.text_input("Enter your search query:", key="query_input", disabled=st.session_state.search_running)

# search_button = st.button("Search", key="search_button", disabled=st.session_state.search_running or not query)

# # Placeholders for dynamic content
# status_placeholder = st.empty()
# result_placeholder = st.empty()

# # --- Search Execution Logic ---

# if search_button and query:
#     # 1. Reset state for a new search
#     st.session_state.search_running = True
#     st.session_state.status_messages = []
#     st.session_state.final_result = ""
#     st.session_state.tried_urls_summary = []
#     result_placeholder.empty() # Clear previous results
#     add_status_message("Starting search...")
#     status_placeholder.info("\n".join(st.session_state.status_messages)) # Initial status update

#     try:
#         # 2. Perform initial web search to get URLs
#         add_status_message(f"Performing web search for top {DDG_MAX_RESULTS} results...")
#         status_placeholder.info("\n".join(st.session_state.status_messages)) # Update status
#         search_urls = perform_web_search(query, num_results=DDG_MAX_RESULTS)

#         if not search_urls:
#             add_status_message("❌ Web search failed or returned no results.")
#             st.session_state.final_result = "Could not find any relevant web pages for the query."
#             st.session_state.search_running = False
#         else:
#             add_status_message(f"Found {len(search_urls)} potential URLs. Starting analysis...")
#             status_placeholder.info("\n".join(st.session_state.status_messages)) # Update status

#             # 3. Run the main agent search session
#             # This function should handle the loop, scraping, LLM calls, and update session state
#             # We pass the status update function and placeholders if needed, or rely on session state updates
#             final_answer, tried_urls = run_search_session(
#                 query=query,
#                 urls=search_urls,
#                 max_attempts=MAX_SEARCH_ATTEMPTS,
#                 status_callback=add_status_message, # Pass the callback
#                 status_placeholder=status_placeholder # Pass the placeholder to update directly
#             )

#             # 4. Process the results from the agent
#             st.session_state.final_result = final_answer
#             st.session_state.tried_urls_summary = tried_urls # Store tried URLs for potential display
#             st.session_state.search_running = False
#             add_status_message("✅ Search finished.")

#     except Exception as e:
#         st.error(f"An unexpected error occurred during the search: {e}")
#         add_status_message(f"❌ An critical error stopped the search: {e}")
#         st.session_state.final_result = "An error occurred. Please try again."
#         st.session_state.search_running = False # Ensure the flag is reset on error

# # --- Display Final Results and Status ---

# # Continuously update status messages if search is running
# if st.session_state.search_running:
#     # Use a spinner while the main process runs
#     with st.spinner("Processing..."):
#         # The status_placeholder should be updated by the callback function in run_search_session
#         # We might need a small sleep here if updates are too rapid or handled differently
#         time.sleep(0.1) # Small delay to allow UI updates
#         # Update the placeholder one last time before potentially exiting the spinner block
#         status_placeholder.info("\n".join(st.session_state.status_messages))


# # Display final result or failure message when search is not running
# if not st.session_state.search_running and st.session_state.final_result:
#     status_placeholder.info("\n".join(st.session_state.status_messages)) # Show final status list
#     result_placeholder.markdown("--- \n**Result:**")
#     result_placeholder.markdown(st.session_state.final_result) # Display the final answer/message

#     # Optionally display tried URLs if the search failed in a specific way
#     # (This depends on the exact failure message format from agent.py)
#     if "Could not find a sufficient answer after trying" in st.session_state.final_result and st.session_state.tried_urls_summary:
#          with st.expander("URLs Attempted"):
#               for url in st.session_state.tried_urls_summary:
#                    st.write(url)

# # --- Footer or additional info ---
# st.markdown("---")
# st.caption("Powered by Ollama and Streamlit.")