# prompts.py

# Prompt template for checking if scraped content sufficiently answers the user query
SUFFICIENCY_CHECK_PROMPT_TEMPLATE = """
Original User Query: "{query}"

Text Scraped from: {url}
--- START SCRAPED TEXT ---
{scraped_text}
--- END SCRAPED TEXT ---

Instruction: Based *only* on the 'SCRAPED TEXT' above, determine if you can answer the 'Original User Query'.

- If the scraped text directly answers the query, respond with "Final Answer:" followed by your answer.
- If the scraped text is insufficient or irrelevant, respond *only* with: "Insufficient context"

Important:
- Use only information from the scraped text, not prior knowledge.
- Do not infer information not explicitly stated in the text.
- If the query asks for specific details missing from the text, it is insufficient.

Example 1:
Query: "What is the capital of France?" 
Text: "France is a country in Europe known for its cuisine and landmarks like the Eiffel Tower."
Response: "Insufficient context"

Example 2:
Query: "When was the iPhone 15 Pro Max released?" 
Text: "The iPhone 7 was released in 2016 with no headphone jack."
Response: "Insufficient context"
"""

# Prompt template for summarizing why the search process failed to find an answer
FAILURE_SUMMARY_PROMPT_TEMPLATE = """
Original User Query: "{query}"

I attempted to answer by scraping these URLs, but none provided sufficient context:
{tried_urls_list}

Provide a brief (1-2 sentence) explanation for why finding a direct answer might have been difficult.

Possible reasons:
- Query too broad or vague (lacks specificity)
- Query too specific or niche (requires rare/detailed data)
- Query about a very recent event (information not widely available)
- URLs scraped seem unrelated to the query
- Other reasons (specify)

Please identify which reason(s) likely apply.
"""

# For testing this file directly
if __name__ == "__main__":
    def print_example(title, template, **kwargs):
        """Helper function to print a template example with formatting"""
        print(f"\n{title}:")
        print(template)
        print("\n   Example Formatted:")
        print(template.format(**kwargs))

    print("--- Prompt Templates ---")
    
    example_query = "What is the capital of France?"
    example_url = "https://example.com/france_info"
    example_text = "France is a country in Europe. It is known for its cuisine and landmarks like the Eiffel Tower."
    example_urls = ["https://example.com/page1", "https://anothersite.org/article", "https://randomblog.net/post"]
    
    print_example(
        "1. Sufficiency Check Prompt Template",
        SUFFICIENCY_CHECK_PROMPT_TEMPLATE,
        query=example_query,
        url=example_url,
        scraped_text=example_text
    )
    
    print_example(
        "2. Failure Summary Prompt Template",
        FAILURE_SUMMARY_PROMPT_TEMPLATE,
        query=example_query,
        tried_urls_list="\n".join([f"- {u}" for u in example_urls])
    )
    
    print("\n--- End Prompt Templates ---")




#---------------------------------------------------------------------------------------------------------------
# # prompts.py

# # Prompt template used after scraping a single web page.
# # It asks the LLM to determine if the scraped text is sufficient to answer the original query.
# SUFFICIENCY_CHECK_PROMPT_TEMPLATE = """
# Original User Query: "{query}"

# Text Scraped from: {url}
# --- START SCRAPED TEXT ---
# {scraped_text}
# --- END SCRAPED TEXT ---

# Instruction: Based *only* on the 'SCRAPED TEXT' provided above, determine if you can formulate a comprehensive and accurate answer to the 'Original User Query'.

# - If the scraped text directly and sufficiently answers the query, provide the final answer directly, starting your response with "Final Answer:". Do not add any preamble or explanation before "Final Answer:".
# - If the scraped text is insufficient, irrelevant, or does not directly address the query, respond *only* with the exact phrase: "Insufficient context"

# Important:
# - Do not use any prior knowledge or information not present in the scraped text.
# - Do not infer or assume information that is not explicitly stated in the scraped text.
# - If the query is about a specific detail and the text does not provide that detail, it is insufficient.

# Example:
# Suppose the query is "What is the capital of France?" and the scraped text is "France is a country in Europe known for its cuisine and landmarks like the Eiffel Tower."
# - Since the text does not mention the capital, you should respond with "Insufficient context"

# Another example:
# If the query is "At what date did the iPhone 15 Pro Max released?" and the scraped text is "The iPhone 7 was released in 2016 with no headphone jack.", you should respond with "Insufficient context" because the text is irrelevant to the iPhone 15 Pro Max.
# """

# # Prompt template used when the agent fails to find a sufficient answer
# # after trying the maximum number of URLs. Asks the LLM to provide a brief summary.
# FAILURE_SUMMARY_PROMPT_TEMPLATE = """
# Original User Query: "{query}"

# I attempted to answer the query by scraping the following URLs, but none provided sufficient context individually according to my analysis process:
# {tried_urls_list}

# Based on the original query and the list of URLs attempted, provide a brief (1-2 sentence) possible explanation for why finding a direct answer might have been difficult.

# Consider the following possible reasons:
# - The query is too broad or vague (e.g., lacks specificity for a clear answer).
# - The query is too specific or niche (e.g., requires rare or detailed data).
# - The query is about a very recent event, and information might not be widely available yet.
# - The URLs scraped seem unrelated to the query (e.g., discuss different topics).
# - Other reasons (specify).

# Please specify which of these reasons might apply or suggest another reason.
# """

# # --- Example Usage (for testing this file directly) ---
# if __name__ == "__main__":
#     print("--- Prompt Templates ---")

#     print("\n1. Sufficiency Check Prompt Template:")
#     print(SUFFICIENCY_CHECK_PROMPT_TEMPLATE)
#     # Example formatting:
#     print("\n   Example Formatted Sufficiency Check:")
#     example_query = "What is the capital of France?"
#     example_url = "https://example.com/france_info"
#     example_text = "France is a country in Europe. It is known for its cuisine and landmarks like the Eiffel Tower. The main language is French."
#     formatted_sufficiency = SUFFICIENCY_CHECK_PROMPT_TEMPLATE.format(
#         query=example_query,
#         url=example_url,
#         scraped_text=example_text
#     )
#     print(formatted_sufficiency)

#     print("\n2. Failure Summary Prompt Template:")
#     print(FAILURE_SUMMARY_PROMPT_TEMPLATE)
#     # Example formatting:
#     print("\n   Example Formatted Failure Summary:")
#     example_urls = ["https://example.com/page1", "https://anothersite.org/article_snippet", "https://randomblog.net/post"]
#     formatted_failure = FAILURE_SUMMARY_PROMPT_TEMPLATE.format(
#         query=example_query,
#         tried_urls_list="\n".join([f"- {u}" for u in example_urls])
#     )
#     print(formatted_failure)

#     print("\n--- End Prompt Templates ---")