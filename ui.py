from __future__ import annotations

import streamlit as st

from app.compliance_chat import (
    ChatMessage,
    generate_compliance_chat_response,
)
from app.compliance_checker import audit_draft_document
from app.config import settings
from app.document_parser import extract_text_from_uploaded_file
from app.retriever import load_vector_store


def initialise_session_state() -> None:
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []

    if "latest_audit_result" not in st.session_state:
        st.session_state["latest_audit_result"] = None

    if "latest_uploaded_filename" not in st.session_state:
        st.session_state["latest_uploaded_filename"] = None


@st.cache_resource
def get_cached_vector_store():
    return load_vector_store()


def retrieve_regulatory_context(
    query: str,
    top_k: int,
) -> str:
    vector_store = get_cached_vector_store()

    documents = vector_store.similarity_search(
        query=query,
        k=top_k,
    )

    return "\n\n".join(
        document.page_content
        for document in documents
    )


def sidebar() -> None:
    with st.sidebar:
        st.header("Configuration")

        st.write(f"LLM: {settings.llm_model}")
        st.write(f"Embedding: {settings.embedding_model}")
        st.write(f"Collection: {settings.collection_name}")
        st.write(f"Top K: {settings.top_k}")

        st.divider()

        st.header("Current Document")

        filename = st.session_state.get("latest_uploaded_filename")

        if filename:
            st.success(str(filename))
        else:
            st.info("No document audited yet.")

        st.divider()

        if st.button("Clear Chat"):
            st.session_state["chat_messages"] = []
            st.success("Chat cleared.")

        if st.button("Clear Audit Context"):
            st.session_state["latest_audit_result"] = None
            st.session_state["latest_uploaded_filename"] = None
            st.success("Audit context cleared.")

def compliance_chat_tab() -> None:
    st.subheader("Compliance Chat Assistant")

    st.caption(
        "Ask questions about APP, RG 271, or your latest uploaded audit result."
    )

    chat_messages: list[ChatMessage] = st.session_state["chat_messages"]

    messages_container = st.container()

    with messages_container:
        for message in chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    user_question = st.chat_input(
        "Ask a compliance question..."
    )

    if not user_question:
        return

    chat_messages.append(
        {
            "role": "user",
            "content": user_question,
        }
    )

    with messages_container:
        with st.chat_message("user"):
            st.markdown(user_question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                regulatory_context = retrieve_regulatory_context(
                    query=user_question,
                    top_k=settings.top_k,
                )

                answer = generate_compliance_chat_response(
                    question=user_question,
                    regulatory_context=regulatory_context,
                    chat_history=chat_messages,
                    latest_audit_result=st.session_state["latest_audit_result"],
                )

                st.markdown(answer)

    chat_messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

def audit_text_tab() -> None:
    st.subheader("Audit Pasted Document")

    draft_document = st.text_area(
        "Paste draft privacy policy, complaint policy, or business document",
        height=300,
    )

    if st.button("Audit Pasted Document"):
        if not draft_document.strip():
            st.warning("Please paste a document.")
            return

        with st.spinner("Auditing document..."):
            result = audit_draft_document(draft_document)

        st.session_state["latest_audit_result"] = result
        st.session_state["latest_uploaded_filename"] = "Pasted Text"

        st.subheader("Audit Result")
        st.text(result)


def upload_and_audit_tab() -> None:
    st.subheader("Upload Document for Audit")

    uploaded_file = st.file_uploader(
        "Upload PDF, DOCX, or TXT",
        type=["pdf", "docx", "txt"],
    )

    if uploaded_file is None:
        st.info("Upload a draft policy document to audit it against APP and RG 271.")
        return

    st.success(f"Uploaded: {uploaded_file.name}")

    if st.button("Extract and Audit Uploaded Document"):
        with st.spinner("Extracting text..."):
            extracted_text = extract_text_from_uploaded_file(
                filename=uploaded_file.name,
                file_bytes=uploaded_file.getvalue(),
            )

        if not extracted_text.strip():
            st.error("No readable text found.")
            return

        with st.expander("Preview Extracted Text"):
            st.text(extracted_text[:3000])

        with st.spinner("Auditing uploaded document..."):
            result = audit_draft_document(extracted_text)

        st.session_state["latest_audit_result"] = result
        st.session_state["latest_uploaded_filename"] = uploaded_file.name

        st.subheader("Audit Result")
        st.text(result)


def main() -> None:
    st.set_page_config(
        page_title="Compliance Auditor",
        layout="wide",
    )

    initialise_session_state()

    st.title("Australian Compliance Auditor")

    st.caption(
        "RAG-powered compliance assistant using APP Guidelines and ASIC RG 271."
    )

    sidebar()

    tab1, tab2, tab3 = st.tabs(
        [
            "Compliance Chat",
            "Audit Text",
            "Upload & Audit",
        ]
    )

    with tab1:
        compliance_chat_tab()

    with tab2:
        audit_text_tab()

    with tab3:
        upload_and_audit_tab()


if __name__ == "__main__":
    main()