from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


def load_documents(data_dir: str) -> list:
    documents = []

    for pdf_file in Path(data_dir).glob("*.pdf"):
        print(f"Loading: {pdf_file.name}")

        loader = PyPDFLoader(str(pdf_file))
        documents.extend(loader.load())

    return documents


def split_documents(documents: list) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )

    return splitter.split_documents(documents)


def create_vector_store(chunks: list) -> None:
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="chroma_db",
        collection_name="compliance_rules",
    )

    vector_store.persist()

    print("Vector database created successfully")


def main() -> None:
    print("Loading PDFs...")
    documents = load_documents("data")

    print(f"Pages loaded: {len(documents)}")

    print("Splitting documents...")
    chunks = split_documents(documents)

    print(f"Chunks created: {len(chunks)}")

    print("Creating local embeddings and storing in ChromaDB...")
    create_vector_store(chunks)

    print("Ingestion completed")


if __name__ == "__main__":
    main()