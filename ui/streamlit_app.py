"""Streamlit UI for GenAI Document Assistant - Claude-like Interface"""
import streamlit as st
import requests
import time
from typing import Optional

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Page config
st.set_page_config(
    page_title="GenAI Document Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Claude-like appearance
st.markdown("""
<style>
    /* Hide Streamlit footer */
    footer {visibility: hidden;}

    /* Keep sidebar collapse button visible */
    [data-testid="collapsedControl"] {
        display: block !important;
        visibility: visible !important;
        position: fixed;
        left: 0;
        top: 0.5rem;
        z-index: 999999;
        background-color: #f7f7f8;
        border-radius: 0 8px 8px 0;
        padding: 8px 12px;
        cursor: pointer;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }

    /* Sidebar toggle icon */
    [data-testid="collapsedControl"] svg {
        color: #2e2e2e;
    }

    /* Center chat container */
    .main .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Chat message spacing and borders */
    .stChatMessage {
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }

    /* Assistant message border */
    [data-testid="stChatMessage"] {
        border: 1px solid rgba(0,0,0,0.1);
    }

    /* Chat input styling */
    .stChatInputContainer {
        border-top: 1px solid rgba(0,0,0,0.1);
        padding-top: 1rem;
    }

    /* Button hover effects */
    .stButton button:hover {
        opacity: 0.85;
        transition: opacity 0.2s;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        border-radius: 6px;
    }

    /* Hide only MainMenu, keep settings accessible */
    #MainMenu {
        visibility: visible !important;
    }

    /* Hide deploy button specifically */
    .stDeployButton {
        display: none !important;
    }

    /* Try to hide deploy with element selectors */
    [data-testid="stToolbar"] button[kind="header"] {
        display: none !important;
    }

    /* Alternative: hide first child in toolbar (usually deploy) */
    [data-testid="stToolbar"] > div > button:first-child {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# API Helper Functions
def upload_document(file) -> Optional[dict]:
    """Upload a document to the API"""
    try:
        files = {"file": (file.name, file, file.type)}
        response = requests.post(f"{API_BASE_URL}/upload-document", files=files)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Upload failed: {str(e)}")
        return None

def ask_question(question: str, top_k: int = 5, answer_style: str = "concise") -> Optional[dict]:
    """Ask a question to the API"""
    try:
        payload = {
            "question": question,
            "collection_id": "documents",
            "top_k": top_k,
            "answer_style": answer_style,
            "include_citations": True
        }
        response = requests.post(f"{API_BASE_URL}/ask-question", json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Question failed: {str(e)}")
        return None

def list_documents() -> list:
    """List all uploaded documents"""
    try:
        response = requests.get(f"{API_BASE_URL}/list-documents")
        response.raise_for_status()
        return response.json().get("documents", [])
    except Exception:
        return []

def delete_document(doc_id: str) -> bool:
    """Delete a document"""
    try:
        response = requests.delete(f"{API_BASE_URL}/delete-document/{doc_id}")
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Failed to delete: {str(e)}")
        return False

def clear_all_documents() -> bool:
    """Clear all documents"""
    try:
        response = requests.post(f"{API_BASE_URL}/clear-all-documents")
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Failed to clear: {str(e)}")
        return False

def get_data_preview(doc_id: str, num_rows: int = 100) -> Optional[dict]:
    """Get tabular data preview"""
    try:
        response = requests.get(f"{API_BASE_URL}/get-data-preview/{doc_id}?num_rows={num_rows}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to get data preview: {str(e)}")
        return None

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'documents' not in st.session_state:
    st.session_state.documents = []
if 'top_k' not in st.session_state:
    st.session_state.top_k = 5
if 'answer_style' not in st.session_state:
    st.session_state.answer_style = "concise"

# Sidebar
with st.sidebar:
    st.title("📚 Document Assistant")
    st.markdown("---")

    # Upload Section
    st.header("📤 Upload Document")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "txt", "csv", "xlsx", "docx"],
        help="Supported: PDF, TXT, CSV, XLSX, DOCX (Max 10MB)",
        label_visibility="collapsed"
    )

    if uploaded_file:
        if st.button("Upload", type="primary", use_container_width=True):
            with st.spinner("Uploading..."):
                result = upload_document(uploaded_file)
                if result:
                    if "already exists" in result.get("message", "").lower():
                        st.warning("⚠️ Document already exists")
                    else:
                        st.success("✅ Uploaded successfully!")

                        # Show upload details
                        with st.expander("📄 Upload Details", expanded=True):
                            st.write(f"**Filename:** {result.get('filename', 'N/A')}")
                            st.write(f"**Document ID:** {result.get('doc_id', 'N/A')}")
                            st.write(f"**File Type:** {result.get('file_type', 'N/A')}")
                            st.write(f"**Text Chunks:** {result.get('chunks_created', 0)}")
                            st.write(f"**Collection:** {result.get('collection_id', 'N/A')}")
                            st.caption(result.get('message', ''))

                        st.session_state.documents = list_documents()
                        time.sleep(1.5)
                        st.rerun()

    st.markdown("---")

    # Documents Section
    st.header("📁 Documents")
    st.session_state.documents = list_documents()

    if st.session_state.documents:
        st.caption(f"{len(st.session_state.documents)} document(s)")

        for doc in st.session_state.documents:
            with st.expander(f"{doc['filename'][:20]}...", expanded=False):
                st.caption(f"Type: {doc['file_type']}")
                st.caption(f"Chunks: {doc['chunks']}")

                # CSV/Excel specific buttons
                if doc['file_type'] in ['.csv', '.xlsx', '.xls']:
                    if st.button("📋 Data", key=f"btn_data_{doc['doc_id']}", use_container_width=True):
                        with st.spinner("Loading..."):
                            preview = get_data_preview(doc['doc_id'], num_rows=50)
                            if preview:
                                st.session_state[f"data_{doc['doc_id']}"] = preview
                                st.rerun()

                if st.button("🗑️ Delete", key=f"del_{doc['doc_id']}", use_container_width=True):
                    if delete_document(doc['doc_id']):
                        st.success("Deleted!")
                        st.session_state.documents = list_documents()
                        time.sleep(0.3)
                        st.rerun()
    else:
        st.info("No documents uploaded yet")

    st.markdown("---")

    # Settings Section
    st.header("⚙️ Settings")
    st.session_state.top_k = st.slider("Sources", 1, 10, 5)
    st.session_state.answer_style = st.selectbox(
        "Answer style",
        ["concise", "detailed", "bullet"],
        index=0
    )

    st.markdown("---")

    # Actions
    if st.button("🔄 Refresh", use_container_width=True):
        st.session_state.documents = list_documents()
        st.rerun()

    if st.button("🗑️ Clear All", use_container_width=True):
        if clear_all_documents():
            st.success("Cleared!")
            st.session_state.documents = []
            st.session_state.chat_history = []
            time.sleep(0.5)
            st.rerun()

    if st.button("💬 New Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# Main Chat Area
st.title("💬 Chat")

# Display chat history (last 10 messages)
chat_display = st.session_state.chat_history[-10:] if len(st.session_state.chat_history) > 10 else st.session_state.chat_history

for message in chat_display:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show citations if present
        if message["role"] == "assistant" and "citations" in message:
            with st.expander("📚 Sources"):
                for i, citation in enumerate(message["citations"][:3], 1):
                    st.caption(f"{i}. **{citation['filename']}** (Score: {citation['score']:.3f})")

# Display data previews if available
for doc in st.session_state.documents:
    if doc['file_type'] in ['.csv', '.xlsx', '.xls']:
        # Data Preview
        if f"data_{doc['doc_id']}" in st.session_state:
            preview_data = st.session_state[f"data_{doc['doc_id']}"]
            if isinstance(preview_data, dict):
                with st.expander(f"📋 Data: {doc['filename']}", expanded=False):
                    st.write(f"**{preview_data['preview_rows']} of {preview_data['total_rows']} rows**")

                    # Column stats
                    st.subheader("Column Information")
                    for col_info in preview_data.get('columns', [])[:5]:
                        st.markdown(f"**{col_info['name']}** ({col_info['dtype']})")
                        if 'stats' in col_info:
                            stats = col_info['stats']
                            st.caption(f"Range: {stats.get('min')} - {stats.get('max')}, Mean: {stats.get('mean', 0):.2f}")
                        elif 'unique_values' in col_info:
                            st.caption(f"Unique: {col_info['unique_values']}")

                    # Data table
                    st.subheader("Data Table")
                    import pandas as pd
                    df = pd.DataFrame(preview_data.get('data', []))
                    st.dataframe(df, use_container_width=True, height=300)

# Chat input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = ask_question(
                prompt,
                top_k=st.session_state.top_k,
                answer_style=st.session_state.answer_style
            )

            if response:
                answer = response.get("answer", "No answer available")
                citations = response.get("citations", [])

                # Display answer
                st.markdown(answer)

                # Display citations
                if citations:
                    with st.expander("📚 Sources"):
                        # Group citations by document
                        docs_cited = {}
                        for citation in citations:
                            filename = citation.get('filename', 'Unknown')
                            if filename not in docs_cited:
                                docs_cited[filename] = []
                            docs_cited[filename].append(citation)

                        for i, (filename, cites) in enumerate(docs_cited.items(), 1):
                            st.caption(f"{i}. **{filename}** ({len(cites)} chunk{'s' if len(cites) > 1 else ''})")

                # Add assistant message to chat history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer,
                    "citations": citations
                })
            else:
                error_msg = "Sorry, I couldn't process your question. Please try again."
                st.error(error_msg)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_msg
                })

    # Rerun to update chat display
    st.rerun()

# Welcome message if no chat history
if not st.session_state.chat_history:
    st.markdown("""
    ### Welcome to GenAI Document Assistant! 👋

    I can help you:
    - 📄 **Analyze documents** (PDF, TXT, CSV, Excel, DOCX)
    - 💬 **Answer questions** about your uploaded files
    - 📋 **Preview data** with statistics (for CSV/Excel)

    **Get started:**
    1. Upload a document using the sidebar
    2. Ask me questions about it!

    **Example questions:**
    - "Summarize this document"
    - "How many rows are in the CSV file?"
    - "What are the key findings?"
    """)
