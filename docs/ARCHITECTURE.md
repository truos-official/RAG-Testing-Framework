# System Architecture

## High-Level Overview
```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │ HTTP/JSON
       ▼
┌─────────────────────────────────────┐
│         Flask API Layer             │
│  - Rate Limiting (20/min)           │
│  - Input Validation (Pydantic)      │
│  - Metrics Collection (Prometheus)  │
└──────┬──────────────────────────────┘
       │
       ├──────────────────┬─────────────────┐
       ▼                  ▼                 ▼
┌─────────────┐   ┌──────────────┐  ┌──────────────┐
│   Search    │   │     LLM      │  │   Metrics    │
│   Service   │   │   Service    │  │   Service    │
└──────┬──────┘   └──────┬───────┘  └──────────────┘
       │                 │
       ▼                 ▼
┌─────────────┐   ┌──────────────┐
│   Azure AI  │   │   OpenAI     │
│   Search    │   │   GPT-4      │
│  (Vectors)  │   │ (Completion) │
└─────────────┘   └──────────────┘
```

## Component Details

### 1. API Layer (`src/api/`)

**Responsibilities:**
- HTTP request handling
- Rate limiting enforcement
- Input validation
- Error handling
- Metrics collection

**Key Files:**
- `routes.py` - Endpoint definitions
- `rate_limiter.py` - Rate limit configuration

### 2. Service Layer (`src/services/`)

**Azure Search Service:**
- Generates query embeddings
- Performs vector similarity search
- Returns top-K documents

**LLM Service:**
- Embedding generation
- RAG response generation
- Token tracking

### 3. Configuration (`src/config/`)

**settings.py:**
- Type-safe configuration
- Environment variable loading
- Validation with Pydantic

### 4. Utilities (`src/utils/`)

**logging.py:**
- Structured JSON logging
- Log level management
- Context enrichment

**metrics.py:**
- Prometheus metrics
- Performance tracking
- Error monitoring

## Data Flow

### Query Request Flow
```
1. Client sends POST /api/v1/query
   {
     "question": "What is your return policy?",
     "top_k": 3
   }

2. Rate Limiter checks limits (20/min)
   └─> If exceeded: Return 429

3. Pydantic validates input
   └─> If invalid: Return 400

4. Search Service:
   a. Generate embedding for query
   b. Search Azure AI Search
   c. Return top 3 documents

5. LLM Service:
   a. Build RAG prompt with context
   b. Call GPT-4
   c. Return answer + token count

6. Response returned to client
   {
     "question": "...",
     "answer": "...",
     "sources": ["POL-001"],
     "tokens_used": 89
   }

7. Metrics recorded:
   - Request count
   - Duration
   - Tokens used
   - Search results count
```

## Azure AI Search Index Schema
```json
{
  "name": "knowledge-base",
  "fields": [
    {
      "name": "doc_id",
      "type": "Edm.String",
      "key": true
    },
    {
      "name": "title",
      "type": "Edm.String",
      "searchable": true
    },
    {
      "name": "content",
      "type": "Edm.String",
      "searchable": true
    },
    {
      "name": "content_vector",
      "type": "Collection(Edm.Single)",
      "searchable": true,
      "dimensions": 1536,
      "vectorSearchProfile": "vector-profile"
    },
    {
      "name": "category",
      "type": "Edm.String",
      "filterable": true
    }
  ],
  "vectorSearch": {
    "algorithms": [
      {
        "name": "hnsw-config",
        "kind": "hnsw",
        "hnswParameters": {
          "m": 4,
          "efConstruction": 400,
          "efSearch": 500,
          "metric": "cosine"
        }
      }
    ]
  }
}
```

## Deployment Architecture
```
┌──────────────────────────────────────┐
│        GitHub Repository             │
│  - Source code                       │
│  - .env.example (no secrets)         │
└──────────────┬───────────────────────┘
               │
               │ git push
               ▼
┌──────────────────────────────────────┐
│      GitHub Actions (CI/CD)          │
│  1. Run tests                        │
│  2. Build Docker image               │
│  3. Push to container registry       │
└──────────────┬───────────────────────┘
               │
               │ deploy
               ▼
┌──────────────────────────────────────┐
│   Azure Container Instances          │
│  - Docker container running          │
│  - Environment variables from vault  │
│  - Public endpoint with SSL          │
└──────────────────────────────────────┘
               │
               ├───────────┬──────────┐
               ▼           ▼          ▼
        ┌───────────┐ ┌────────┐ ┌──────────┐
        │  Azure AI │ │ OpenAI │ │ Azure    │
        │  Search   │ │  API   │ │ Monitor  │
        └───────────┘ └────────┘ └──────────┘
```

## Security Considerations

1. **API Keys**: Stored in environment variables, never committed
2. **Rate Limiting**: Prevents abuse and cost overruns
3. **Input Validation**: Prevents injection attacks
4. **HTTPS**: All production traffic encrypted
5. **Secrets Management**: Azure Key Vault in production

## Performance Characteristics

- **Avg Response Time**: 1-3 seconds
- **Throughput**: 20 queries/min per user
- **Token Cost**: ~100 tokens per query
- **Search Latency**: 50-200ms
- **LLM Latency**: 1-2 seconds

## Monitoring & Alerting

**Key Metrics:**
- Error rate threshold: 5%
- Response time p95: 3 seconds
- Token usage: Track for cost management

**Alerts:**
- Error rate > 5% → Email
- Response time > 5s → Slack
- Daily token usage > threshold → Email