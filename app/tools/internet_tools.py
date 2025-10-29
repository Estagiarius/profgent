import requests
from bs4 import BeautifulSoup
from app.core.tools.tool_decorator import tool

@tool
def search_internet(query: str) -> str:
    """
    Performs a web search for a given query and returns a summary of the top result.
    """
    try:
        # For this example, we'll use DuckDuckGo as the search engine.
        # A real implementation might use a dedicated search API (e.g., Tavily, Serper).
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        url = f"https://html.duckduckgo.com/html/?q={query}"

        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status() # Raise an exception for bad status codes

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract snippets from DuckDuckGo's HTML results
        snippets = soup.find_all('a', class_='result__a')

        if not snippets:
            return "No search results found."

        # For simplicity, we'll just summarize the first few snippets.
        summary = ""
        for i, snippet in enumerate(snippets[:3]): # Get top 3 results
            summary += f"Result {i+1}: {snippet.get_text(strip=True)}\n"

        return summary if summary else "Could not extract a summary from the search results."

    except requests.RequestException as e:
        return f"Error during web search: {e}"
    except Exception as e:
        return f"An unexpected error occurred during the search: {e}"
