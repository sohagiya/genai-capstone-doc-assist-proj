"""Streamlit UI for GenAI Document Assistant - Single Page Layout"""
import streamlit as st
import requests
from typing import Optional, List
import time

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="GenAI Document Assistant",
    page_icon="📚",
    layout="wide"
)

# Hide Streamlit deploy button
hide_deploy_button = """
<style>
.stDeployButton {display:none !important;}
button[kind="header"] {display:none !important;}
[data-testid="stToolbar"] {display:none !important;}
.viewerBadge_container__1QSob {display:none !important;}
</style>
"""
st.markdown(hide_deploy_button, unsafe_allow_html=True)


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
    """Ask a question via the API"""
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


def list_documents() -> List[dict]:
    """Get list of all uploaded documents"""
    try:
        response = requests.get(f"{API_BASE_URL}/list-documents")
        response.raise_for_status()
        return response.json().get("documents", [])
    except Exception as e:
        st.error(f"Failed to list documents: {str(e)}")
        return []


def delete_document(doc_id: str) -> bool:
    """Delete a specific document"""
    try:
        response = requests.delete(f"{API_BASE_URL}/delete-document/{doc_id}")
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Failed to delete document: {str(e)}")
        return False


def clear_all_documents() -> bool:
    """Clear all documents"""
    try:
        response = requests.post(f"{API_BASE_URL}/clear-all-documents")
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Failed to clear documents: {str(e)}")
        return False


def get_health_status() -> Optional[dict]:
    """Get API health status"""
    try:
        response = requests.get(f"{API_BASE_URL}/health-check")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# Initialize session state
if 'documents' not in st.session_state:
    st.session_state.documents = []
if 'last_answer' not in st.session_state:
    st.session_state.last_answer = None


# Main UI
st.title("📚 GenAI Document Assistant")
st.markdown("Upload documents and ask questions using AI-powered search and reasoning")

# Sidebar - Settings and Controls
with st.sidebar:
    st.header("⚙️ Settings")

    # Query settings
    st.subheader("Query Settings")
    top_k = st.slider("Number of sources", 1, 10, 5, help="How many document chunks to retrieve")
    answer_style = st.selectbox(
        "Answer style",
        ["concise", "detailed", "bullet"],
        index=0,
        help="How the answer should be formatted"
    )

    st.markdown("---")

    # System controls
    st.subheader("🛠️ System Controls")

    if st.button("🔄 Refresh Documents"):
        st.session_state.documents = list_documents()
        st.rerun()

    if st.button("🗑️ Clear All Documents", help="Remove all uploaded documents"):
        if clear_all_documents():
            st.success("All documents cleared!")
            st.session_state.documents = []
            time.sleep(1)
            st.rerun()

    # Health check
    if st.button("💊 Check API Health"):
        health = get_health_status()
        if health and health.get("status") == "healthy":
            st.success("✅ API is healthy")
            stats = health.get("collection_stats", {})
            st.info(f"Total chunks: {stats.get('total_chunks', 0)}")
        else:
            st.error("❌ API is unhealthy")

    st.markdown("---")
    st.caption("GenAI Document Assistant v1.0")


# Main content - Single page layout
col1, col2 = st.columns([1, 1])

# Left Column - Document Upload & Management
with col1:
    st.header("📤 Upload & Manage Documents")

    # Upload section
    st.subheader("Upload New Document")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "txt", "csv", "xlsx", "docx"],
        help="Supported: PDF, TXT, CSV, XLSX, DOCX (max 10MB)",
        key="file_uploader"
    )

    if uploaded_file:
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.info(f"📄 {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
        with col_b:
            if st.button("⬆️ Upload", type="primary", use_container_width=True):
                with st.spinner("Processing..."):
                    result = upload_document(uploaded_file)
                    if result:
                        if "already exists" in result.get("message", "").lower():
                            st.warning(f"⚠️ Document already exists")
                        else:
                            st.success(f"✅ Uploaded successfully!")
                            st.info(f"Chunks created: {result['num_chunks']}")
                            # Refresh document list
                            time.sleep(0.5)
                            st.session_state.documents = list_documents()
                            st.rerun()

    st.markdown("---")

    # Document list section
    st.subheader("📚 Current Documents")

    # Refresh documents
    st.session_state.documents = list_documents()

    if st.session_state.documents:
        st.info(f"**{len(st.session_state.documents)} document(s) in knowledge base**")

        for doc in st.session_state.documents:
            with st.container():
                col_doc, col_btn = st.columns([4, 1])

                with col_doc:
                    st.markdown(f"**{doc['filename']}**")
                    st.caption(f"Type: {doc['file_type']} | Chunks: {doc['chunks']} | ID: {doc['doc_id'][:8]}...")

                with col_btn:
                    if st.button("🗑️", key=f"del_{doc['doc_id']}", help="Delete this document"):
                        if delete_document(doc['doc_id']):
                            st.success("Deleted!")
                            time.sleep(0.5)
                            st.session_state.documents = list_documents()
                            st.rerun()

                st.markdown("---")
    else:
        st.warning("📭 No documents uploaded yet. Upload a document to get started!")


# Right Column - Ask Questions
with col2:
    st.header("❓ Ask Questions")

    # Show current context
    if st.session_state.documents:
        st.success(f"✅ Ready to answer questions from **{len(st.session_state.documents)} document(s)**")
    else:
        st.error("❌ No documents available. Please upload documents first!")

    # Question input
    question = st.text_area(
        "Your question",
        height=120,
        placeholder="What is the main topic discussed in the documents?",
        help="Ask anything about your uploaded documents",
        key="question_input"
    )

    # Ask button
    if st.button("🤖 Ask Question", type="primary", disabled=not question or not st.session_state.documents, use_container_width=True):
        with st.spinner("🔍 Thinking..."):
            result = ask_question(question, top_k, answer_style)

            if result:
                st.session_state.last_answer = result
                st.rerun()

    # Display last answer
    if st.session_state.last_answer:
        result = st.session_state.last_answer

        st.markdown("---")
        st.markdown("### 💡 Answer")

        # Confidence indicator
        confidence = result.get("confidence", "medium")
        confidence_emoji = {
            "high": "🟢",
            "medium": "🟡",
            "low": "🔴"
        }.get(confidence, "⚪")

        col_conf, col_clear = st.columns([4, 1])
        with col_conf:
            st.markdown(f"**Confidence:** {confidence_emoji} {confidence.upper()}")
        with col_clear:
            if st.button("Clear Answer", key="clear_answer"):
                st.session_state.last_answer = None
                st.rerun()

        # Answer text
        st.markdown(result["answer"])

        # Safety flags
        if result.get("safety_flags"):
            st.warning(f"⚠️ Safety flags: {', '.join(result['safety_flags'])}")

        # Citations - Group by document
        if result.get("citations"):
            st.markdown("### 📎 Sources Used")

            # Group citations by filename
            docs_used = {}
            for citation in result["citations"]:
                filename = citation['filename']
                if filename not in docs_used:
                    docs_used[filename] = {
                        'citations': [],
                        'doc_id': citation.get('doc_id', 'N/A')
                    }
                docs_used[filename]['citations'].append(citation)

            st.info(f"📄 **{len(docs_used)} document(s)** used | **{len(result['citations'])} chunk(s)** retrieved")

            for doc_num, (filename, doc_info) in enumerate(docs_used.items(), 1):
                citations = doc_info['citations']
                avg_score = sum(c['score'] for c in citations) / len(citations)

                with st.expander(f"Document {doc_num}: {filename} ({len(citations)} chunks, Avg: {avg_score:.1%})"):
                    st.write(f"**Filename:** {filename}")
                    st.write(f"**Document ID:** {doc_info['doc_id'][:8]}...")
                    st.write(f"**Chunks Used:** {len(citations)}")
                    st.write(f"**Average Relevance:** {avg_score:.3f}")

                    st.markdown("**Chunk Details:**")
                    for i, citation in enumerate(citations, 1):
                        st.write(f"  - Chunk {i}: Score {citation['score']:.3f}")
        else:
            st.info("ℹ️ No sources cited")

        # Debug info (collapsible)
        with st.expander("🔍 Debug Information"):
            st.json({
                "trace_id": result.get("trace_id"),
                "reasoning": result.get("reasoning"),
                "num_citations": len(result.get("citations", []))
            })


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Powered by GenAI | RAG-based Document Q&A System</p>
    <p style='font-size: 0.8em;'>💡 Tip: Upload documents on the left, ask questions on the right</p>
</div>
""", unsafe_allow_html=True)
