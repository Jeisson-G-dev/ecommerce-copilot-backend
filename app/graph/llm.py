from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import config

# Gemini LLM desde LangChain
llm = ChatGoogleGenerativeAI(
    model=config.GEMINI_MODEL,
    temperature=0
)