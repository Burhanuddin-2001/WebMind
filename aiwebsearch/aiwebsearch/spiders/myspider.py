# webscraptool/webscraptool/spiders/myspider.py

import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from urllib.parse import urlparse
import logging
from readability import Document
import lxml.html
from typing import List, Iterator, Dict, Any, Optional

class MySpider(scrapy.Spider):
    """
    A Scrapy spider that uses Selenium to scrape dynamic web pages,
    extracts main content using readability-lxml, and yields the URL and text.
    Accepts 'start_urls' as a comma-separated command-line argument.
    """
    name = 'myspider'

    def __init__(self, start_urls=None, *args, **kwargs):
        """
        Initializes the spider.

        Args:
            start_urls (str, optional): A comma-separated string of URLs to crawl.
                                        Passed via command line: -a start_urls='url1,url2'
        """
        super(MySpider, self).__init__(*args, **kwargs)
        self.start_urls = self._parse_urls(start_urls or getattr(self, "start_urls", None))
        self.logger.info(f"Spider initialized with {len(self.start_urls)} URLs")

    def _parse_urls(self, input_urls_str: Optional[str]) -> List[str]:
        """Parse and validate comma-separated URL string."""
        if not input_urls_str:
            raise ValueError("Spider requires 'start_urls' argument (e.g., -a start_urls='http://example.com')")
            
        result = []
        for url in input_urls_str.split(','):
            url = url.strip()
            if not url:
                continue
                
            parsed_uri = urlparse(url)
            # Add http scheme if missing
            if not parsed_uri.scheme:
                url = 'http://' + url
            result.append(url)
            
        return result

    def start_requests(self) -> Iterator[SeleniumRequest]:
        """Generate the initial Selenium requests for each start URL."""
        if not self.start_urls:
            self.logger.warning("No valid start URLs provided to the spider.")
            return

        for url in self.start_urls:
            self.logger.debug(f"Creating SeleniumRequest for: {url}")
            yield SeleniumRequest(
                url=url,
                callback=self.parse,
                wait_until=EC.presence_of_element_located((By.TAG_NAME, "body")),
                wait_time=20,
                errback=self.errback,
            )

    def parse(self, response) -> Iterator[Dict[str, str]]:
        """
        Process the response and extract content using readability-lxml.
        
        Args:
            response: The Scrapy response object with Selenium-rendered page
        
        Yields:
            Dict containing URL and extracted text
        """
        self.logger.info(f"Processing: {response.url} (Status: {response.status})")

        try:
            # Verify content is HTML
            content_type = response.headers.get('Content-Type', b'').decode('utf-8', errors='ignore').lower()
            if 'text/html' not in content_type and 'application/xhtml+xml' not in content_type:
                self.logger.warning(f"Skipping non-HTML content: {content_type}")
                return
            
            # Extract text content
            cleaned_text = self._extract_content(response)
            
            if cleaned_text:
                self.logger.info(f"Extracted {len(cleaned_text)} chars from {response.url}")
                yield {
                    'url': response.url,
                    'text': cleaned_text,
                }
            else:
                self.logger.warning(f"No text extracted from {response.url}")
                
        except Exception as e:
            self.logger.exception(f"Error parsing {response.url}: {str(e)}")

    def _extract_content(self, response) -> str:
        """Extract main content from the page using readability with fallback."""
        try:
            # Try readability first
            doc = Document(response.body, url=response.url)
            cleaned_html = doc.summary(html_partial=True)
            
            if cleaned_html:
                html_tree = lxml.html.fromstring(cleaned_html)
                cleaned_text = html_tree.text_content()
                cleaned_text = ' '.join(cleaned_text.split()).strip()
                
                if cleaned_text:
                    return cleaned_text
                
            self.logger.warning(f"Readability extracted empty content - using fallback")
            
        except Exception as read_err:
            self.logger.error(f"Readability failed: {read_err} - using fallback")
        
        # Fallback: extract all text from body
        body_text = ' '.join(response.css('body ::text').getall()).strip()
        return ' '.join(body_text.split()).strip()

    def errback(self, failure):
        """Handle request/download errors including Selenium issues."""
        request_url = getattr(failure.request, 'url', "Unknown URL")
        self.logger.error(f"Request failed: {request_url}")

        if failure.check(TimeoutException):
            self.logger.error(f"Selenium Timeout: {failure.value}")
        elif failure.check(WebDriverException):
            self.logger.error(f"WebDriver Error: {str(failure.value)}")
        elif failure.check(scrapy.exceptions.IgnoreRequest):
            self.logger.warning(f"Request ignored: {failure.value}")
        else:
            self.logger.error(f"Error Type: {failure.type}")
            self.logger.error(f"Error Value: {repr(failure.value)}")






#-----------------------------------------------------------------------------------------------------------------------------

# # webscraptool/webscraptool/spiders/myspider.py

# import scrapy
# from scrapy_selenium import SeleniumRequest
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, WebDriverException
# from urllib.parse import urlparse
# import logging
# from readability import Document # Use readability-lxml for content extraction
# import lxml.html # To parse the cleaned HTML from readability

# class MySpider(scrapy.Spider):
#     """
#     A Scrapy spider that uses Selenium to scrape dynamic web pages,
#     extracts main content using readability-lxml, and yields the URL and text.
#     Accepts 'start_urls' as a comma-separated command-line argument.
#     """
#     name = 'myspider'

#     def __init__(self, start_urls=None, *args, **kwargs):
#         """
#         Initializes the spider.

#         Args:
#             start_urls (str, optional): A comma-separated string of URLs to crawl.
#                                         Passed via command line: -a start_urls='url1,url2'
#         """
#         super(MySpider, self).__init__(*args, **kwargs)

#         # Get URLs from the command-line argument 'start_urls'
#         input_urls_str = getattr(self, "start_urls", None)
#         if start_urls: # Allow overriding via constructor if needed
#             input_urls_str = start_urls

#         if not input_urls_str:
#             raise ValueError("Spider requires 'start_urls' argument (e.g., -a start_urls='http://example.com')")

#         self.start_urls = []
#         # Process the comma-separated string, ensuring URLs have a scheme
#         for url in input_urls_str.split(','):
#             url = url.strip()
#             if not url:
#                 continue
#             parsed_uri = urlparse(url)
#             # Add http scheme if missing (basic assumption)
#             if not parsed_uri.scheme:
#                 url = 'http://' + url
#             self.start_urls.append(url)

#         self.logger.info(f"Spider initialized. Starting crawl with URLs: {self.start_urls}")

#     def start_requests(self):
#         """
#         Generates the initial requests (SeleniumRequests) for each start URL.
#         """
#         if not self.start_urls:
#              self.logger.warning("No valid start URLs provided to the spider.")
#              return

#         for url in self.start_urls:
#             self.logger.debug(f"Yielding SeleniumRequest for URL: {url}")
#             yield SeleniumRequest(
#                 url=url,
#                 callback=self.parse,
#                 # Wait for the body element to be present, indicating basic page load
#                 wait_until=EC.presence_of_element_located((By.TAG_NAME, "body")),
#                 # Increase wait time slightly for potentially slow-loading pages
#                 wait_time=20,
#                 # Specify errback function to handle request errors
#                 errback=self.errback,
#                 # Optional: Add screenshot for debugging if needed (remove in production)
#                 # screenshot=True
#             )

#     def parse(self, response):
#         """
#         Processes the response received after Selenium renders the page.
#         Extracts cleaned content using readability-lxml and yields the result.

#         Args:
#             response: The Scrapy response object containing the Selenium-rendered page source.
#         """
#         self.logger.info(f"Processing response for URL: {response.url} (Status: {response.status})")

#         # Optional: Save screenshot for debugging (corresponds to screenshot=True in request)
#         # if hasattr(response, 'meta') and 'screenshot' in response.meta:
#         #     screenshot_path = f"screenshot_{response.url.split('/')[-1]}.png"
#         #     with open(screenshot_path, 'wb') as f:
#         #         f.write(response.meta['screenshot'])
#         #     self.logger.info(f"Screenshot saved to {screenshot_path}")

#         try:
#             # 1. Verify content type is HTML (though Selenium usually handles this)
#             content_type = response.headers.get('Content-Type', b'').decode('utf-8').lower()
#             if 'text/html' not in content_type and 'application/xhtml+xml' not in content_type:
#                 self.logger.warning(f"Skipping non-HTML content ({content_type}) at {response.url}")
#                 return

#             # 2. Use Readability to extract main content
#             try:
#                 # Pass the response body (HTML source) to Readability
#                 doc = Document(response.body, url=response.url)
#                 # Get the main content as a cleaned HTML fragment
#                 cleaned_html_content = doc.summary(html_partial=True)

#                 # Extract plain text from the cleaned HTML using lxml
#                 if cleaned_html_content:
#                     html_tree = lxml.html.fromstring(cleaned_html_content)
#                     # Use text_content() to get all text within the cleaned fragment
#                     cleaned_text = html_tree.text_content()
#                     # Basic whitespace cleaning: replace multiple spaces/newlines with single space
#                     cleaned_text = ' '.join(cleaned_text.split()).strip()
#                 else:
#                     cleaned_text = "" # No content extracted by readability

#                 if not cleaned_text:
#                      self.logger.warning(f"Readability extracted empty content from {response.url}. Falling back to body text.")
#                      # Fallback: Extract text from the entire body if Readability fails or returns nothing
#                      cleaned_text = ' '.join(response.css('body ::text').getall()).strip()
#                      cleaned_text = ' '.join(cleaned_text.split()).strip() # Clean whitespace again

#             except Exception as read_err:
#                 self.logger.error(f"Readability processing failed for {response.url}: {read_err}. Falling back to raw body text.")
#                 # Fallback: Extract text from the entire body if Readability errors out
#                 cleaned_text = ' '.join(response.css('body ::text').getall()).strip()
#                 cleaned_text = ' '.join(cleaned_text.split()).strip() # Clean whitespace again

#             # 3. Yield the structured data item
#             if cleaned_text:
#                 self.logger.info(f"Successfully extracted text (length: {len(cleaned_text)}) from {response.url}")
#                 yield {
#                     'url': response.url,
#                     'text': cleaned_text,
#                 }
#             else:
#                  self.logger.warning(f"No text content could be extracted (even fallback) from {response.url}")


#         except Exception as e:
#             # Catch any other unexpected errors during parsing
#             self.logger.exception(f"Critical error parsing response for {response.url}: {str(e)}")

#     def errback(self, failure):
#         """
#         Handles errors that occur during the request/download process (including Selenium errors).

#         Args:
#             failure: A Twisted Failure object containing details about the error.
#         """
#         request_url = failure.request.url if hasattr(failure.request, 'url') else "Unknown URL"
#         self.logger.error(f"Request failed for URL: {request_url}")

#         # Log specific error types
#         if failure.check(TimeoutException):
#             self.logger.error(f"  Error Type: Selenium Timeout (wait_time exceeded?)")
#             self.logger.error(f"  Error Details: {failure.value}")
#         elif failure.check(WebDriverException):
#             self.logger.error(f"  Error Type: Selenium WebDriver Error")
#             # Log specific WebDriver errors if possible, otherwise generic message
#             self.logger.error(f"  Error Details: {str(failure.value)}")
#         elif failure.check(scrapy.exceptions.IgnoreRequest):
#              self.logger.warning(f"  Request ignored for {request_url}: {failure.value}")
#         else:
#             # Log other Scrapy/Twisted errors
#             self.logger.error(f"  Error Type: {failure.type}")
#             self.logger.error(f"  Error Value: {repr(failure.value)}")

#         # Optionally yield an error item if you want to track failures in the output
#         # yield {
#         #     'url': request_url,
#         #     'error': str(failure.value),
#         #     'error_type': str(failure.type)
#         # }