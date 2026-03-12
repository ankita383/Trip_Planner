import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch

load_dotenv()

llm_supervisor = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

llm_worker = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

tavily_instance = TavilySearch(
    max_results=2
)
