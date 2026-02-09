# Enterprise RAG Testing Framework

Production-ready Retrieval-Augmented Generation (RAG) system with Azure AI Search, OpenAI GPT-4, and enterprise monitoring.

## 🎯 Features

- **Vector Search**: Azure AI Search with semantic embeddings (1536-dimensional)
- **RAG Pipeline**: GPT-4 powered question answering with retrieved context
- **Rate Limiting**: 20 queries/min, 60 searches/min to control costs
- **Monitoring**: Prometheus metrics for observability
- **Structured Logging**: JSON logs for production debugging
- **Type Safety**: Pydantic validation for all inputs/outputs
- **CI/CD**: GitHub Actions pipeline with automated testing
- **Containerized**: Docker ready for cloud deployment

## 🏗️ Architecture
```
User Query
    ↓
Flask API (Rate Limited)
    ↓
Azure AI Search (Vector Similarity)
    ↓
Top K Documents Retrieved
    ↓
OpenAI GPT-4 (RAG Response)
    ↓
JSON Response + Metrics
```

## 📁 Project Structure
```
rag-testing-framework/
├── src/
│   ├── api/
│   │   ├── routes.py              # API endpoints
│   │   └── rate_limiter.py        # Rate limiting config
│   ├── services/
│   │   ├── llm_service.py         # OpenAI integration
│   │   └── azure_search_service.py # Azure AI Search
│   ├── config/
│   │   └── settings.py            # Configuration management
│   └── utils/
│       ├── logging.py             # Structured logging
│       └── metrics.py             # Prometheus metrics
├── scripts/
│   ├── create_search_index.py    # Initialize Azure index
│   └── index_documents.py         # Upload documents
├── data/
│   └── knowledge_base.json        # Document repository
├── tests/
│   └── (test files)
├── .github/workflows/
│   └── ci-cd.yml                  # GitHub Actions
├── Dockerfile
├── requirements.txt
└── app.py                         # Application entry point
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Azure subscription
- OpenAI API key

### Installation

1. **Clone repository**
```bash
git clone https://github.com/truos-official/rag-testing-framework.git
cd rag-testing-framework
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Create Azure AI Search index**
```bash
python scripts/create_search_index.py
```

5. **Index documents**
```bash
python scripts/index_documents.py
```

6. **Run application**
```bash
python app.py
```

Server runs at: http://localhost:5000

## 📖 API Endpoints

### Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "azure_search": "healthy",
    "openai": "healthy"
  }
}
```

### Query RAG System
```bash
POST /api/v1/query
Content-Type: application/json

{
  "question": "What is your return policy?",
  "top_k": 3
}
```

Response:
```json
{
  "question": "What is your return policy?",
  "answer": "According to POL-001, we accept returns within 30 days...",
  "sources": ["POL-001"],
  "tokens_used": 89
}
```

### Search Documents
```bash
POST /api/v1/search
Content-Type: application/json

{
  "query": "shipping",
  "top_k": 5
}
```

### Prometheus Metrics
```bash
GET /metrics
```

## 📊 Monitoring

### Available Metrics

- `http_requests_total` - Total HTTP requests by endpoint/status
- `http_request_duration_seconds` - Request latency histogram
- `rag_queries_total` - RAG query count by status
- `rag_tokens_used_total` - OpenAI token consumption
- `errors_total` - Error count by type/endpoint
- `active_requests` - Currently processing requests

### Grafana Dashboard

Import metrics into Grafana for visualization:
1. Configure Prometheus to scrape `/metrics`
2. Create Grafana dashboard
3. Monitor costs, performance, errors

## 🔒 Rate Limits

- **Query endpoint**: 20 requests/minute
- **Search endpoint**: 60 requests/minute  
- **Health check**: Unlimited

## 🧪 Testing
```bash
# Test RAG functionality
python test_new_api.py

# Test rate limiting
python test_rate_limit.py

# Test metrics
python test_metrics.py

# Run unit tests
pytest tests/
```

## 🐳 Docker Deployment

### Build Image
```bash
docker build -t rag-api:latest .
```

### Run Container
```bash
docker run -d -p 8080:80 \
  -e OPENAI_API_KEY="sk-..." \
  -e AZURE_SEARCH_ENDPOINT="https://..." \
  -e AZURE_SEARCH_KEY="..." \
  --name rag-api rag-api:latest
```

## 🛠️ Tech Stack

- **Backend**: Python 3.11, Flask
- **AI/ML**: OpenAI GPT-4, OpenAI Embeddings
- **Search**: Azure AI Search (HNSW vector index)
- **Monitoring**: Prometheus, structured logging
- **Validation**: Pydantic
- **Containerization**: Docker
- **CI/CD**: GitHub Actions

## 📝 Configuration

All configuration via environment variables. See `.env.example`:
```bash
# OpenAI
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4

# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_KEY=...
AZURE_SEARCH_INDEX_NAME=knowledge-base

# API Settings
API_HOST=0.0.0.0
API_PORT=5000
LOG_LEVEL=INFO
```

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 🙏 Acknowledgments

- Azure AI Search for vector search capabilities
- OpenAI for GPT-4 and embeddings


## 📧 Contact

**Developer**: Tristan Gitman  
**Email**: info@truos.io  
**GitHub**: [@truos-official](https://github.com/truos-official)

---

Built with ❤️ for production AI systems