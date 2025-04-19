# WebMind

## Project Overview

The WebMind is an intelligent search assistant designed to provide direct answers to user queries by leveraging web content and AI analysis. Unlike traditional search engines that return a list of links, this tool actively scrapes the content of top search results and uses a locally hosted Large Language Model (LLM) via Ollama to extract and present the most relevant answer along with its source URL. This approach ensures privacy and control over the AI model used.

### High-Level Architecture

- **User Interface**: Built with Streamlit, allowing users to input queries and view results.
- **Web Search**: Utilizes DuckDuckGo to retrieve a list of relevant URLs.
- **Web Scraping**: Employs Scrapy and Selenium to fetch and render web page content.
- **AI Analysis**: Uses Ollama to host and query the LLM for content analysis.
- **Orchestration**: Managed by an agent that coordinates the entire process and provides real-time status updates.

## Requirements

- Python 3.8+
- Dependencies: See `requirements.txt`
- Ollama service running with model `gemma3:4b` (configurable)
- Chrome browser and matching ChromeDriver

To install Python dependencies:

```bash
pip install -r requirements.txt
```

To use a different Ollama model, update `CHAT_MODEL` in `config.py`. For integrating another LLM, modify the `llm_service.py` module accordingly.

## Setup & Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Burhanuddin-2001/WebMind.git
   cd advanced-ai-search-tool
   ```

2. **Create and activate a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **ChromeDriver setup**:

   - Download the ChromeDriver version that matches your Chrome browser from [ChromeDriver downloads](https://developer.chrome.com/docs/chromedriver/downloads).
   - Place the downloaded `chromedriver` executable in a directory of your choice and update `SELENIUM_DRIVER_PATH` in the `.env` file to point to its location.


5. **Configure environment variables**:

   - Create a `.env` file in the root directory:

     ```
     SELENIUM_DRIVER_PATH=path/to/chromedriver
     CHAT_MODEL=gemma3:4b
     ```

   - Ensure the Ollama service is running and accessible.

## Usage

1. **Launch the Streamlit app**:

   ```bash
   streamlit run streamlit_app.py
   ```

2. **Enter your query** in the web interface and click "Search".

3. **View the results**, including real-time status updates and the final answer with source URL if found.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push to your fork.
4. Open a pull request to the main repository.

Please follow the [contribution guidelines](CONTRIBUTING.md) if available.

## License

This project is licensed under the [MIT License](LICENSE).

## Author & Contact

- **Author**: Burhanuddin
- **LinkedIn**: www.linkedin.com/in/burhanuddin-cyber