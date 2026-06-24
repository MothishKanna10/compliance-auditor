import requests
import streamlit as st


BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Compliance Auditor",
    page_icon="⚖️",
)

st.title("⚖️ AI Compliance Auditor")

st.markdown(
    """
Audit documents against:

- Australian Privacy Principles (APP)
- ASIC RG271
"""
)

upload_tab, paste_tab = st.tabs(["Upload File", "Paste Text"])

with upload_tab:
    uploaded_file = st.file_uploader(
        "Upload a document (PDF, DOCX, or TXT)",
        type=["pdf", "docx", "txt"],
    )

    if st.button("Run Audit", key="audit_file"):
        if uploaded_file is None:
            st.warning("Please upload a file.")
            st.stop()

        with st.spinner("Running compliance audit..."):
            response = requests.post(
                f"{BASE_URL}/audit/file",
                files={
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type,
                    )
                },
                timeout=300,
            )

        if response.status_code != 200:
            st.error(f"API Error: {response.json().get('detail', response.text)}")
            st.stop()

        result = response.json()

        st.subheader("Confidence")
        st.write(result["confidence"])

        st.subheader("Audit Report")
        st.text_area("", value=result["report"], height=500, key="report_file")

with paste_tab:
    document_text = st.text_area(
        "Paste document text",
        height=300,
    )

    if st.button("Run Audit", key="audit_text"):
        if not document_text.strip():
            st.warning("Please enter a document.")
            st.stop()

        with st.spinner("Running compliance audit..."):
            response = requests.post(
                f"{BASE_URL}/audit",
                json={"document_text": document_text},
                timeout=300,
            )

        if response.status_code != 200:
            st.error(f"API Error: {response.text}")
            st.stop()

        result = response.json()

        st.subheader("Confidence")
        st.write(result["confidence"])

        st.subheader("Audit Report")
        st.text_area("", value=result["report"], height=500, key="report_text")
