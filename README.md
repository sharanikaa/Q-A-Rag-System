# AI-Powered Document Q&A System

**Student:** Sharanika  
**Institution:** Mohan Babu University  
**Department:** AIM

A document question-answering application built with Streamlit, Google Gemini, ChromaDB, and LangChain. Upload PDF, DOCX, or TXT files, index their contents, and ask questions in natural language. Answers include source excerpts so you can check the supporting material.

> **Attribution:** This is a customized student version of an existing Q&A RAG project supplied to the student. See [ATTRIBUTION.md](ATTRIBUTION.md) for the source credit and reuse notes. The original license was not present in the supplied archive; confirm permission before redistribution.

## Features in this customized version

- A redesigned dashboard with student/project branding and status cards.
- PDF, DOCX, and TXT upload, with a 10 MB per-file limit.
- Retrieval-augmented question answering using Gemini and a persistent ChromaDB index.
- Source excerpts and optional retrieved-context display.
- Timestamped conversation view.
- Searchable history explorer for questions and answers.
- Export chat history as Markdown or JSON.
- Clear chat history separately from resetting the knowledge-base index.
- API-key configuration through `.env` or Streamlit secrets; keys are not hard-coded in source files.

## Requirements

- Python 3.10 or 3.11 is recommended for compatibility with the project's dependency stack.
- A Google Gemini API key from Google AI Studio.
- Internet access for API calls and initial model/dependency downloads.

## Setup on Windows

Open Command Prompt or PowerShell in the project folder.

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

Open `.env` in a text editor and replace `your_google_gemini_api_key_here` with your own API key. Do not share this key or commit `.env` to Git.

Run the application:

```powershell
streamlit run app.py
```

Streamlit will print a local URL, usually `http://localhost:8501`. Open it in your browser.

## Setup on macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Add your API key to `.env`, then run:

```bash
streamlit run app.py
```

## How to use

1. Start the app and add PDF, DOCX, or TXT documents from the sidebar.
2. Click **Process selected files** and wait for indexing to finish.
3. Type a question in **Ask your documents** and click **Ask question**.
4. Review the answer and expand **Sources** to inspect the excerpts used.
5. Search prior questions in **History explorer**.
6. Export the conversation from the sidebar if you want to keep a copy.
7. Use **Clear chat history** to remove the current conversation, or **Reset index** to remove the searchable vector index. These are separate actions.

## Project structure

```text
app.py                  Streamlit interface and chat history
config.py               Environment and application settings
utils/document_processor.py  Document extraction and chunking
utils/vector_store.py   ChromaDB vector-store wrapper
utils/rag_chain.py      Retrieval and Gemini answer generation
requirements.txt        Python dependencies
.env.example            API-key configuration template
ATTRIBUTION.md          Source credit and reuse notes
```

## Chat-history scope and privacy

Chat history is held in Streamlit session state. It remains available during the active app session and can be exported, but it is not automatically saved as a permanent server-side conversation archive. Do not upload confidential documents to a deployment unless you are authorized to do so. Uploaded files and the vector index are stored locally in the project directories.

## Troubleshooting

- **API key warning:** Check that `.env` is in the same folder as `app.py`, that the variable is named `GOOGLE_API_KEY`, and that you restarted Streamlit.
- **Dependency installation errors:** Use Python 3.10/3.11 and install in a fresh virtual environment. Some dependencies in the original project may need version adjustments depending on your platform.
- **No answer or no sources:** Confirm that documents were processed successfully and contain selectable/readable text.
- **Reset index:** Use the sidebar reset control if the local vector index becomes inconsistent, then process your documents again.

## Academic note

Be prepared to explain the document-ingestion, chunking, embedding, similarity-search, and answer-generation stages. Clearly identify which parts were adapted from the supplied project and which changes you made. Follow your instructor's citation and collaboration requirements.
