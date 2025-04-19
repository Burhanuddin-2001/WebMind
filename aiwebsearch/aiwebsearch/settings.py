# aiwebsearch/aiwebsearch/settings.py

import sys
import os
import logging
from pathlib import Path

# Configure basic logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path Setup to Import Main Config
try:
    project_root = Path(__file__).absolute().parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from config import SELENIUM_DRIVER_PATH
    CONFIG_IMPORT_SUCCESS = True
    logger.info(f"Successfully imported SELENIUM_DRIVER_PATH: {SELENIUM_DRIVER_PATH}")
except ImportError:
    logger.error("Could not import config.py from the main project root.")
    SELENIUM_DRIVER_PATH = None
    CONFIG_IMPORT_SUCCESS = False
except Exception as e:
    logger.error(f"Unexpected error during config import: {e}")
    SELENIUM_DRIVER_PATH = None
    CONFIG_IMPORT_SUCCESS = False

# Scrapy Project Settings
BOT_NAME = 'aiwebsearch'
SPIDER_MODULES = ['aiwebsearch.spiders']
NEWSPIDER_MODULE = 'aiwebsearch.spiders'

# Polite crawling settings
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 1
DOWNLOAD_DELAY = 3

# Scrapy-Selenium Integration
DOWNLOADER_MIDDLEWARES = {
    'scrapy_selenium.SeleniumMiddleware': 800
}

# Selenium Driver Configuration
SELENIUM_DRIVER_NAME = 'chrome'

# Configure Selenium Service
try:
    from selenium.webdriver.chrome.service import Service
    
    if CONFIG_IMPORT_SUCCESS and SELENIUM_DRIVER_PATH and Path(SELENIUM_DRIVER_PATH).exists():
        SELENIUM_DRIVER_SERVICE = Service(executable_path=SELENIUM_DRIVER_PATH)
        logger.info(f"Using Selenium Service with executable: {SELENIUM_DRIVER_PATH}")
    else:
        SELENIUM_DRIVER_SERVICE = None
        reasons = []
        if not CONFIG_IMPORT_SUCCESS:
            reasons.append("config import failed")
        elif not SELENIUM_DRIVER_PATH:
            reasons.append("SELENIUM_DRIVER_PATH not set in config")
        elif not Path(SELENIUM_DRIVER_PATH).exists():
            reasons.append(f"path does not exist: {SELENIUM_DRIVER_PATH}")
        
        logger.warning(f"Using default Selenium Service (reasons: {', '.join(reasons)})")
        
except ImportError:
    logger.error("Failed to import Selenium Service class")
    SELENIUM_DRIVER_SERVICE = None
except Exception as e:
    logger.error(f"Failed to initialize Selenium Service: {e}")
    SELENIUM_DRIVER_SERVICE = None

# Browser arguments
SELENIUM_DRIVER_ARGUMENTS = [
    '--headless',
    '--disable-gpu',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    '--disable-blink-features=AutomationControlled',
    '--log-level=WARNING'
]

# Future-proof settings
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

# Logging Configuration
LOG_LEVEL = 'INFO'





#--------------------------------------------------------------------------------------------------------------
# # aiwebsearch/aiwebsearch/settings.py

# import sys
# import os
# import logging # Import logging for warnings

# # --- Path Setup to Import Main Config ---
# # Add the parent directory (streamlit-ai-search) to sys.path
# # Assumes settings.py is in streamlit-ai-search/aiwebsearch/aiwebsearch/
# try:
#     project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
#     if project_root not in sys.path:
#         sys.path.insert(0, project_root)

#     # Import the specific variable needed from the main config
#     from config import SELENIUM_DRIVER_PATH
#     SELENIUM_DRIVER_EXECUTABLE_PATH_FROM_CONFIG = SELENIUM_DRIVER_PATH # Assign to a distinct temporary name
#     CONFIG_IMPORT_SUCCESS = True
#     logging.info(f"Successfully imported SELENIUM_DRIVER_PATH from main config: {SELENIUM_DRIVER_EXECUTABLE_PATH_FROM_CONFIG}")

# except ImportError:
#     logging.error("Could not import config.py from the main project root.")
#     logging.warning("Web scraping using Selenium might fail without SELENIUM_DRIVER_PATH.")
#     SELENIUM_DRIVER_EXECUTABLE_PATH_FROM_CONFIG = None
#     CONFIG_IMPORT_SUCCESS = False
# except Exception as e:
#     logging.error(f"An unexpected error occurred during config import: {e}")
#     SELENIUM_DRIVER_EXECUTABLE_PATH_FROM_CONFIG = None
#     CONFIG_IMPORT_SUCCESS = False

# # --- Scrapy Project Settings ---
# BOT_NAME = 'aiwebsearch' # Updated bot name

# SPIDER_MODULES = ['aiwebsearch.spiders'] # Updated path
# NEWSPIDER_MODULE = 'aiwebsearch.spiders' # Updated path

# # Obey robots.txt rules (Set to False if specifically required, but True is polite)
# ROBOTSTXT_OBEY = True

# # Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 1

# # Configure a delay for requests for the same website (default: 0)
# DOWNLOAD_DELAY = 3

# # The download delay setting will honor only one of:
# #CONCURRENT_REQUESTS_PER_DOMAIN = 1
# #CONCURRENT_REQUESTS_PER_IP = 1

# # Disable cookies (enabled by default)
# #COOKIES_ENABLED = False

# # Disable Telnet Console (enabled by default)
# #TELNETCONSOLE_ENABLED = False

# # Override the default request headers:
# #DEFAULT_REQUEST_HEADERS = {
# #   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
# #   'Accept-Language': 'en',
# #}

# # Enable or disable spider middlewares
# # See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# #SPIDER_MIDDLEWARES = {
# #    'aiwebsearch.middlewares.AiwebsearchSpiderMiddleware': 543, # Example if you add middlewares
# #}

# # --- Scrapy-Selenium Integration ---

# # Enable Scrapy-Selenium middleware
# DOWNLOADER_MIDDLEWARES = {
#     'scrapy_selenium.SeleniumMiddleware': 800
# }

# # Selenium Driver Configuration
# SELENIUM_DRIVER_NAME = 'chrome' # Or 'firefox', etc.

# # *** THE FIX IS HERE: Use Service object for Selenium 4+ ***
# # Import the Service class (adjust path based on your webdriver)
# try:
#     from selenium.webdriver.chrome.service import Service
#     # from selenium.webdriver.firefox.service import Service # Example for Firefox
# except ImportError:
#      logging.error("Failed to import Selenium Service class. Ensure 'selenium' library is installed correctly.")
#      # Handle this case - maybe raise error or set Service to None?
#      Service = None

# # Define the Service object using the path from config
# # Check if the path was successfully imported and exists before creating the Service
# if Service and CONFIG_IMPORT_SUCCESS and SELENIUM_DRIVER_EXECUTABLE_PATH_FROM_CONFIG and os.path.exists(SELENIUM_DRIVER_EXECUTABLE_PATH_FROM_CONFIG):
#     try:
#         SELENIUM_DRIVER_SERVICE = Service(executable_path=SELENIUM_DRIVER_EXECUTABLE_PATH_FROM_CONFIG)
#         logging.info(f"Using Selenium Service with executable: {SELENIUM_DRIVER_EXECUTABLE_PATH_FROM_CONFIG}")
#     except Exception as service_init_error:
#         logging.error(f"Failed to initialize Selenium Service object: {service_init_error}", exc_info=True)
#         SELENIUM_DRIVER_SERVICE = None # Fallback if service creation fails
# else:
#     # Fallback: Let Selenium try to find the driver automatically if path is missing/invalid
#     SELENIUM_DRIVER_SERVICE = None # Setting to None lets scrapy-selenium use default Service() behavior
#     if not Service:
#          logging.warning("Selenium Service class not imported. Cannot configure service.")
#     elif not CONFIG_IMPORT_SUCCESS:
#          logging.warning("Could not import config, Selenium Service not configured with specific path.")
#     elif not SELENIUM_DRIVER_EXECUTABLE_PATH_FROM_CONFIG:
#          logging.warning("SELENIUM_DRIVER_PATH not set in config/.env, Selenium Service not configured with specific path.")
#     elif not os.path.exists(SELENIUM_DRIVER_EXECUTABLE_PATH_FROM_CONFIG):
#          logging.warning(f"Configured SELENIUM_DRIVER_PATH does not exist: {SELENIUM_DRIVER_EXECUTABLE_PATH_FROM_CONFIG}. Selenium Service not configured with specific path.")
#     logging.info("Attempting to let Selenium manage the driver automatically via default Service().")


# # !! REMOVED OR COMMENTED OUT the old executable path setting !!
# # SELENIUM_DRIVER_EXECUTABLE_PATH = SELENIUM_DRIVER_EXECUTABLE_PATH_FROM_CONFIG # DO NOT USE THIS

# # Arguments to pass to the Selenium driver (e.g., headless mode) - Keep these
# SELENIUM_DRIVER_ARGUMENTS = [
#     '--headless', # Run in headless mode (no browser UI)
#     '--disable-gpu', # Often recommended for headless
#     '--no-sandbox', # May be needed in some environments (like Docker)
#     '--disable-dev-shm-usage', # May be needed in some environments
#     # Set a realistic user agent to avoid blocking
#     '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#     '--disable-blink-features=AutomationControlled', # Attempt to hide automation flags
#     '--log-level=WARNING' # Reduce browser console noise
# ]


# # --- Other Scrapy Settings ---

# # Enable or disable downloader middlewares
# # See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# #DOWNLOADER_MIDDLEWARES = {
# #    'aiwebsearch.middlewares.AiwebsearchDownloaderMiddleware': 543, # Example
# #}

# # Enable or disable extensions
# # See https://docs.scrapy.org/en/latest/topics/extensions.html
# #EXTENSIONS = {
# #    'scrapy.extensions.telnet.TelnetConsole': None,
# #}

# # Configure item pipelines
# # See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# #ITEM_PIPELINES = {
# #    'aiwebsearch.pipelines.AiwebsearchPipeline': 300, # Example
# #}

# # Enable and configure the AutoThrottle extension (optional)
# # See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# #AUTOTHROTTLE_ENABLED = True
# #AUTOTHROTTLE_START_DELAY = 5
# #AUTOTHROTTLE_MAX_DELAY = 60
# #AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# #AUTOTHROTTLE_DEBUG = False

# # Enable and configure HTTP caching (disabled by default)
# # See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# #HTTPCACHE_ENABLED = True
# #HTTPCACHE_EXPIRATION_SECS = 0
# #HTTPCACHE_DIR = 'httpcache'
# #HTTPCACHE_IGNORE_HTTP_CODES = []
# #HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# # Set settings whose default value is deprecated to a future-proof value
# REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
# TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

# # Logging Configuration
# LOG_LEVEL = 'INFO' # Set to 'DEBUG' for more verbose output during development
