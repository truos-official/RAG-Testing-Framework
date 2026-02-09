"""
Azure AI Search Service - Production vector search implementation.

Replaces simple keyword matching with semantic vector search.

Responsibilities:
- Perform vector similarity search
- Hybrid search (text + vectors)
- Return ranked results with scores
"""

from typing import List, Dict, Any
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from src.config.settings import settings
from src.services.llm_service import LLMService
from src.utils.logging import get_logger

logger = get_logger(__name__)


class AzureSearchService:
    """Production search service using Azure AI Search with vector embeddings."""
    
    def __init__(self):
        """Initialize Azure AI Search client and LLM service."""
        
        # Initialize search client
        self.search_client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index_name,
            credential=AzureKeyCredential(settings.azure_search_key)
        )
        
        # Initialize LLM service for embeddings
        self.llm_service = LLMService()
        
        logger.info("Azure Search Service initialized", extra={
            "endpoint": settings.azure_search_endpoint,
            "index": settings.azure_search_index_name
        })
    
    def search(
        self,
        query: str,
        top_k: int = 3,
        use_vector_search: bool = True,
        use_text_search: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for documents using hybrid search (text + vector).
        
        Args:
            query: Search query string
            top_k: Number of results to return (default: 3)
            use_vector_search: Enable vector similarity search (default: True)
            use_text_search: Enable keyword search (default: True)
            
        Returns:
            List of documents with scores
            
        Example:
            results = search_service.search(
                query="How do I return an item?",
                top_k=5
            )
            for doc in results:
                print(f"{doc['doc_id']}: {doc['score']}")
        """
        try:
            logger.info("Performing search", extra={
                "query": query,
                "top_k": top_k,
                "vector_search": use_vector_search,
                "text_search": use_text_search
            })
            
            # Generate query embedding for vector search
            vector_queries = []
            if use_vector_search:
                logger.debug("Generating query embedding")
                query_embedding = self.llm_service.generate_embedding(query)
                
                vector_queries = [
                    VectorizedQuery(
                        vector=query_embedding,
                        k_nearest_neighbors=top_k,
                        fields="content_vector"
                    )
                ]
            
            # Perform search
            search_text = query if use_text_search else None
            
            results = self.search_client.search(
                search_text=search_text,
                vector_queries=vector_queries,
                top=top_k,
                select=["doc_id", "title", "content", "category"]
            )
            
            # Convert to list and format
            documents = []
            for result in results:
                doc = {
                    "doc_id": result["doc_id"],
                    "title": result["title"],
                    "content": result["content"],
                    "category": result.get("category", ""),
                    "score": result.get("@search.score", 0.0)
                }
                documents.append(doc)
            
            logger.info("Search completed", extra={
                "num_results": len(documents),
                "top_score": documents[0]["score"] if documents else 0
            })
            
            return documents
            
        except Exception as e:
            logger.error("Search failed", extra={
                "error": str(e),
                "query": query
            })
            raise
    
    def vector_search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Perform pure vector similarity search (semantic search only).
        
        Better for questions phrased differently from documents.
        
        Args:
            query: Natural language query
            top_k: Number of results
            
        Returns:
            List of semantically similar documents
            
        Example:
            # Query: "How do I get my money back?"
            # Finds: "Return Policy" document (even without exact words)
            results = search_service.vector_search(
                "How do I get my money back?",
                top_k=3
            )
        """
        return self.search(
            query=query,
            top_k=top_k,
            use_vector_search=True,
            use_text_search=False
        )
    
    def text_search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Perform pure keyword search (traditional search).
        
        Better for exact term matching.
        
        Args:
            query: Keyword query
            top_k: Number of results
            
        Returns:
            List of documents matching keywords
        """
        return self.search(
            query=query,
            top_k=top_k,
            use_vector_search=False,
            use_text_search=True
        )
    
    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document dict or None if not found
        """
        try:
            result = self.search_client.get_document(key=doc_id)
            
            logger.debug("Document retrieved", extra={
                "doc_id": doc_id
            })
            
            return {
                "doc_id": result["doc_id"],
                "title": result["title"],
                "content": result["content"],
                "category": result.get("category", "")
            }
            
        except Exception as e:
            logger.warning("Document not found", extra={
                "doc_id": doc_id,
                "error": str(e)
            })
            return None