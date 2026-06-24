# research_agent/config.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

load_dotenv()

OPEN_ROUTER_API = os.getenv("OPEN_ROUTER_API")
if OPEN_ROUTER_API is None:
    raise ValueError("OPEN_ROUTER_API environment variable is required")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if TAVILY_API_KEY is None:
    raise ValueError("TAVILY_API_KEY environment variable is required")

llm = ChatOpenAI(
    api_key=SecretStr(OPEN_ROUTER_API),
    base_url="https://openrouter.ai/api/v1",
    model="openai/gpt-oss-120b:free"
)

MAX_REVISIONS = 2