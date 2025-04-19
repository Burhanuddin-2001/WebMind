# web_tools.py

import logging
import subprocess
import os
import json
import tempfile
from duckduckgo_search import DDGS
from typing import List, Optional
import sys
from pathlib import Path
from functools import lru_cache

# --- Configuration Import ---
try:
    # Add project root to sys.path if needed
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from config import SCRAPY_PROJECT_DIR
except ImportError as e:
    logging.error(f"Error importing config in web_tools.py: {e}. Using default Scrapy path.")
    SCRAPY_PROJECT_DIR = "./aiwebsearch"
except Exception as e:
    logging.error(f"An unexpected error occurred during config import: {e}")
    SCRAPY_PROJECT_DIR = "./aiwebsearch"

# Configure logging for this module
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@lru_cache(maxsize=100)
def perform_web_search(query: str, num_results: int) -> List[str]:
    """
    Performs a web search using DuckDuckGo and returns a list of URLs.
    Results are cached to improve performance for repeated queries.

    Args:
        query: The search query string.
        num_results: The maximum number of results to retrieve.

    Returns:
        A list of URL strings, or an empty list if the search fails or yields no results.
    """
    logger.info(f"Performing web search for: '{query}' (max {num_results} results)")
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=num_results))
        
        # Extract URLs with list comprehension for better performance
        urls = [result['href'] for result in results 
                if isinstance(result, dict) and 'href' in result and result['href']]
        
        logger.info(f"Found {len(urls)} valid URLs from DDG search.")
        if len(urls) != len(results):
            logger.warning(f"Filtered out {len(results) - len(urls)} results missing valid 'href'.")
            
        return urls

    except Exception as e:
        logger.error(f"DuckDuckGo search failed: {e}", exc_info=True)
        return []


def scrape_single_url(url: str) -> Optional[str]:
    """
    Runs the Scrapy spider ('myspider') for a single URL and returns the extracted text.

    Args:
        url: The URL to scrape.

    Returns:
        The extracted text content as a string if successful, otherwise None.
    """
    if not url:
        logger.warning("scrape_single_url called with empty URL.")
        return None

    scrapy_dir = Path(SCRAPY_PROJECT_DIR)
    if not scrapy_dir.is_dir():
        logger.error(f"Scrapy project directory not found: {SCRAPY_PROJECT_DIR}")
        return None

    temp_file_path = None
    try:
        # Create temporary file for output
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_f:
            temp_file_path = temp_f.name
        logger.debug(f"Created temporary output file for Scrapy: {temp_file_path}")

        # Construct and run the Scrapy command
        command = f'scrapy crawl myspider -a start_urls="{url}" -O "{temp_file_path}"'
        logger.info(f"Running Scrapy for URL: {url}")
        
        # Use subprocess.run with appropriate settings
        process = subprocess.run(
            command,
            shell=True,
            check=False,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            cwd=SCRAPY_PROJECT_DIR
        )

        # Check if process succeeded
        if process.returncode != 0:
            logger.error(f"Scrapy command failed for URL {url} with return code {process.returncode}.")
            logger.error(f"Scrapy stderr:\n{process.stderr[:2000]}")
            return None
        
        # Log output info
        logger.info(f"Scrapy command completed successfully for URL {url}.")
        if process.stdout:
            logger.debug(f"Scrapy stdout (first 500 chars):\n{process.stdout[:500]}...")
        if process.stderr:
            logger.warning(f"Scrapy stderr (first 500 chars):\n{process.stderr[:500]}...")

        # Process the output file
        output_file = Path(temp_file_path)
        if not output_file.exists():
            logger.error(f"Scrapy output file not found: {temp_file_path}")
            return None
            
        if output_file.stat().st_size == 0:
            logger.warning(f"Scrapy output file is empty: {temp_file_path}")
            return None
            
        # Parse JSON output
        with open(temp_file_path, 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)
            
        # Extract text from scraped data
        if isinstance(scraped_data, list) and scraped_data:
            first_item = scraped_data[0]
            if isinstance(first_item, dict) and 'text' in first_item:
                extracted_text = first_item.get('text')
                if extracted_text:
                    logger.debug(f"Successfully extracted text (length: {len(extracted_text)}) from {url}.")
                    return extracted_text
                logger.warning(f"Scraped data for {url} found, but 'text' field was empty.")
                return ""
            logger.warning(f"Scraped data format unexpected for {url}. Data: {first_item}")
        else:
            logger.error(f"Scrapy output for {url} did not contain expected JSON format")
        
        return None

    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from Scrapy output file: {temp_file_path}", exc_info=True)
        # Log file content on error if small enough
        try:
            if temp_file_path and Path(temp_file_path).exists() and Path(temp_file_path).stat().st_size < 1024:
                with open(temp_file_path, 'r', encoding='utf-8') as f_err:
                    logger.error(f"Content of invalid JSON file:\n{f_err.read()}")
        except Exception:
            pass
        return None
    except Exception as e:
        logger.error(f"Error scraping URL {url}: {e}", exc_info=True)
        return None
    finally:
        # Ensure temporary file is cleaned up
        if temp_file_path and Path(temp_file_path).exists():
            try:
                os.remove(temp_file_path)
                logger.debug(f"Removed temporary Scrapy output file: {temp_file_path}")
            except OSError as e:
                logger.warning(f"Could not remove temporary file {temp_file_path}: {e}")


# --- Simple Test Function (Optional) ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("--- Testing Web Tools ---")

    # Test 1: Web Search
    test_query = "Latest news on Perseverance rover"
    print(f"\n1. Testing web search for: '{test_query}'")
    try:
        urls = perform_web_search(test_query, num_results=3)
        if urls:
            print(f"  Success! Found URLs:")
            for u in urls:
                print(f"  - {u}")
        else:
            print("  Search returned no URLs or failed.")
    except Exception as e:
        print(f"  Search test failed with error: {e}")

    # Test 2: Scraping
    test_url = "https://example.com"
    if test_url:
        print(f"\n2. Testing scraping for URL: {test_url}")
        print(f"   (Using Scrapy project dir: {SCRAPY_PROJECT_DIR})")
        try:
            scraped_content = scrape_single_url(test_url)
            if scraped_content is not None:
                print(f"  Success! Scraped content (first 300 chars):")
                print(f"  '{scraped_content[:300]}...'")
                print(f"  (Total length: {len(scraped_content)})")
            else:
                print("  Scraping failed or returned no content.")
        except Exception as e:
            print(f"  Scraping test failed with error: {e}")
    else:
        print("\n2. Skipping scraping test (no URL available).")

    print("\n--- Web Tools Test Finished ---")


















#-------------------------------------------------------------------------------------------------------------------------------

# # web_tools.py

# import logging
# import subprocess
# import os
# import json
# import tempfile
# from duckduckgo_search import DDGS
# from typing import List, Optional
# import sys

# # --- Configuration Import ---
# try:
#     # Add project root to sys.path if needed
#     project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#     if project_root not in sys.path:
#         sys.path.insert(0, project_root)
#     # Use the correct Scrapy project name as defined in config.py
#     from config import SCRAPY_PROJECT_DIR
# except ImportError as e:
#     logging.error(f"Error importing config in web_tools.py: {e}. Using default Scrapy path.")
#     # Define a fallback or raise an error if SCRAPY_PROJECT_DIR is critical
#     SCRAPY_PROJECT_DIR = "./aiwebsearch" # Ensure this matches your Scrapy project folder name
# except Exception as e:
#     logging.error(f"An unexpected error occurred during config import: {e}")
#     SCRAPY_PROJECT_DIR = "./aiwebsearch" # Fallback

# # Configure logging for this module
# logger = logging.getLogger(__name__)
# # Basic logging setup if not configured by a main entry point
# if not logger.handlers:
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# def perform_web_search(query: str, num_results: int) -> List[str]:
#     """
#     Performs a web search using DuckDuckGo and returns a list of URLs.

#     Args:
#         query: The search query string.
#         num_results: The maximum number of results to retrieve.

#     Returns:
#         A list of URL strings, or an empty list if the search fails or yields no results.
#     """
#     logger.info(f"Performing web search for: '{query}' (max {num_results} results)")
#     urls = []
#     try:
#         # Use DDGS context manager for cleanup
#         with DDGS() as ddgs:
#             # Fetch results using ddgs.text(), which includes URLs
#             results = list(ddgs.text(query, max_results=num_results))

#         # Extract valid URLs ('href' key) from the results
#         for result in results:
#             if isinstance(result, dict) and 'href' in result and result['href']:
#                 urls.append(result['href'])

#         logger.info(f"Found {len(urls)} valid URLs from DDG search.")
#         if len(urls) != len(results):
#              logger.warning(f"Filtered out {len(results) - len(urls)} results missing valid 'href'.")

#     except Exception as e:
#         logger.error(f"DuckDuckGo search failed: {e}", exc_info=True)
#         # Return empty list on failure
#         return []

#     return urls


# def scrape_single_url(url: str) -> Optional[str]:
#     """
#     Runs the Scrapy spider ('myspider') for a single URL and returns the extracted text.

#     Args:
#         url: The URL to scrape.

#     Returns:
#         The extracted text content as a string if successful, otherwise None.
#     """
#     if not url:
#         logger.warning("scrape_single_url called with empty URL.")
#         return None

#     if not os.path.isdir(SCRAPY_PROJECT_DIR):
#          logger.error(f"Scrapy project directory not found or not a directory: {SCRAPY_PROJECT_DIR}")
#          return None

#     temp_file_path = None
#     try:
#         # Create a temporary file to store the Scrapy output for this specific URL
#         # Use NamedTemporaryFile to get a path, close it so Scrapy can write, then read/delete.
#         # Ensure deletion happens even on error using 'finally' block.
#         with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_f:
#             temp_file_path = temp_f.name
#         logger.debug(f"Created temporary output file for Scrapy: {temp_file_path}")

#         # Construct the Scrapy command
#         # Use -O to overwrite/create the output file safely
#         # Pass the single URL via -a start_urls
#         # Ensure the spider name 'myspider' matches your spider file
#         command = f'scrapy crawl myspider -a start_urls="{url}" -O "{temp_file_path}"'

#         logger.info(f"Running Scrapy for URL: {url}")
#         logger.debug(f"Executing command in '{SCRAPY_PROJECT_DIR}': {command}")

#         # Run the Scrapy command as a subprocess
#         # Ensure the current working directory is the Scrapy project root
#         process = subprocess.run(
#             command,
#             shell=True,        # Use shell to handle the command string easily
#             check=False,       # Don't raise exception on non-zero exit; we'll check returncode
#             capture_output=True, # Capture stdout/stderr
#             text=True,         # Decode stdout/stderr as text
#             encoding='utf-8',  # Specify encoding
#             errors='ignore',   # *** ADDED: Ignore UTF-8 decoding errors in stdout/stderr ***
#             cwd=SCRAPY_PROJECT_DIR # Set working directory
#         )

#         # Check if Scrapy ran successfully
#         if process.returncode != 0:
#             logger.error(f"Scrapy command failed for URL {url} with return code {process.returncode}.")
#             # Log stderr even on failure, potentially truncated if very long
#             logger.error(f"Scrapy stderr:\n{process.stderr[:2000]}") # Log start of stderr
#             return None
#         else:
#             logger.info(f"Scrapy command completed successfully for URL {url}.")
#             # Log stdout/stderr only if they contain data (and truncate for brevity)
#             if process.stdout:
#                  logger.debug(f"Scrapy stdout (first 500 chars):\n{process.stdout[:500]}...")
#             if process.stderr: # Log stderr even on success, might contain warnings
#                  logger.warning(f"Scrapy stderr (first 500 chars):\n{process.stderr[:500]}...")


#         # Read the result from the temporary JSON file
#         if not os.path.exists(temp_file_path):
#              logger.error(f"Scrapy finished but output file not found: {temp_file_path}")
#              return None

#         # Add extra check for empty file before trying to load JSON
#         if os.path.getsize(temp_file_path) == 0:
#             logger.warning(f"Scrapy output file is empty: {temp_file_path}")
#             return None # Treat empty file as no content extracted

#         with open(temp_file_path, 'r', encoding='utf-8') as f:
#             scraped_data = json.load(f)

#         # Expecting output like: [{"url": "...", "text": "..."}]
#         if isinstance(scraped_data, list) and len(scraped_data) > 0:
#             # Get the first item, assuming single URL scrape yields one result dict
#             first_item = scraped_data[0]
#             if isinstance(first_item, dict) and 'text' in first_item:
#                 extracted_text = first_item.get('text', None)
#                 if extracted_text:
#                     logger.debug(f"Successfully extracted text (length: {len(extracted_text)}) from {url}.")
#                     return extracted_text
#                 else:
#                     logger.warning(f"Scraped data for {url} found, but 'text' field was empty.")
#                     return "" # Return empty string if text field exists but is empty
#             else:
#                 logger.warning(f"Scraped data format unexpected (missing 'text' key or not a dict) in first item for {url}. Data: {first_item}")
#                 return None
#         elif isinstance(scraped_data, list) and len(scraped_data) == 0:
#              logger.warning(f"Scrapy output file for {url} contained an empty list. No data extracted.")
#              return None
#         else:
#             logger.error(f"Scrapy output file for {url} did not contain a JSON list. Content: {scraped_data}")
#             return None

#     except json.JSONDecodeError:
#         logger.error(f"Error decoding JSON from Scrapy output file: {temp_file_path}", exc_info=True)
#         # Log the content of the file if possible and small enough
#         try:
#             if temp_file_path and os.path.exists(temp_file_path) and os.path.getsize(temp_file_path) < 1024:
#                  with open(temp_file_path, 'r', encoding='utf-8') as f_err:
#                       logger.error(f"Content of invalid JSON file ({temp_file_path}):\n{f_err.read()}")
#         except Exception:
#             pass # Ignore errors during error logging
#         return None
#     except FileNotFoundError:
#         # This might happen if the temp file creation failed earlier, though unlikely
#         logger.error(f"Temporary file path not found during processing: {temp_file_path}", exc_info=True)
#         return None
#     except Exception as e:
#         logger.error(f"An unexpected error occurred during scraping or processing for URL {url}: {e}", exc_info=True)
#         return None
#     finally:
#         # --- Cleanup: Ensure the temporary file is deleted ---
#         if temp_file_path and os.path.exists(temp_file_path):
#             try:
#                 os.remove(temp_file_path)
#                 logger.debug(f"Removed temporary Scrapy output file: {temp_file_path}")
#             except OSError as e:
#                 logger.warning(f"Could not remove temporary Scrapy output file {temp_file_path}: {e}")


# # --- Simple Test Function (Optional) ---
# if __name__ == "__main__":
#     # Configure logging for direct script execution
#     logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     logger.info("--- Testing Web Tools ---")

#     # Test 1: Web Search
#     test_query = "Latest news on Perseverance rover"
#     print(f"\n1. Testing web search for: '{test_query}'")
#     try:
#         urls = perform_web_search(test_query, num_results=3)
#         if urls:
#             print(f"  Success! Found URLs:")
#             for u in urls:
#                 print(f"  - {u}")
#         else:
#             print("  Search returned no URLs or failed.")
#     except Exception as e:
#         print(f"  Search test failed with error: {e}")

#     # Test 2: Scraping (Requires Scrapy project and potentially Selenium setup)
#     # Use a known simple URL for testing if possible
#     test_url = "https://example.com" # Replace with a suitable test URL if needed
#     # test_url = urls[0] if urls else None # Or use a URL from the search test

#     if test_url:
#         print(f"\n2. Testing scraping for URL: {test_url}")
#         # Ensure SCRAPY_PROJECT_DIR is correctly set relative to this file when run directly
#         # Or provide an absolute path in config.py / .env
#         print(f"   (Using Scrapy project dir: {SCRAPY_PROJECT_DIR})")
#         try:
#             scraped_content = scrape_single_url(test_url)
#             if scraped_content is not None:
#                 print(f"  Success! Scraped content (first 300 chars):")
#                 print(f"  '{scraped_content[:300]}...'")
#                 print(f"  (Total length: {len(scraped_content)})")
#             else:
#                 print("  Scraping failed or returned no content.")
#         except Exception as e:
#             print(f"  Scraping test failed with error: {e}")
#     else:
#         print("\n2. Skipping scraping test (no URL available).")

#     print("\n--- Web Tools Test Finished ---")