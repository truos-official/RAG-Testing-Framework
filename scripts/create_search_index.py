"""
Create Azure AI Search index with vector search capabilities.

This script:
1. Connects to Azure AI Search
2. Defines index schema (fields, vector config)
3. Creates the index
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
)
from azure.core.credentials import AzureKeyCredential
from src.config.settings import settings
from src.utils.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def create_search_index():
    """Create Azure AI Search index with vector search."""
    
    # Initialize index client
    index_client = SearchIndexClient(
        endpoint=settings.azure_search_endpoint,
        credential=AzureKeyCredential(settings.azure_search_key)
    )
    
    logger.info("Creating search index", extra={
        "index_name": settings.azure_search_index_name,
        "endpoint": settings.azure_search_endpoint
    })
    
    # Define fields
    fields = [
        # Unique document ID
        SimpleField(
            name="doc_id",
            type=SearchFieldDataType.String,
            key=True,
            filterable=True,
            sortable=True
        ),
        
        # Document title (searchable text)
        SearchableField(
            name="title",
            type=SearchFieldDataType.String,
            searchable=True,
            filterable=True
        ),
        
        # Document content (searchable text)
        SearchableField(
            name="content",
            type=SearchFieldDataType.String,
            searchable=True
        ),
        
        # Vector embedding for semantic search
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,  # OpenAI embedding size
            vector_search_profile_name="vector-profile"
        ),
        
        # Metadata
        SimpleField(
            name="category",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True
        ),
    ]
    
    # Configure vector search
    vector_search = VectorSearch(
        profiles=[
            VectorSearchProfile(
                name="vector-profile",
                algorithm_configuration_name="hnsw-config"
            )
        ],
        algorithms=[
            HnswAlgorithmConfiguration(
                name="hnsw-config",
                parameters={
                    "m": 4,
                    "efConstruction": 400,
                    "efSearch": 500,
                    "metric": "cosine"
                }
            )
        ]
    )
    
    # Create index definition
    index = SearchIndex(
        name=settings.azure_search_index_name,
        fields=fields,
        vector_search=vector_search
    )
    
    # Create or update index
    try:
        result = index_client.create_or_update_index(index)
        logger.info("Search index created successfully", extra={
            "index_name": result.name,
            "fields_count": len(result.fields)
        })
        print(f"\n✅ Index created: {result.name}")
        print(f"   Fields: {len(result.fields)}")
        print(f"   Vector search enabled: Yes")
        
    except Exception as e:
        logger.error("Failed to create index", extra={
            "error": str(e)
        })
        raise


if __name__ == "__main__":
    create_search_index()