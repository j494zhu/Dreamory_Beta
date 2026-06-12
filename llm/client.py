import openai
from openai import AsyncOpenAI
from dotenv import load_dotenv 
import os 

load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-v4-flash"      # 抽取/分类用(便宜、低温、JSON)
GEN_MODEL = "deepseek-v4-pro"    # 对话生成用(质量、两段式)

_client: AsyncOpenAI | None = None

def get_client():
    global _client 
    if _client is None:
        _client = AsyncOpenAI(
            api_key=API_KEY, 
            base_url=BASE_URL
        )
    return _client