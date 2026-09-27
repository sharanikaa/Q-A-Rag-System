"""AI-Powered Document Q&A System — student-customized interface."""
import json
import os
from datetime import datetime
from io import BytesIO

import streamlit as st

from config import Config
from utils.document_processor import DocumentProcessor
from utils.vector_store import VectorStore
from utils.rag_chain import RAGChain

st.set_page_config(page_title=Config.PAGE_TITLE, page_icon=Config.PAGE_ICON, layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1450px; }
.hero { padding: 1.65rem 1.8rem; border-radius: 22px; margin-bottom: 1.3rem;
        background: linear-gradient(120deg, #14213d 0%, #243b67 52%, #4d5fa8 100%); color: white; }
.hero h1 { font-family: 'Manrope', sans-serif; color: white; font-size: clamp(1.7rem, 3vw, 2.5rem); margin: .2rem 0 .5rem; }
.hero p { color: #e4eaf8; font-size: 1rem; margin-bottom: .7rem; }
.eyebrow { text-transform: uppercase; letter-spacing: .14em; font-size: .72rem; font-weight: 700; color: #c7d2fe; }
.metric-card { border: 1px solid rgba(128,140,170,.25); border-radius: 15px; padding: 1rem 1.1rem; background: var(--secondary-background-color); }
.metric-label { font-size: .78rem; color: var(--text-color); opacity: .72; }
.metric-value { font-family: 'Manrope', sans-serif; font-size: 1.45rem; font-weight: 800; margin-top: .2rem; }
.section-title { font-family: 'Manrope', sans-serif; font-size: 1.15rem; font-weight: 800; margin: .3rem 0 .8rem; }
div[data-testid="stChatMessage"] { border: 1px solid rgba(128,140,170,.18); border-radius: 15px; padding: .85rem 1rem; }
section[data-testid="stSidebar"] { border-right: 1px solid rgba(128,140,170,.2); }
.stButton button, .stDownloadButton button { border-radius: 10px; font-weight: 600; }
.small-muted { opacity: .72; font-size: .82rem; }
</style>
""", unsafe_allow_html=True)

# Session state keeps each browser session's conversation private and separate.
def init_state():
    defaults = {
        "vectorstore": None,
        "rag_chain": None,
        "chat_history": [],
        "documents_processed": False,
        "processed_filenames": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_state()


def initialize_components():
    if st.session_state.vectorstore is None:
        st.session_state.vectorstore = VectorStore(
            embedding_model=Config.EMBEDDING_MODEL,
            persist_directory=Config.VECTOR_STORE_DIR,
        )
        # Reconnect to an existing persistent collection after a page rerun.
        st.session_state.vectorstore.load_vectorstore()
        try:
            st.session_state.documents_processed = st.session_state.vectorstore.get_collection_info().get("count", 0) > 0
        except Exception:
            st.session_state.documents_processed = False
    if st.session_state.rag_chain is None:
        st.session_state.rag_chain = RAGChain(st.session_state.vectorstore)


def process_documents(uploaded_files):
    try:
        with st.spinner("Reading files and building the searchable knowledge base…"):
            os.makedirs(Config.DATA_DIR, exist_ok=True)
            file_paths = []
            for uploaded_file in uploaded_files:
                safe_name = os.path.basename(uploaded_file.name)
                file_path = os.path.join(Config.DATA_DIR, safe_name)
                with open(file_path, "wb") as target:
                    target.write(uploaded_file.getbuffer())
                file_paths.append(file_path)

            processor = DocumentProcessor(
                chunk_size=Config.CHUNK_SIZE,
                chunk_overlap=Config.CHUNK_OVERLAP,
            )
            documents = processor.process_multiple_documents(file_paths)
            if not documents:
                st.error("No readable text was found. Check that the files are valid PDFs, DOCX, or TXT documents.")
                return

            st.session_state.vectorstore.add_documents(documents)
            st.session_state.documents_processed = True
            st.session_state.processed_filenames = sorted(
                set(st.session_state.processed_filenames).union(os.path.basename(p) for p in file_paths)
            )
            st.success(f"Added content from {len(file_paths)} file(s) to your knowledge base.")
    except Exception as exc:
        st.error(f"Document processing failed: {exc}")


def ask_question(question: str):
    with st.spinner("Searching your documents and preparing an answer…"):
        result = st.session_state.rag_chain.generate_answer(question.strip())
    entry = {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "question": question.strip(),
        "answer": result.get("answer", "No answer was returned."),
        "sources": result.get("sources", []),
        "context": result.get("context", ""),
    }
    st.session_state.chat_history.append(entry)


def transcript_markdown(history):
    lines = ["# AI-Powered Document Q&A — Chat Transcript", "", "Student project: Sharanika | Mohan Babu University | AIM", ""]
    for index, item in enumerate(history, 1):
        lines += [f"## Conversation {index}", f"**Time:** {item.get('timestamp', 'Unknown time')}", "", "**Question**", item["question"], "", "**Answer**", item["answer"], ""]
        if item.get("sources"):
            lines.append("**Sources:** " + ", ".join(s.get("filename", "Unknown") for s in item["sources"]))
            lines.append("")
    return "\n".join(lines)


# Sidebar: upload, system controls, and conversation tools.
with st.sidebar:
    st.markdown("## 📚 Your workspace")
    st.caption("Sharanika · AIM · Mohan Babu University")
    st.divider()
    st.markdown("### 1. Add documents")
    uploaded_files = st.file_uploader(
        "Choose PDF, DOCX, or TXT files", type=["pdf", "docx", "txt"],
        accept_multiple_files=True, help="Maximum 10 MB per file.",
    )
    if uploaded_files:
        too_large = [f.name for f in uploaded_files if f.size > 10 * 1024 * 1024]
        for filename in too_large:
            st.error(f"{filename} is over the 10 MB limit and will be skipped.")
        valid_files = [f for f in uploaded_files if f.size <= 10 * 1024 * 1024]
        if st.button("⚡ Process selected files", type="primary", use_container_width=True):
            if valid_files:
                process_documents(valid_files)
            else:
                st.warning("Choose at least one file under 10 MB.")

    st.divider()
    st.markdown("### 2. Knowledge base")
    if st.session_state.vectorstore is not None:
        try:
            info = st.session_state.vectorstore.get_collection_info()
            st.metric("Indexed text chunks", info.get("count", 0))
        except Exception:
            st.caption("Index status will appear after processing documents.")
    st.caption("Supported files: PDF · DOCX · TXT")
    with st.expander("Display options"):
        show_sources = st.checkbox("Show source excerpts", value=True)
        show_context = st.checkbox("Show retrieved context", value=False)

    st.divider()
    st.markdown("### 3. Chat history")
    if st.session_state.chat_history:
        st.caption(f"{len(st.session_state.chat_history)} question(s) in this session")
        st.download_button(
            "⬇ Export transcript (.md)",
            data=transcript_markdown(st.session_state.chat_history),
            file_name="sharanika_document_qa_transcript.md",
            mime="text/markdown", use_container_width=True,
        )
        st.download_button(
            "⬇ Export data (.json)",
            data=json.dumps(st.session_state.chat_history, ensure_ascii=False, indent=2),
            file_name="sharanika_document_qa_history.json",
            mime="application/json", use_container_width=True,
        )
        if st.button("Clear chat history", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    else:
        st.caption("Your questions and answers will appear here after your first query.")

    with st.expander("Reset knowledge base", expanded=False):
        st.warning("This deletes the local searchable index. Your original uploaded files are not deleted.")
        confirm_reset = st.checkbox("I understand; reset the index")
        if st.button("Reset index", disabled=not confirm_reset, use_container_width=True):
            try:
                if st.session_state.vectorstore is not None:
                    st.session_state.vectorstore.delete_collection()
                st.session_state.vectorstore = None
                st.session_state.rag_chain = None
                st.session_state.documents_processed = False
                st.session_state.processed_filenames = []
                st.success("Knowledge base reset.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not reset the index: {exc}")

# Main page hero and lightweight status cards.
st.markdown("""
<div class="hero">
  <div class="eyebrow">Student project · AIM</div>
  <h1>AI-Powered Document Q&amp;A System</h1>
  <p>Ask questions in natural language. Get answers grounded in your own notes, reports, and documents.</p>
  <span>Built by <b>Sharanika</b> · Mohan Babu University</span>
</div>
""", unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Knowledge base</div><div class="metric-value">{"Ready" if st.session_state.documents_processed else "Not ready"}</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Questions this session</div><div class="metric-value">{len(st.session_state.chat_history)}</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Files processed this session</div><div class="metric-value">{len(st.session_state.processed_filenames)}</div></div>', unsafe_allow_html=True)

st.write("")
if not Config.GOOGLE_API_KEY:
    st.warning("Google Gemini API key is not configured. Add GOOGLE_API_KEY to your .env file, then restart the app.")
    st.code('GOOGLE_API_KEY="your_api_key_here"', language="bash")
else:
    try:
        initialize_components()
    except Exception as exc:
        st.error(f"Could not initialize the document search components: {exc}")

left, right = st.columns([1.65, 1], gap="large")
with left:
    st.markdown('<div class="section-title">💬 Ask your documents</div>', unsafe_allow_html=True)
    if not st.session_state.chat_history:
        st.info("Start by uploading and processing a document from the left sidebar. Then ask a question below.")
    with st.form("question_form", clear_on_submit=True):
        question = st.text_area(
            "Your question", placeholder="For example: Summarize the main findings in this report…",
            height=90, label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Ask question →", type="primary", use_container_width=True)
    if submitted:
        if not Config.GOOGLE_API_KEY:
            st.error("Add your Google Gemini API key before asking questions.")
        elif not question.strip():
            st.warning("Type a question first.")
        else:
            try:
                initialize_components()
                ask_question(question)
                st.rerun()
            except Exception as exc:
                st.error(f"Unable to answer this question: {exc}")

    st.markdown('<div class="section-title">🗨️ Conversation</div>', unsafe_allow_html=True)
    if st.session_state.chat_history:
        for item in st.session_state.chat_history:
            try:
                display_time = datetime.fromisoformat(item["timestamp"]).strftime("%b %d, %Y · %I:%M %p")
            except (ValueError, KeyError):
                display_time = "Earlier"
            with st.chat_message("user"):
                st.markdown(item["question"])
                st.caption(display_time)
            with st.chat_message("assistant", avatar="📚"):
                st.markdown(item["answer"])
                sources = item.get("sources", [])
                if show_sources and sources:
                    with st.expander(f"📎 Sources ({len(sources)})"):
                        for source in sources:
                            st.markdown(f"**{source.get('filename', 'Unknown source')}**")
                            st.caption(source.get("content_preview", ""))
                if show_context and item.get("context"):
                    with st.expander("Retrieved context"):
                        st.text(item["context"])
    else:
        st.markdown('<p class="small-muted">Conversation messages will stay visible while this session is open. Export the transcript from the sidebar to keep a copy.</p>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-title">🕘 History explorer</div>', unsafe_allow_html=True)
    history = st.session_state.chat_history
    if history:
        search_term = st.text_input("Search past questions and answers", placeholder="Search chat history…")
        matches = [item for item in reversed(history) if search_term.casefold() in (item.get("question", "") + " " + item.get("answer", "")).casefold()]
        st.caption(f"Showing {len(matches)} of {len(history)} conversation(s)")
        for index, item in enumerate(matches):
            label = item.get("question", "Untitled question").replace("\n", " ")
            if len(label) > 76:
                label = label[:73] + "…"
            with st.expander(f"{len(history) - history.index(item):02d}. {label}"):
                st.markdown("**Question**")
                st.write(item.get("question", ""))
                st.markdown("**Answer**")
                st.write(item.get("answer", ""))
                try:
                    st.caption(datetime.fromisoformat(item["timestamp"]).strftime("%b %d, %Y · %I:%M %p"))
                except (ValueError, KeyError):
                    pass
    else:
        st.info("No chat history yet. Your recent questions will be searchable here.")
    st.divider()
    st.markdown("**How it works**")
    st.markdown("1. Upload your study material.\n2. The app splits it into searchable text chunks.\n3. Relevant passages are retrieved for each question.\n4. Gemini drafts an answer from those passages.")
    st.caption("AI-generated answers can be incomplete. Check the cited source excerpts for important work.")

st.divider()
st.markdown('<p class="small-muted">AI-Powered Document Q&amp;A System · Sharanika · AIM, Mohan Babu University. Adapted from an existing RAG project; see ATTRIBUTION.md and README.md for credit and reuse notes.</p>', unsafe_allow_html=True)
