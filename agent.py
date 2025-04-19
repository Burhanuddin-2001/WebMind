# agent.py
import streamlit as st
import logging
import functools
from typing import Optional, Tuple, List, Callable, Any

# --- Module Imports ---
from llm_service import query_chat_model
from web_tools import scrape_single_url
from prompts import SUFFICIENCY_CHECK_PROMPT_TEMPLATE, FAILURE_SUMMARY_PROMPT_TEMPLATE
from config import CHAT_MODEL, MAX_LLM_CONTEXT_LENGTH

# Configure logging for this module
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def parse_llm_sufficiency_response(response: str) -> Tuple[Optional[str], bool]:
    """
    Parses the LLM response to determine if the context was sufficient.

    Args:
        response: The raw text response from the LLM.

    Returns:
        A tuple containing:
        - The extracted final answer (str) if found, otherwise None.
        - A boolean indicating if the context was deemed sufficient.
    """
    response_lower = response.lower().strip()

    # Check for explicit insufficient context marker
    if response_lower == "insufficient context":
        logger.info("LLM indicated insufficient context.")
        return None, False

    # Check for the "Final Answer:" marker
    final_answer_marker = "final answer:"
    marker_pos = response_lower.find(final_answer_marker)

    if marker_pos != -1:
        # Extract text after "Final Answer:"
        final_answer_text = response[marker_pos + len(final_answer_marker):].strip()
        if final_answer_text:
            logger.info(f"Extracted Final Answer (length {len(final_answer_text)}).")
            return final_answer_text, True
        
        logger.warning("Found 'Final Answer:' marker but the subsequent text was empty.")
        return None, False
    
    # No "Final Answer:" marker and not "Insufficient context"
    logger.warning(f"LLM response did not contain expected markers. Response: '{response[:100]}...'")
    return None, False


def update_status(status_callback: Callable, status_placeholder: Any, message: str) -> None:
    """
    Updates status in both the session state and the UI placeholder.
    
    Args:
        status_callback: Function to add status message to session state.
        status_placeholder: Streamlit placeholder to update UI.
        message: Status message to display.
    """
    status_callback(message)
    status_placeholder.info("\n".join(st.session_state.status_messages))


def run_search_session(
    query: str,
    urls: List[str],
    max_attempts: int,
    status_callback: Callable,
    status_placeholder: Any
) -> Tuple[str, List[str]]:
    """
    Runs the sequential search loop: scrape -> analyze -> decide.

    Args:
        query: The original user query.
        urls: List of URLs obtained from the initial web search.
        max_attempts: Maximum number of URLs to try.
        status_callback: A function to call with status updates.
        status_placeholder: The Streamlit placeholder object for the status display.

    Returns:
        A tuple containing:
        - The final answer string (or a failure message).
        - A list of URLs that were actually attempted.
    """
    tried_urls = []
    # Create a bound function for simpler status updates
    update_ui = functools.partial(update_status, status_callback, status_placeholder)
    
    # Limit URLs to max_attempts
    urls_to_try = urls[:max_attempts]
    
    for attempt_count, url in enumerate(urls_to_try, 1):
        tried_urls.append(url)
        update_ui(f"Attempt {attempt_count}/{max_attempts}: Trying URL: {url}")

        # --- Step 1: Scrape Single URL ---
        update_ui(f"  ↳ Scraping content...")
        try:
            scraped_text = scrape_single_url(url)
            if not scraped_text or not scraped_text.strip():
                update_ui(f"  ↳ ⚠️ No valid content obtained from {url}.")
                continue
                
            update_ui(f"  ↳ ✅ Scraping successful (content length: {len(scraped_text)}).")
        except Exception as scrape_err:
            logger.error(f"Error scraping URL {url}: {scrape_err}", exc_info=True)
            update_ui(f"  ↳ ❌ Error during scraping for {url}: {scrape_err}")
            continue

        # --- Step 2: Analyze Content with LLM ---
        update_ui(f"  ↳ Analyzing content for sufficiency...")
        try:
            # Format the prompt with truncated content for LLM
            max_context_length = getattr(MAX_LLM_CONTEXT_LENGTH, CHAT_MODEL, 15000)
            prompt = SUFFICIENCY_CHECK_PROMPT_TEMPLATE.format(
                query=query,
                url=url,
                scraped_text=scraped_text[:max_context_length]
            )

            # Query the LLM and parse response
            llm_response = query_chat_model(prompt)
            final_answer, is_sufficient = parse_llm_sufficiency_response(llm_response)

            if is_sufficient and final_answer:
                update_ui(f"  ↳ ✅ Found sufficient answer from {url}.")
                # Add reference to the answer
                final_answer_with_ref = f"{final_answer}\n\n---\n*Source: {url}*"
                return final_answer_with_ref, tried_urls
                
            update_ui(f"  ↳ ℹ️ Content from {url} deemed insufficient by AI.")
        except Exception as llm_err:
            logger.error(f"Error analyzing content from {url} with LLM: {llm_err}", exc_info=True)
            update_ui(f"  ↳ ❌ Error during AI analysis for {url}: {llm_err}")

    # --- Step 3: Handle Failure (Loop finished without sufficient answer) ---
    failure_message = f"Could not find a sufficient answer after trying {len(tried_urls)} URL(s)."
    update_ui(f"🏁 {failure_message}")
    
    return failure_message, tried_urls






#-----------------------------------------------------------------------------------------------------------------------------
# # agent.py
# import streamlit as st
# import logging
# import re
# import time # Potentially for small delays if needed

# # --- Module Imports ---
# try:
#     from llm_service import query_chat_model
#     from web_tools import scrape_single_url
#     from prompts import SUFFICIENCY_CHECK_PROMPT_TEMPLATE, FAILURE_SUMMARY_PROMPT_TEMPLATE # Import templates
#     from config import CHAT_MODEL # Import necessary config
# except ImportError as e:
#     logging.error(f"Error importing modules in agent.py: {e}")
#     # This error should ideally be caught higher up (streamlit_app.py),
#     # but logging here helps debugging.
#     raise # Re-raise to indicate failure

# # Configure logging for this module
# logger = logging.getLogger(__name__)
# # Basic logging setup if not configured by a main entry point
# if not logger.handlers:
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# def parse_llm_sufficiency_response(response: str) -> tuple[str | None, bool]:
#     """
#     Parses the LLM response to the sufficiency check prompt.

#     Args:
#         response: The raw text response from the LLM.

#     Returns:
#         A tuple containing:
#         - The extracted final answer (str) if found, otherwise None.
#         - A boolean indicating if the context was deemed sufficient (True if final answer found, False otherwise).
#     """
#     response_lower = response.lower().strip()

#     # Check for explicit insufficient context marker first
#     if response_lower == "insufficient context":
#         logger.info("LLM indicated insufficient context.")
#         return None, False

#     # Check for the "Final Answer:" marker
#     final_answer_marker = "final answer:"
#     marker_pos = response_lower.find(final_answer_marker)

#     if marker_pos != -1:
#         # Extract text after "Final Answer:"
#         final_answer_text = response[marker_pos + len(final_answer_marker):].strip()
#         if final_answer_text:
#             logger.info(f"Extracted Final Answer (length {len(final_answer_text)}).")
#             return final_answer_text, True
#         else:
#             # Marker found but no text after it
#             logger.warning("Found 'Final Answer:' marker but the subsequent text was empty.")
#             # Treat as insufficient as we didn't get a usable answer
#             return None, False
#     else:
#         # No "Final Answer:" marker and not "Insufficient context"
#         # This indicates the LLM didn't follow instructions.
#         logger.warning(f"LLM response did not contain 'Final Answer:' or 'Insufficient context'. Response: '{response[:100]}...'")
#         # Treat as insufficient context as we can't be sure
#         return None, False


# def run_search_session(
#     query: str,
#     urls: list[str],
#     max_attempts: int,
#     status_callback: callable, # Function to send status updates to UI
#     status_placeholder # Streamlit placeholder to update directly
#     ) -> tuple[str, list[str]]:
#     """
#     Runs the sequential search loop: scrape -> analyze -> decide.

#     Args:
#         query: The original user query.
#         urls: List of URLs obtained from the initial web search.
#         max_attempts: Maximum number of URLs to try.
#         status_callback: A function (like add_status_message) to call with status updates.
#         status_placeholder: The Streamlit placeholder object to update the status display.

#     Returns:
#         A tuple containing:
#         - The final answer string (or a failure message).
#         - A list of URLs that were actually attempted.
#     """
#     tried_urls = []
#     attempt_count = 0

#     for url in urls:
#         if attempt_count >= max_attempts:
#             status_callback(f"🏁 Reached maximum attempts ({max_attempts}).")
#             status_placeholder.info("\n".join(st.session_state.status_messages)) # Update UI
#             break

#         attempt_count += 1
#         tried_urls.append(url)
#         status_callback(f"Attempt {attempt_count}/{max_attempts}: Trying URL: {url}")
#         status_placeholder.info("\n".join(st.session_state.status_messages)) # Update UI

#         # --- Step 1: Scrape Single URL ---
#         status_callback(f"  ↳ Scraping content...")
#         status_placeholder.info("\n".join(st.session_state.status_messages)) # Update UI
#         try:
#             scraped_text = scrape_single_url(url)
#             if scraped_text is None:
#                 status_callback(f"  ↳ ⚠️ Scraping failed or returned no content for {url}.")
#                 status_placeholder.info("\n".join(st.session_state.status_messages)) # Update UI
#                 continue # Move to the next URL
#             elif not scraped_text.strip():
#                  status_callback(f"  ↳ ⚠️ Scraped content is empty for {url}.")
#                  status_placeholder.info("\n".join(st.session_state.status_messages)) # Update UI
#                  continue # Move to the next URL
#             else:
#                  status_callback(f"  ↳ ✅ Scraping successful (content length: {len(scraped_text)}).")
#                  status_placeholder.info("\n".join(st.session_state.status_messages)) # Update UI

#         except Exception as scrape_err:
#             logger.error(f"Error scraping URL {url}: {scrape_err}", exc_info=True)
#             status_callback(f"  ↳ ❌ Error during scraping for {url}: {scrape_err}")
#             status_placeholder.info("\n".join(st.session_state.status_messages)) # Update UI
#             continue # Move to the next URL

#         # --- Step 2: Analyze Content with LLM ---
#         status_callback(f"  ↳ Analyzing content for sufficiency...")
#         status_placeholder.info("\n".join(st.session_state.status_messages)) # Update UI
#         try:
#             # Format the prompt for the LLM
#             prompt = SUFFICIENCY_CHECK_PROMPT_TEMPLATE.format(
#                 query=query,
#                 url=url,
#                 scraped_text=scraped_text[:15000] # Limit context window size for safety
#             )

#             # Query the LLM
#             llm_response = query_chat_model(prompt) # Use the configured model implicitly

#             # Parse the LLM's decision
#             final_answer, is_sufficient = parse_llm_sufficiency_response(llm_response)

#             if is_sufficient and final_answer:
#                 status_callback(f"  ↳ ✅ Found sufficient answer from {url}.")
#                 status_placeholder.info("\n".join(st.session_state.status_messages)) # Update UI
#                 # Add reference to the answer
#                 final_answer_with_ref = f"{final_answer}\n\n---\n*Source: {url}*"
#                 return final_answer_with_ref, tried_urls # Success! Return the answer.
#             else:
#                 status_callback(f"  ↳ ℹ️ Content from {url} deemed insufficient by AI.")
#                 status_placeholder.info("\n".join(st.session_state.status_messages)) # Update UI
#                 # Continue to the next URL

#         except Exception as llm_err:
#             logger.error(f"Error analyzing content from {url} with LLM: {llm_err}", exc_info=True)
#             status_callback(f"  ↳ ❌ Error during AI analysis for {url}: {llm_err}")
#             status_placeholder.info("\n".join(st.session_state.status_messages)) # Update UI
#             # Decide whether to continue or stop on LLM error? Let's continue for now.
#             continue

#     # --- Step 3: Handle Failure (Loop finished without sufficient answer) ---
#     failure_message = f"Could not find a sufficient answer after trying {attempt_count} URL(s)."
#     status_callback(f"🏁 {failure_message}")
#     status_placeholder.info("\n".join(st.session_state.status_messages)) # Update UI

#     # Optional: Ask LLM to summarize the failure (can add time)
#     # try:
#     #     urls_list_str = "\n".join([f"- {u}" for u in tried_urls])
#     #     summary_prompt = FAILURE_SUMMARY_PROMPT_TEMPLATE.format(
#     #         query=query,
#     #         tried_urls_list=urls_list_str
#     #     )
#     #     failure_summary = query_chat_model(summary_prompt)
#     #     failure_message += f"\n\nSummary of attempts:\n{failure_summary}"
#     # except Exception as summary_err:
#     #     logger.error(f"Failed to generate failure summary: {summary_err}")
#     #     # Keep the basic failure message

#     return failure_message, tried_urls