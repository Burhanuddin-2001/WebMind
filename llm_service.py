# llm_service.py

import logging
import ollama
import time
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Import configuration
try:
    from config import CHAT_MODEL, setup_logging
    setup_logging(__name__)
except ImportError as e:
    logger.error(f"Error importing config: {e}. Using default model.")
    CHAT_MODEL = "gemma3:4b"  # Fallback model


def extract_content(response: Any) -> str:
    """
    Extract content from Ollama response, handling different response structures.
    
    Args:
        response: Ollama API response
        
    Returns:
        String content from the model
        
    Raises:
        RuntimeError: If content cannot be extracted
    """
    # Try attribute access first (object)
    if hasattr(response, 'message') and hasattr(response.message, 'content'):
        return response.message.content
        
    # Try dictionary access second
    if isinstance(response, dict) and "message" in response:
        message = response["message"]
        if isinstance(message, dict) and "content" in message:
            return message["content"]
            
    # Neither structure matched
    logger.error(f"Unexpected response structure: {response}")
    raise RuntimeError("Failed to parse model response (unknown format)")


def query_chat_model(
    prompt: str, 
    model_name: Optional[str] = None, 
    temperature: float = 0.7
) -> str:
    """
    Query the chat model with the given prompt.

    Args:
        prompt: The prompt string to send to the model
        model_name: Optional model override (defaults to config)
        temperature: Controls response randomness (0-1)

    Returns:
        The text response from the model

    Raises:
        ValueError: If prompt is empty
        RuntimeError: If query fails or response parsing fails
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")

    active_model = model_name or CHAT_MODEL
    messages = [{"role": "user", "content": prompt}]
    
    try:
        logger.debug(f"Querying {active_model}...")
        start_time = time.time()

        response = ollama.chat(
            model=active_model,
            messages=messages,
            options={'temperature': temperature}
        )

        duration = time.time() - start_time
        logger.debug(f"LLM response received in {duration:.2f} seconds")
        
        content = extract_content(response)
        logger.debug(f"LLM response content length: {len(content)}")
        return content
        
    except ollama.ResponseError as e:
        error_msg = (f"Ollama API error (Status: {e.status_code}). "
                    f"Check if Ollama server is running and '{active_model}' is available.")
        logger.error(f"{error_msg} Details: {str(e)}")
        raise RuntimeError(error_msg) from e
        
    except Exception as e:
        logger.error(f"Unexpected error querying {active_model}: {str(e)}", exc_info=True)
        raise RuntimeError(f"Model query failed: {str(e)}") from e


# Test function
if __name__ == "__main__":
    print(f"Testing LLM Service with model: {CHAT_MODEL}")
    test_prompt = "Explain the concept of Streamlit in simple terms."
    
    try:
        response_text = query_chat_model(test_prompt)
        print("\n--- Model Response ---")
        print(response_text)
        print("--- End Model Response ---")
    except Exception as e:
        print(f"\nTest Failed: {e}")













#---------------------------------------------------------------------------------------------------------------------
# # llm_service.py

# import logging
# import ollama
# import time
# import os
# import sys

# # --- Configuration Import ---
# try:
#     # Add project root to sys.path if needed
#     project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#     if project_root not in sys.path:
#         sys.path.insert(0, project_root)
#     from config import CHAT_MODEL # Import the specific chat model name
# except ImportError as e:
#     logging.error(f"Error importing config in llm_service.py: {e}. Using default model.")
#     CHAT_MODEL = "gemma3:4b" # Fallback model

# # Configure logging for this module
# logger = logging.getLogger(__name__)
# # Basic logging setup if not configured by a main entry point
# if not logger.handlers:
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# def query_chat_model(prompt: str) -> str:
#     """
#     Query the configured chat model with the given prompt.

#     Args:
#         prompt: The prompt string to send to the model.

#     Returns:
#         The text response from the model.

#     Raises:
#         RuntimeError: If the model query fails or response parsing fails.
#         ValueError: If the prompt is empty.
#     """
#     if not prompt or not prompt.strip():
#         logger.error("query_chat_model called with empty prompt.")
#         raise ValueError("Prompt cannot be empty.")

#     model_name = CHAT_MODEL # Use the model from config

#     # Format the prompt as a single user message for Ollama
#     messages = [{"role": "user", "content": prompt}]

#     try:
#         logger.debug(f"Querying {model_name}...")
#         start_time = time.time()

#         response = ollama.chat(
#             model=model_name,
#             messages=messages
#             # Add other parameters like temperature if needed:
#             # options={'temperature': 0.7}
#         )

#         end_time = time.time()
#         logger.debug(f"LLM response received in {end_time - start_time:.2f} seconds.")
#         logger.debug(f"Raw Ollama response object type: {type(response)}")
#         # Log the raw response structure for debugging if needed (can be verbose)
#         # logger.debug(f"Raw Ollama response data: {response}")

#         # --- Updated Response Parsing ---
#         try:
#             # Check for the object structure first (common in recent ollama versions)
#             if hasattr(response, 'message') and hasattr(response.message, 'content'):
#                 content = response.message.content
#                 logger.debug(f"LLM response content length (from object): {len(content)}")
#                 return content
#             # Fallback: Check for the dictionary structure
#             elif isinstance(response, dict) and "message" in response and isinstance(response["message"], dict) and "content" in response["message"]:
#                 content = response["message"]["content"]
#                 logger.debug(f"LLM response content length (from dict): {len(content)}")
#                 return content
#             # If neither structure matches
#             else:
#                 # Log the actual response structure to help diagnose
#                 logger.error(f"Unexpected response structure from Ollama: {response}")
#                 raise RuntimeError("Failed to parse model response structure (unknown format).")
#         except AttributeError as e:
#             # Catch errors if attributes don't exist as expected
#             logger.error(f"Error accessing attributes in Ollama response object: {e}. Response: {response}", exc_info=True)
#             raise RuntimeError(f"Failed to parse model response attributes: {e}") from e
#         # --- End Updated Response Parsing ---

#     except ollama.ResponseError as e:
#         logger.error(f"Ollama API error when querying {model_name}: Status {e.status_code}, Error: {str(e)}")
#         # Provide a more specific error message if possible
#         error_message = f"Model query failed: Ollama API error (Status: {e.status_code}). Check if Ollama server is running and the model '{model_name}' is available."
#         raise RuntimeError(error_message) from e

#     except Exception as e:
#         # Catch other potential errors (network issues, parsing errors from above, etc.)
#         logger.error(f"Unexpected error querying model {model_name}: {str(e)}", exc_info=True)
#         # Re-raise ensuring the original exception context is preserved if possible
#         if isinstance(e, RuntimeError): # If it's the parsing error we raised
#              raise e
#         else: # For other unexpected errors
#              raise RuntimeError(f"Model query failed unexpectedly: {str(e)}") from e

# # --- Simple Test Function (Optional) ---
# if __name__ == "__main__":
#     print("--- Testing LLM Service ---")
#     test_prompt = "Explain the concept of Streamlit in simple terms."
#     print(f"Sending test prompt: '{test_prompt}' to model '{CHAT_MODEL}'")
#     try:
#         response_text = query_chat_model(test_prompt)
#         print("\n--- Model Response ---")
#         print(response_text)
#         print("--- End Model Response ---")
#     except (ValueError, RuntimeError) as e:
#         print(f"\n--- Test Failed ---")
#         print(f"Error: {e}")
#     except Exception as e:
#         print(f"\n--- Test Failed ---")
#         print(f"An unexpected error occurred: {e}")
#     print("\n--- LLM Service Test Finished ---")