from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    embedding_model: str
    llm_provider:str
    embedding_provider:str
    llm_model: str
    chroma_dir: str
    collection_name: str
    chunk_size: int
    chunk_overlap: int
    top_k: int


settings = Settings(
    openai_api_key=os.getenv("OPENAI_API_KEY", ""),
    llm_provider=os.getenv("LLM_PROVIDER", "llama"),
    embedding_provider=os.getenv("EMBEDDING_PROVIDER", "huggingface"),
    embedding_model=os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
    ),
    llm_model=os.getenv(
        "LLM_MODEL",
        "llama3.2:3b",
    ),
    chroma_dir=os.getenv(
        "CHROMA_PERSIST_DIR",
        "chroma_db",
    ),
    collection_name=os.getenv(
        "CHROMA_COLLECTION_NAME",
        "compliance_rules",
    ),
    chunk_size=int(
        os.getenv(
            "CHUNK_SIZE",
            "1000",
        )   
    ),
    chunk_overlap=int(
        os.getenv(
            "CHUNK_OVERLAP",
            "150",
        )
    ),
    top_k=int(
        os.getenv(
            "TOP_K",
            "5",
        )
    ),
)