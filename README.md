# 🧠 Q&A RAG System

> A grounded Retrieval-Augmented Generation system that retrieves relevant evidence, reranks it, and generates cited answers from a controlled knowledge base.

## ✨ Features

* 🔎 **Hybrid Retrieval** — Vector Search + BM25-style Keyword Search
* 🔀 **RRF Fusion** — Combines semantic and lexical rankings
* 🎯 **FlashRank Reranking** — Improves retrieved context relevance
* 🛡️ **Grounded Generation** — Answers only from retrieved evidence
* 📚 **Citations** — References document, page, and section
* 📊 **Confidence Scoring** — Estimates retrieval confidence
* 🚫 **Safe Fallback** — Refuses unsupported/out-of-scope questions
* 🐳 **Dockerized** — Frontend, backend, and database run as containers

## 🏗️ Architecture

```text
User Query
    ↓
Vector Search + Keyword Search
    ↓
Reciprocal Rank Fusion (RRF)
    ↓
FlashRank Reranking
    ↓
Context Filtering
    ↓
Evidence & Confidence Check
    ↓
Grounded Answer + Citations
```

## 🧰 Tech Stack

**Frontend:** React, TypeScript, Vite, Tailwind CSS

**Backend:** Python, FastAPI, SQLAlchemy

**Database:** PostgreSQL, pgvector

**Retrieval:** Vector Search, BM25, RRF

**Reranking:** FlashRank

**Infrastructure:** Docker, Docker Compose

## 📁 Project Structure
