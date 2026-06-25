import requests
import streamlit as st

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Compliance Auditor",
    page_icon="⚖️",
    layout="wide",
)

# --- Sidebar ---
with st.sidebar:
    st.image("https://www.oaic.gov.au/assets/images/oaic-logo.svg", width=120)
    st.markdown("## ⚖️ AI Compliance Auditor")
    st.markdown("---")
    st.markdown("### What this tool checks")
    st.markdown("""
- 🔵 **APP 1** — Privacy policy transparency
- 🔵 **APP 5** — Collection notice obligations
- 🔵 **APP 6** — Use & disclosure of personal information
- 🔵 **APP 11** — Security of personal information
- 🔵 **APP 12** — Access to personal information
- 🔵 **APP 13** — Correction of personal information
- 🔵 **ASIC RG 271** — Internal dispute resolution
""")
    st.markdown("---")
    st.markdown("### How to use")
    st.markdown("""
1. Upload a PDF, DOCX, or TXT file **or** paste text directly
2. Click **Run Audit**
3. Review the findings
4. Ask follow-up questions in the chat
""")
    st.markdown("---")
    st.caption("Powered by GPT-4o-mini · ChromaDB · LangGraph")

# --- Session state ---
if "report" not in st.session_state:
    st.session_state.report = None
if "confidence" not in st.session_state:
    st.session_state.confidence = None
if "messages" not in st.session_state:
    st.session_state.messages = []


def run_audit_from_response(response: requests.Response) -> None:
    result = response.json()
    st.session_state.report = result["report"]
    st.session_state.confidence = result["confidence"]
    st.session_state.messages = []


def confidence_badge(confidence: str) -> None:
    colours = {"High": "#28a745", "Medium": "#fd7e14", "Low": "#dc3545"}
    colour = colours.get(confidence, "#6c757d")
    st.markdown(
        f"""
        <div style="display:inline-block; background-color:{colour};
        color:white; padding:6px 18px; border-radius:20px;
        font-weight:bold; font-size:16px;">
        {confidence} Confidence
        </div>
        """,
        unsafe_allow_html=True,
    )


# --- Header ---
st.markdown("# ⚖️ AI Compliance Auditor")
st.markdown("Automatically audit documents against **Australian Privacy Principles (APP)** and **ASIC RG 271**.")
st.markdown("---")

# --- Upload / Paste tabs ---
upload_tab, paste_tab = st.tabs(["📂 Upload File", "📋 Paste Text"])

with upload_tab:
    uploaded_file = st.file_uploader(
        "Upload a policy document",
        type=["pdf", "docx", "txt"],
        help="Supports PDF, Word documents, and plain text files.",
    )

    if st.button("🔍 Run Audit", key="audit_file", type="primary", use_container_width=True):
        if uploaded_file is None:
            st.warning("Please upload a file before running the audit.")
            st.stop()

        with st.spinner("⏳ Analysing document against regulatory requirements..."):
            response = requests.post(
                f"{BASE_URL}/audit/file",
                files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                timeout=300,
            )

        if response.status_code != 200:
            st.error(f"❌ Error: {response.json().get('detail', response.text)}")
            st.stop()

        run_audit_from_response(response)
        st.success("✅ Audit complete!")

with paste_tab:
    document_text = st.text_area(
        "Paste your document text below",
        height=250,
        placeholder="Paste the text of your privacy policy or compliance document here...",
    )

    if st.button("🔍 Run Audit", key="audit_text", type="primary", use_container_width=True):
        if not document_text.strip():
            st.warning("Please enter document text before running the audit.")
            st.stop()

        with st.spinner("⏳ Analysing document against regulatory requirements..."):
            response = requests.post(
                f"{BASE_URL}/audit",
                json={"document_text": document_text},
                timeout=300,
            )

        if response.status_code != 200:
            st.error(f"❌ Error: {response.text}")
            st.stop()

        run_audit_from_response(response)
        st.success("✅ Audit complete!")


# --- Audit results ---
if st.session_state.report:
    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("## 📋 Audit Report")
    with col2:
        st.markdown("**Overall Confidence**")
        confidence_badge(st.session_state.confidence)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(
            f"<pre style='white-space: pre-wrap; font-size: 14px; line-height: 1.6;'>{st.session_state.report}</pre>",
            unsafe_allow_html=True,
        )

    st.download_button(
        label="⬇️ Download Report",
        data=st.session_state.report,
        file_name="compliance_audit_report.txt",
        mime="text/plain",
    )

    # --- Chat ---
    st.markdown("---")
    st.markdown("## 💬 Ask About This Report")
    st.caption("Ask follow-up questions about the findings, regulations, or recommendations. Chat resets when you run a new audit.")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    question = st.chat_input("e.g. Why is finding 2 High severity? What does APP 6 require?")

    if question:
        st.session_state.messages.append({"role": "user", "content": question})

        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                chat_response = requests.post(
                    f"{BASE_URL}/chat",
                    json={
                        "report": st.session_state.report,
                        "messages": [
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages[:-1]
                        ],
                        "question": question,
                    },
                    timeout=60,
                )

            answer = (
                chat_response.json()["answer"]
                if chat_response.status_code == 200
                else "Sorry, something went wrong. Please try again."
            )
            st.write(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})
