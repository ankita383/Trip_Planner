import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch

# Load environment variables from .env
load_dotenv()

# GROQ LLM for Supervisor
llm_supervisor = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

# GROQ LLM for Worker Agents
llm_worker = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

# Tavily Web Search Tool
tavily_instance = TavilySearch(
    max_results=2
)