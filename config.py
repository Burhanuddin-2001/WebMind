# config.py

import os
import logging
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Model Configuration ---
CHAT_MODEL = os.getenv("CHAT_MODEL", "gemma3:4b")

# Model-specific context length limits
MAX_LLM_CONTEXT_LENGTH = {
    "gemma3:4b": 100000
    # Add other models as needed
}

# --- Agent Configuration ---
MAX_SEARCH_ATTEMPTS = int(os.getenv("MAX_SEARCH_ATTEMPTS", "5"))

# --- Web Search Configuration ---
DDG_MAX_RESULTS = int(os.getenv("DDG_MAX_RESULTS", "5"))

# --- Tool Configuration (Paths) ---
_BASE_DIR = Path(__file__).parent.absolute()
SCRAPY_PROJECT_DIR = Path(os.getenv("SCRAPY_PROJECT_DIR", _BASE_DIR / "aiwebsearch"))
SELENIUM_DRIVER_PATH = os.getenv("SELENIUM_DRIVER_PATH")

# --- Logging Configuration ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# --- Validation Functions ---
def validate_paths() -> Dict[str, bool]:
    """Validate critical paths and return their status."""
    return {
        "scrapy_dir": SCRAPY_PROJECT_DIR.is_dir(),
        "selenium_driver": bool(SELENIUM_DRIVER_PATH and Path(SELENIUM_DRIVER_PATH).exists())
    }

def setup_logging(logger_name: str = None) -> logging.Logger:
    """Configure and return a logger instance."""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format=LOG_FORMAT
    )
    return logging.getLogger(logger_name if logger_name else __name__)

# Validate paths on import
_path_status = validate_paths()
_logger = setup_logging("config")

if not _path_status["scrapy_dir"]:
    _logger.warning(f"Scrapy project directory not found: {SCRAPY_PROJECT_DIR}")

if not _path_status["selenium_driver"]:
    _logger.warning("Selenium driver path invalid or not configured")

# --- Example Usage ---
if __name__ == "__main__":
    print("--- Configuration Settings ---")
    config_items = {
        "Chat Model": CHAT_MODEL,
        "Max Context Length": MAX_LLM_CONTEXT_LENGTH.get(CHAT_MODEL, "Default"),
        "Max Search Attempts": MAX_SEARCH_ATTEMPTS,
        "DDG Max Results": DDG_MAX_RESULTS,
        "Scrapy Project Dir": str(SCRAPY_PROJECT_DIR),
        "Selenium Driver Path": SELENIUM_DRIVER_PATH or "Not Set",
        "Log Level": LOG_LEVEL,
        "Path Validation": _path_status
    }
    
    for key, value in config_items.items():
        print(f"{key}: {value}")
    print("--- End Configuration ---")
    
    _logger.info("Configuration loaded and validated.")













#-------------------------------------------------------------------------------------------------------------------
# # config.py

# import os
# import logging
# from dotenv import load_dotenv

# # Load environment variables from a .env file if it exists
# # Useful for sensitive info or environment-specific paths like SELENIUM_DRIVER_PATH
# load_dotenv()

# # --- Model Configuration ---
# # Specify the Ollama chat model to be used by the agent
# CHAT_MODEL = os.getenv("CHAT_MODEL", "gemma3:4b") # Default to gemma3:4b if not set in .env

# # --- Agent Configuration ---
# # Maximum number of URLs the agent will attempt to scrape sequentially
# MAX_SEARCH_ATTEMPTS = 5 # Keep this reasonably low to manage execution time

# # --- Web Search Configuration ---
# # Maximum number of search results to fetch initially from DuckDuckGo
# DDG_MAX_RESULTS = 5 # Fetch a few more than max attempts to have backups if some fail

# # --- Tool Configuration (Paths) ---
# # !! IMPORTANT: Set these paths correctly, especially SCRAPY_PROJECT_DIR and SELENIUM_DRIVER_PATH !!

# # Get the directory where this config file is located
# _BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# # Path to the root directory of the Scrapy project (webscraptool)
# # Assumes 'webscraptool' directory is at the same level as this config file
# SCRAPY_PROJECT_DIR = os.getenv("SCRAPY_PROJECT_DIR", os.path.join(_BASE_DIR, "aiwebsearch"))

# # Path to the Selenium ChromeDriver executable (or other webdriver)
# # This is REQUIRED by the Scrapy project (webscraptool/settings.py) if using SeleniumMiddleware
# # Best practice: Set this in your .env file
# # Example .env line: SELENIUM_DRIVER_PATH=C:/path/to/your/chromedriver.exe
# SELENIUM_DRIVER_PATH = os.getenv("SELENIUM_DRIVER_PATH")

# # --- Sanity Checks & Warnings ---

# # Check if the Scrapy project directory exists
# if not os.path.isdir(SCRAPY_PROJECT_DIR):
#     logging.warning(f"Configured SCRAPY_PROJECT_DIR does not exist or is not a directory: {SCRAPY_PROJECT_DIR}")
#     # Depending on your setup, you might want to raise an error here if it's critical
#     # raise FileNotFoundError(f"Scrapy project directory not found: {SCRAPY_PROJECT_DIR}")

# # Check if the Selenium driver path is configured and exists
# if not SELENIUM_DRIVER_PATH:
#      # This is only a warning because the user *might* modify the scraper not to use Selenium,
#      # but the current 'myspider.py' likely requires it.
#      logging.warning("SELENIUM_DRIVER_PATH is not configured in config.py or .env file. Web scraping tool (Scrapy/Selenium) might fail.")
# elif not os.path.exists(SELENIUM_DRIVER_PATH):
#      logging.warning(f"Configured SELENIUM_DRIVER_PATH does not exist: {SELENIUM_DRIVER_PATH}. Web scraping tool (Scrapy/Selenium) might fail.")
#      # Consider raising an error if Selenium is definitely required:
#      # raise FileNotFoundError(f"Selenium driver not found at configured path: {SELENIUM_DRIVER_PATH}")


# # --- Logging Configuration (Optional but Recommended) ---
# LOG_LEVEL = "INFO" # Logging level (e.g., DEBUG, INFO, WARNING, ERROR)
# LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# # Note: Basic logging configuration might be handled in the main entry point (streamlit_app.py)
# # This just defines the constants if needed elsewhere.

# # --- Example Usage (for testing this file directly) ---
# if __name__ == "__main__":
#     print("--- Configuration Settings ---")
#     print(f"Chat Model: {CHAT_MODEL}")
#     print(f"Max Search Attempts: {MAX_SEARCH_ATTEMPTS}")
#     print(f"DDG Max Results: {DDG_MAX_RESULTS}")
#     print(f"Scrapy Project Dir: {SCRAPY_PROJECT_DIR}")
#     print(f"Selenium Driver Path: {SELENIUM_DRIVER_PATH if SELENIUM_DRIVER_PATH else 'Not Set'}")
#     print(f"Log Level: {LOG_LEVEL}")
#     print("--- End Configuration ---")

#     # Example of how logging might be used with these settings
#     logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper(), logging.INFO), format=LOG_FORMAT)
#     logger = logging.getLogger("config_test")
#     logger.info("Configuration loaded.")
#     if not SELENIUM_DRIVER_PATH or not os.path.exists(SELENIUM_DRIVER_PATH):
#         logger.warning("Selenium driver path check failed (as seen in config warnings).")
#     if not os.path.isdir(SCRAPY_PROJECT_DIR):
#         logger.warning("Scrapy project directory check failed.")