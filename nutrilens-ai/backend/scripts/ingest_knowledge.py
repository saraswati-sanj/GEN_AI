"""
NutriLens AI — Knowledge Ingestion Script
Reads regulatory & scientific documents from backend/knowledge_base/,
chunks them, generates embeddings using BAAI/bge-small-en-v1.5,
and stores them into ChromaDB vector database.
"""
import os
import sys
import argparse
import logging
from pathlib import Path

# Add backend root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.vector_store import vector_store

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("nutrilens.ingest")

KNOWLEDGE_BASE_DIR = Path(__file__).resolve().parent.parent / "knowledge_base"


def split_markdown_into_chunks(content: str, source_file: str, category: str, max_chunk_size: int = 600) -> list:
    """Split markdown file content by headers or paragraphs into semantic chunks."""
    chunks = []
    lines = content.splitlines()
    
    current_header = category.upper()
    current_chunk = []
    current_size = 0
    chunk_index = 0

    for line in lines:
        if line.startswith("#"):
            if current_chunk:
                chunk_text = "\n".join(current_chunk).strip()
                if len(chunk_text) > 30:
                    chunks.append({
                        "id": f"{category}_{Path(source_file).stem}_{chunk_index}",
                        "content": f"Source: {category.upper()} - {current_header}\n\n{chunk_text}",
                        "metadata": {
                            "source": source_file,
                            "category": category,
                            "header": current_header,
                            "chunk_index": chunk_index,
                        }
                    })
                    chunk_index += 1
                current_chunk = []
                current_size = 0
            current_header = line.lstrip("#").strip()
        else:
            current_chunk.append(line)
            current_size += len(line)
            if current_size >= max_chunk_size and line == "":
                chunk_text = "\n".join(current_chunk).strip()
                if len(chunk_text) > 30:
                    chunks.append({
                        "id": f"{category}_{Path(source_file).stem}_{chunk_index}",
                        "content": f"Source: {category.upper()} - {current_header}\n\n{chunk_text}",
                        "metadata": {
                            "source": source_file,
                            "category": category,
                            "header": current_header,
                            "chunk_index": chunk_index,
                        }
                    })
                    chunk_index += 1
                current_chunk = []
                current_size = 0

    if current_chunk:
        chunk_text = "\n".join(current_chunk).strip()
        if len(chunk_text) > 30:
            chunks.append({
                "id": f"{category}_{Path(source_file).stem}_{chunk_index}",
                "content": f"Source: {category.upper()} - {current_header}\n\n{chunk_text}",
                "metadata": {
                    "source": source_file,
                    "category": category,
                    "header": current_header,
                    "chunk_index": chunk_index,
                }
            })

    return chunks


def run_ingestion(reset: bool = False):
    """Scan knowledge_base directory and index all documents into ChromaDB."""
    logger.info(f"Starting Knowledge Base Ingestion from: {KNOWLEDGE_BASE_DIR}")
    
    if reset:
        logger.info("Resetting ChromaDB collection...")
        vector_store.reset_collection()

    total_chunks = 0
    all_docs = []
    all_metas = []
    all_ids = []

    for category_dir in KNOWLEDGE_BASE_DIR.iterdir():
        if category_dir.is_dir():
            category_name = category_dir.name
            for file_path in category_dir.glob("*.md"):
                logger.info(f"Processing knowledge document: [{category_name}] {file_path.name}")
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                file_chunks = split_markdown_into_chunks(content, file_path.name, category_name)
                for chunk in file_chunks:
                    all_docs.append(chunk["content"])
                    all_metas.append(chunk["metadata"])
                    all_ids.append(chunk["id"])
                    total_chunks += 1

    if all_docs:
        logger.info(f"Embedding and indexing {total_chunks} chunks into ChromaDB...")
        added_count = vector_store.add_documents(documents=all_docs, metadatas=all_metas, ids=all_ids)
        logger.info(f"Successfully indexed {added_count} chunks into collection '{vector_store.collection_name}'.")
    else:
        logger.warning("No markdown documents found in knowledge base!")

    return total_chunks


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest Knowledge Base into ChromaDB")
    parser.add_argument("--reset", action="store_true", help="Reset ChromaDB collection before indexing")
    parser.add_argument("--verify", action="store_true", help="Verify search after indexing")
    args = parser.parse_args()

    count = run_ingestion(reset=args.reset)
    
    if args.verify or True:
        logger.info("Testing semantic search query: 'Monosodium glutamate MSG diabetes sodium'")
        results = vector_store.search("Monosodium glutamate MSG diabetes sodium", top_k=3)
        for idx, res in enumerate(results, 1):
            logger.info(f"\n--- Result {idx} (Score: {res['relevance_score']}) ---")
            logger.info(f"Category: {res['metadata'].get('category')}")
            logger.info(f"Snippet: {res['content'][:200]}...")
