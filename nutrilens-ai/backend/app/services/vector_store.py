"""
NutriLens AI — ChromaDB Vector Store & BAAI/bge-small Embedding Service
Handles document embedding, indexing, and semantic similarity search for RAG.
"""
import os
import logging
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from app.core.config import settings

logger = logging.getLogger("nutrilens.vector_store")

_embedding_model_instance: Optional[SentenceTransformer] = None


def get_embedding_model() -> SentenceTransformer:
    """Lazy load the BAAI/bge-small-en-v1.5 embedding model."""
    global _embedding_model_instance
    if _embedding_model_instance is None:
        model_name = settings.EMBEDDING_MODEL  # default "BAAI/bge-small-en-v1.5"
        logger.info(f"Loading embedding model: {model_name}")
        try:
            _embedding_model_instance = SentenceTransformer(model_name)
        except Exception as e:
            logger.warning(f"Could not load {model_name} directly ({e}). Falling back to sentence-transformers/all-MiniLM-L6-v2")
            _embedding_model_instance = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model_instance


class VectorStoreService:
    """ChromaDB Service Manager for RAG semantic search."""

    def __init__(self, persist_dir: Optional[str] = None, collection_name: Optional[str] = None):
        self.persist_dir = persist_dir or settings.CHROMA_PERSIST_DIR
        self.collection_name = collection_name or settings.CHROMA_COLLECTION_NAME
        
        # Ensure persistence directory exists
        os.makedirs(self.persist_dir, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True)
        )
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate vector embeddings for a list of text strings."""
        model = get_embedding_model()
        # BGE models perform best when query/passage instructions are formatted
        embeddings = model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
    ) -> int:
        """Embed and store documents inside ChromaDB."""
        if not documents:
            return 0
        embeddings = self.embed_texts(documents)
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )
        return len(documents)

    def search(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Semantic similarity search in ChromaDB vector store."""
        count = self.collection.count()
        if count == 0:
            logger.warning("ChromaDB collection is empty! No documents returned.")
            return []

        model = get_embedding_model()
        # BGE recommended query prompt prefix
        query_embedding = model.encode([f"Represent this sentence for searching relevant passages: {query_text}"], normalize_embeddings=True).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=min(top_k, count),
            include=["documents", "metadatas", "distances"],
        )

        formatted_results = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            dists = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

            for doc, meta, dist in zip(docs, metas, dists):
                formatted_results.append({
                    "content": doc,
                    "metadata": meta,
                    "distance": float(dist),
                    "relevance_score": round(max(0.0, 1.0 - (dist / 2.0)), 4)
                })

        return formatted_results

    def reset_collection(self) -> None:
        """Clear and recreate the collection."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(name=self.collection_name)


# Global singleton instance
vector_store = VectorStoreService()
