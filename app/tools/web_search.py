from langchain_core.tools import tool
from app.config.settings import tavily_instance


@tool
def web_search(query: str) -> str:
    """
    Search the web for travel information using Tavily.
    This is the ONLY search tool available. Always use this tool for any web search.
    Do NOT use brave_search, google_search, or any other search tool — they do not exist.
    """
    return tavily_instance.invoke({
        "query": query
    })