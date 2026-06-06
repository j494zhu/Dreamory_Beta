import openai
from openai import AsyncOpenAI
from dotenv import load_dotenv 
import os 

load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-v4-flash"

_client: AsyncOpenAI | None = None

def get_client():
    global _client 
    if _client is None:
        _client = AsyncOpenAI(
            api_key=API_KEY, 
            base_url=BASE_URL
        )
    return _client