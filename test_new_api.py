import requests

print("🧪 Testing Enterprise RAG API\n")

# Test 1: Health check
print("Test 1: Health Check")
print("-" * 50)
response = requests.get("http://localhost:5000/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# Test 2: RAG Query
print("Test 2: RAG Query - 'What is your return policy?'")
print("-" * 50)
response = requests.post(
    "http://localhost:5000/api/v1/query",
    json={"question": "What is your return policy?", "top_k": 3}
)
result = response.json()
print(f"Question: {result['question']}")
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")
print(f"Tokens: {result['tokens_used']}\n")

# Test 3: Semantic query
print("Test 3: Semantic Query - 'How do I get my money back?'")
print("-" * 50)
response = requests.post(
    "http://localhost:5000/api/v1/query",
    json={"question": "How do I get my money back?"}
)
result = response.json()
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}\n")

# Test 4: Search endpoint
print("Test 4: Search Endpoint - 'shipping'")
print("-" * 50)
response = requests.post(
    "http://localhost:5000/api/v1/search",
    json={"query": "shipping", "top_k": 3}
)
result = response.json()
print(f"Found {result['num_results']} results:")
for doc in result['results']:
    print(f"  - {doc['doc_id']}: {doc['title']} (score: {doc['score']:.2f})")

print("\n✅ All tests passed!")