
"""Application configuration for Sharanika's document Q&A project."""

import os

import streamlit as st
from dotenv import load_dotenv

# Load variables from the local .env file, if present.
# On Streamlit Cloud, configure secrets in the app settings instead.
load_dotenv()


def _get_secret(name: str, default: str = "") -> str:
    """Read a setting from Streamlit secrets or environment variables."""

    # Prefer environment variables (including values loaded from .env).
    env_value = os.getenv(name)
    if env_value:
        return env_value

    # Fall back to Streamlit secrets.
    try:
        secret_value = st.secrets.get(name, default)
        return str(secret_value) if secret_value else default
    except Exception:
        # Streamlit secrets may not be configured during local development.
        return default


class Config:
    # Gemini API configuration
    GOOGLE_API_KEY = _get_secret("GOOGLE_API_KEY")
    GEMINI_MODEL = _get_secret("GEMINI_MODEL", "gemini-3.8-flash")

    # Vector database configuration
    VECTOR_STORE_TYPE = "chromadb"
    VECTOR_STORE_DIR = "vectorstore"

    # Embedding configuration
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"

    # Document processing configuration
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    DATA_DIR = "data/documents"

    # Streamlit page configuration
    PAGE_TITLE = "AI-Powered Document Q&A | Sharanika"
    PAGE_ICON = "📚"