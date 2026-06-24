from langchain_ollama import ChatOllama

from app.config import settings


def get_llm() -> ChatOllama:
    return ChatOllama(
        model=settings.llm_model,
        temperature=0,
    )