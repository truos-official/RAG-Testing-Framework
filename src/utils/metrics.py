"""
Prometheus metrics for monitoring.

Tracks:
- Request counts
- Response times
- Error rates
- Token usage
- Search performance
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from functools import wraps
import time
from flask import request
from src.utils.logging import get_logger

logger = get_logger(__name__)

# ============================================
# Metrics Definitions
# ============================================

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# RAG-specific metrics
rag_queries_total = Counter(
    'rag_queries_total',
    'Total RAG queries processed',
    ['status']
)

rag_query_duration_seconds = Histogram(
    'rag_query_duration_seconds',
    'RAG query processing time'
)

rag_tokens_used = Counter(
    'rag_tokens_used_total',
    'Total OpenAI tokens consumed'
)

rag_search_results = Histogram(
    'rag_search_results_count',
    'Number of documents retrieved per query'
)

# Error metrics
errors_total = Counter(
    'errors_total',
    'Total errors',
    ['error_type', 'endpoint']
)

# System metrics
active_requests = Gauge(
    'active_requests',
    'Number of requests currently being processed'
)


# ============================================
# Decorators
# ============================================

def track_request_metrics(f):
    """Decorator to track HTTP request metrics."""
    
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Start timer
        start_time = time.time()
        
        # Track active requests
        active_requests.inc()
        
        try:
            # Execute request
            response = f(*args, **kwargs)
            status = response[1] if isinstance(response, tuple) else 200
            
            # Record metrics
            http_requests_total.labels(
                method=request.method,
                endpoint=request.path,
                status=status
            ).inc()
            
            return response
            
        except Exception as e:
            # Track error
            errors_total.labels(
                error_type=type(e).__name__,
                endpoint=request.path
            ).inc()
            raise
            
        finally:
            # Record duration
            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=request.path
            ).observe(duration)
            
            # Decrease active requests
            active_requests.dec()
    
    return wrapper


def track_rag_metrics(f):
    """Decorator to track RAG-specific metrics."""
    
    @wraps(f)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = f(*args, **kwargs)
            
            # Track success
            rag_queries_total.labels(status='success').inc()
            
            # Track duration
            duration = time.time() - start_time
            rag_query_duration_seconds.observe(duration)
            
            # Track tokens if available
            if isinstance(result, tuple) and len(result) > 0:
                response_data = result[0].get_json()
                if 'tokens_used' in response_data:
                    rag_tokens_used.inc(response_data['tokens_used'])
                
                if 'sources' in response_data:
                    rag_search_results.observe(len(response_data['sources']))
            
            return result
            
        except Exception as e:
            # Track failure
            rag_queries_total.labels(status='failure').inc()
            raise
    
    return wrapper


def get_metrics():
    """Generate Prometheus metrics."""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}