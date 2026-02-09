"""
API Routes - Flask endpoints for RAG system.

Endpoints:
- POST /api/query - Query the RAG system
- GET /health - Health check
"""

from flask import request, jsonify
from typing import Dict, Any
from src.services.azure_search_service import AzureSearchService
from src.services.llm_service import LLMService
from src.utils.logging import get_logger
from src.api.rate_limiter import get_limiter
from src.utils.metrics import track_request_metrics, track_rag_metrics, get_metrics

logger = get_logger(__name__)

# Initialize services (singleton pattern)
search_service = AzureSearchService()
llm_service = LLMService()
limiter = None


def register_routes(app):
    """Register all API routes with Flask app."""
    
    global limiter
    limiter = get_limiter(app)  # Initialize rate limiter

    @app.route('/metrics', methods=['GET'])
    @limiter.exempt
    def metrics():
        """Prometheus metrics endpoint."""
        return get_metrics()
    
    @app.route('/health', methods=['GET'])
    @limiter.exempt  # No rate limit on health checks
    @track_request_metrics
    def health():
        """Enhanced health check with service status."""
        try:
            # Could add actual service checks here
            return jsonify({
                "status": "healthy",
                "version": "1.0.0",
                "services": {
                    "azure_search": "healthy",
                    "openai": "healthy"
                }
            }), 200
        except Exception as e:
            return jsonify({
                "status": "unhealthy",
                "error": str(e)
            }), 503
    
    @app.route('/api/v1/query', methods=['POST'])
    @limiter.limit("20 per minute")  # Expensive endpoint
    @track_request_metrics
    @track_rag_metrics
    def query():
        """
        Query the RAG system.
        
        Request Body:
            {
                "question": "What is your return policy?",
                "top_k": 3  // optional, default 3
            }
        
        Response:
            {
                "question": "...",
                "answer": "...",
                "sources": ["POL-001", "POL-002"],
                "tokens_used": 89
            }
        """
        try:
            # Validate request
            data = request.json
            if not data or 'question' not in data:
                logger.warning("Invalid request - missing question")
                return jsonify({"error": "Missing 'question' in request"}), 400
            
            question = data['question']
            top_k = data.get('top_k', 3)
            
            # Validate question
            if not question.strip():
                return jsonify({"error": "Question cannot be empty"}), 400
            
            if len(question) > 1000:
                return jsonify({"error": "Question too long (max 1000 chars)"}), 400
            
            logger.info("Processing query", extra={
                "question_length": len(question),
                "top_k": top_k
            })
            
            # Step 1: Search for relevant documents
            logger.debug("Searching documents")
            retrieved_docs = search_service.search(
                query=question,
                top_k=top_k
            )
            
            if not retrieved_docs:
                logger.info("No documents found")
                return jsonify({
                    "question": question,
                    "answer": "I don't have information about that.",
                    "sources": [],
                    "tokens_used": 0
                }), 200
            
            logger.debug("Documents retrieved", extra={
                "num_docs": len(retrieved_docs),
                "top_score": retrieved_docs[0]['score']
            })
            
            # Step 2: Generate RAG response
            logger.debug("Generating response")
            result = llm_service.generate_rag_response(
                question=question,
                context_documents=retrieved_docs
            )
            
            # Step 3: Build response
            response = {
                "question": question,
                "answer": result['answer'],
                "sources": result['sources'],
                "tokens_used": result['tokens_used']
            }
            
            logger.info("Query completed", extra={
                "tokens_used": result['tokens_used'],
                "num_sources": len(result['sources'])
            })
            
            return jsonify(response), 200
            
        except Exception as e:
            logger.error("Query failed", extra={
                "error": str(e)
            }, exc_info=True)
            return jsonify({
                "error": "Internal server error",
                "message": str(e)
            }), 500
    
    @app.route('/api/v1/search', methods=['POST'])
    @limiter.limit("60 per minute")
    @track_request_metrics
    def search():
        """
        Search documents without generating answer.
        
        Request Body:
            {
                "query": "shipping",
                "top_k": 5
            }
        
        Response:
            {
                "query": "shipping",
                "results": [
                    {
                        "doc_id": "POL-002",
                        "title": "Shipping Policy",
                        "content": "...",
                        "score": 0.89
                    }
                ]
            }
        """
        try:
            data = request.json
            if not data or 'query' not in data:
                return jsonify({"error": "Missing 'query' in request"}), 400
            
            query = data['query']
            top_k = data.get('top_k', 5)
            
            results = search_service.search(query=query, top_k=top_k)
            
            return jsonify({
                "query": query,
                "num_results": len(results),
                "results": results
            }), 200
            
        except Exception as e:
            logger.error("Search failed", extra={"error": str(e)})
            return jsonify({"error": str(e)}), 500