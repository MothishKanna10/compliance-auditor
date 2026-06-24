import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000/audit"

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

document_text = st.text_area(
    "Paste document text",
    height=300,
)

if st.button("Run Audit"):

    if not document_text.strip():
        st.warning("Please enter a document.")
        st.stop()

    with st.spinner("Running compliance audit..."):

        response = requests.post(
            API_URL,
            json={
                "document_text": document_text,
            },
            timeout=300,
        )

        if response.status_code != 200:
            st.error(
                f"API Error: {response.text}"
            )
            st.stop()

        result = response.json()

    st.subheader("Confidence")

    st.write(
        result["confidence"]
    )

    st.subheader("Audit Report")

    st.text_area(
        "",
        value=result["report"],
        height=500,
    )