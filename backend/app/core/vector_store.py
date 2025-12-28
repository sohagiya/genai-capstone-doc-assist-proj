"""Vector database wrapper for ChromaDB with abstraction for other providers"""
import uuid
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from backend.app.config import settings
from backend.app.core.embeddings import EmbeddingsProvider
from backend.app.utils.logger import logger


class VectorStore:
    """Vector store wrapper with abstraction for multiple backends"""

    def __init__(self, collection_name: str = "documents"):
        self.collection_name = collection_name
        self.embeddings_provider = EmbeddingsProvider()

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=settings.vector_db_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        logger.info(f"Initialized vector store with collection: {collection_name}")

    def add_documents(self, chunks: List[Dict], doc_id: str) -> None:
        """
        Add document chunks to vector store
        Args:
            chunks: List of chunk dicts with text and metadata
            doc_id: Document identifier
        """
        if not chunks:
            return

        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embeddings_provider.generate_embeddings(texts)

        # Prepare data for ChromaDB
        ids = [f"{doc_id}_{chunk['chunk_id']}" for chunk in chunks]

        metadatas = []
        for chunk in chunks:
            metadata = {
                "doc_id": doc_id,
                "chunk_id": str(chunk["chunk_id"]),
                "token_count": chunk["token_count"],
                "start_pos": chunk["start_pos"],
                "end_pos": chunk["end_pos"]
            }

            # Add document metadata if present
            if "metadata" in chunk:
                for key, value in chunk["metadata"].items():
                    # ChromaDB requires metadata values to be strings, ints, or floats
                    if isinstance(value, (str, int, float)):
                        metadata[key] = value
                    else:
                        metadata[key] = str(value)

            metadatas.append(metadata)

        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

        logger.info(f"Added {len(chunks)} chunks for document {doc_id}")

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for similar chunks
        Args:
            query: Search query
            top_k: Number of results to return
        Returns:
            List of dicts with chunk text, metadata, and similarity score
        """
        # Generate query embedding
        query_embedding = self.embeddings_provider.generate_embedding(query)

        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        # Format results
        formatted_results = []
        if results["ids"] and len(results["ids"]) > 0:
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "chunk_id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": 1 - results["distances"][0][i]  # Convert distance to similarity
                })

        logger.info(f"Search returned {len(formatted_results)} results")
        return formatted_results

    def check_document_exists(self, doc_hash: str) -> Optional[str]:
        """
        Check if a document with given hash already exists
        Returns doc_id if exists, None otherwise
        """
        results = self.collection.get(
            where={"file_hash": doc_hash},
            limit=1
        )

        if results["ids"]:
            # Extract doc_id from chunk_id (format: doc_id_chunk_id)
            chunk_id = results["ids"][0]
            doc_id = chunk_id.rsplit("_", 1)[0]
            return doc_id

        return None

    def delete_document(self, doc_id: str) -> None:
        """Delete all chunks for a document"""
        self.collection.delete(
            where={"doc_id": doc_id}
        )
        logger.info(f"Deleted document: {doc_id}")

    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "total_chunks": count
        }

    def list_all_documents(self) -> List[Dict]:
        """List all unique documents in the collection"""
        try:
            # Get all items from collection
            results = self.collection.get()

            # Extract unique documents
            documents = {}
            if results["ids"]:
                for i, chunk_id in enumerate(results["ids"]):
                    metadata = results["metadatas"][i]
                    doc_id = metadata.get("doc_id", "unknown")

                    if doc_id not in documents:
                        documents[doc_id] = {
                            "doc_id": doc_id,
                            "filename": metadata.get("filename", "unknown"),
                            "file_type": metadata.get("file_type", "unknown"),
                            "chunks": 0
                        }

                    documents[doc_id]["chunks"] += 1

            return list(documents.values())
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            return []

    def clear_all_documents(self) -> int:
        """Delete all documents from the collection"""
        try:
            # Get count before deletion
            count = self.collection.count()

            # Delete the entire collection
            self.client.delete_collection(name=self.collection_name)

            # Recreate empty collection
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )

            logger.info(f"Cleared all documents: {count} chunks removed")
            return count
        except Exception as e:
            logger.error(f"Error clearing all documents: {str(e)}")
            raise

    def health_check(self) -> bool:
        """Check if vector store is accessible"""
        try:
            self.collection.count()
            return True
        except Exception as e:
            logger.error(f"Vector store health check failed: {str(e)}")
            return False
