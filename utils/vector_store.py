import os
import sys
import sqlite3
import chromadb
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import numpy as np

class VectorStore:
    def __init__(self, 
                 embedding_model: str = "all-MiniLM-L6-v2",
                 persist_directory: str = "vectorstore"):
        self.embedding_model_name = embedding_model
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        self.vectorstore = None
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
    
    def create_vectorstore(self, documents: List[Document]) -> None:
        """Create a new vector store from documents."""
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name="rag_collection"
        )
    
    def load_vectorstore(self) -> bool:
        """Load existing vector store."""
        try:
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name="rag_collection"
            )
            return True
        except Exception as e:
            print(f"Error loading vector store: {str(e)}")
            return False
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add new documents to existing vector store."""
        if self.vectorstore is None:
            self.create_vectorstore(documents)
        else:
            self.vectorstore.add_documents(documents)
    
    def similarity_search(self, 
                         query: str, 
                         k: int = 4) -> List[Document]:
        """Perform similarity search and return relevant documents."""
        if self.vectorstore is None:
            return []
        
        return self.vectorstore.similarity_search(query, k=k)
    
    def similarity_search_with_score(self, 
                                   query: str, 
                                   k: int = 4) -> List[tuple]:
        """Perform similarity search with scores."""
        if self.vectorstore is None:
            return []
        
        return self.vectorstore.similarity_search_with_score(query, k=k)
    
    def delete_collection(self) -> None:
        """Delete the vector store collection."""
        if self.vectorstore is not None:
            self.vectorstore.delete_collection()
            self.vectorstore = None
    
    def get_collection_info(self) -> dict:
        """Get information about the collection."""
        if self.vectorstore is None:
            return {"status": "No collection loaded", "count": 0}
        
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            return {"status": "Collection loaded", "count": count}
        except Exception as e:

            return {"status": f"Error: {str(e)}", "count": 0}

