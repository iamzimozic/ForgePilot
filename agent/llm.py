from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_MODEL

def get_llm():
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0,
        max_retries=0
    )
