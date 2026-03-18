import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch

load_dotenv()

llm_supervisor = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

llm_worker = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

tavily_instance = TavilySearch(
    max_results=2
)
