"""
Index documents into Azure AI Search with vector embeddings.

This script:
1. Loads documents from JSON file
2. Generates embeddings for each document
3. Uploads documents to Azure AI Search index
"""

import sys
from pathlib import Path
import json

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from src.config.settings import settings
from src.services.llm_service import LLMService
from src.utils.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def load_knowledge_base(file_path: str = "data/knowledge_base.json"):
    """Load knowledge base from JSON file."""
    
    path = project_root / file_path
    
    logger.info("Loading knowledge base", extra={
        "file_path": str(path)
    })
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    documents = data.get("documents", [])
    
    logger.info("Knowledge base loaded", extra={
        "num_documents": len(documents)
    })
    
    return documents


def index_documents():
    """Index documents with embeddings into Azure AI Search."""
    
    # Initialize clients
    search_client = SearchClient(
        endpoint=settings.azure_search_endpoint,
        index_name=settings.azure_search_index_name,
        credential=AzureKeyCredential(settings.azure_search_key)
    )
    
    llm_service = LLMService()
    
    # Load documents
    documents = load_knowledge_base()
    
    logger.info("Starting document indexing", extra={
        "num_documents": len(documents),
        "index_name": settings.azure_search_index_name
    })
    
    # Process each document
    indexed_docs = []
    
    for i, doc in enumerate(documents, 1):
        print(f"\nProcessing {i}/{len(documents)}: {doc['doc_id']}")
        
        try:
            # Generate embedding for content
            logger.debug("Generating embedding", extra={
                "doc_id": doc["doc_id"]
            })
            
            embedding = llm_service.generate_embedding(doc["content"])
            
            # Prepare document for indexing
            search_doc = {
                "doc_id": doc["doc_id"],
                "title": doc.get("title", ""),
                "content": doc["content"],
                "content_vector": embedding,
                "category": doc.get("category", "general")
            }
            
            indexed_docs.append(search_doc)
            
            print(f"  ✅ Embedded (dimension: {len(embedding)})")
            
        except Exception as e:
            logger.error("Failed to process document", extra={
                "doc_id": doc["doc_id"],
                "error": str(e)
            })
            print(f"  ❌ Error: {e}")
            continue
    
    # Upload to Azure AI Search
    if indexed_docs:
        print(f"\n📤 Uploading {len(indexed_docs)} documents to Azure AI Search...")
        
        try:
            result = search_client.upload_documents(documents=indexed_docs)
            
            succeeded = sum(1 for r in result if r.succeeded)
            failed = len(result) - succeeded
            
            logger.info("Documents indexed", extra={
                "succeeded": succeeded,
                "failed": failed
            })
            
            print(f"\n✅ Indexing complete!")
            print(f"   Succeeded: {succeeded}")
            print(f"   Failed: {failed}")
            
        except Exception as e:
            logger.error("Failed to upload documents", extra={
                "error": str(e)
            })
            print(f"\n❌ Upload failed: {e}")
            raise
    else:
        print("\n⚠️  No documents to index")


if __name__ == "__main__":
    index_documents()