import os
from pathlib import Path

from app.config import settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from app.embeddings import get_embeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone


def load_documents(data_dir: str) -> list:
    documents = []

    for pdf_file in Path(data_dir).glob("*.pdf"):
        print(f"Loading: {pdf_file.name}")

        loader = PyPDFLoader(str(pdf_file))
        documents.extend(loader.load())

    return documents


def split_documents(documents: list) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    chunks = splitter.split_documents(documents)
    return [c for c in chunks if len(c.page_content.strip()) >= 150]


def create_vector_store(chunks: list) -> None:
    embeddings = get_embeddings()

    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = pc.Index(settings.pinecone_index)

    stats = index.describe_index_stats()
    if stats.total_vector_count > 0:
        index.delete(delete_all=True)

    PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=settings.pinecone_index,
        pinecone_api_key=settings.pinecone_api_key,
    )

    print("Vector database created successfully")


def main() -> None:
    print("Loading PDFs...")
    documents = load_documents(os.getenv("DATA_DIR", "data"))

    print(f"Pages loaded: {len(documents)}")

    print("Splitting documents...")
    chunks = split_documents(documents)

    print(f"Chunks created: {len(chunks)}")

    print("Creating embeddings and storing in Pinecone...")
    create_vector_store(chunks)

    print("Ingestion completed")


if __name__ == "__main__":
    main()
