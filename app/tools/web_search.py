from langchain_core.tools import tool
from app.config.settings import tavily_instance


@tool
def web_search(query: str):
    """
    Search the web for travel information.
    """
    return tavily_instance.invoke({
        "query": query
    })