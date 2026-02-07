import requests

print("🧪 Testing Dockerized RAG API\n")

# Health check
health = requests.get("http://localhost:8080/health")
print(f"✅ Health: {health.json()}\n")

# Test query
response = requests.post(
    "http://localhost:8080/api/query",
    json={"question": "What is your return policy?"}
)

result = response.json()
print(f"Question: {result['question']}")
print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")