from flask import Flask, request, jsonify
import json
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load .env file (works locally, harmless in Docker)
load_dotenv()

# Get API key (works both locally and in Docker)
api_key = os.getenv("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found!")

client = OpenAI(api_key=api_key)

app=Flask(__name__)

knowledge_base = {
    "documents": [
        {
            "doc_id": "POL-001",
            "title": "Return Policy",
            "content": "We accept returns within 30 days of purchase with original receipt. Refunds processed in 5-7 business days."
        },
        {
            "doc_id": "POL-002",
            "title": "Shipping Policy",
            "content": "Free standard shipping on orders over $50. Standard delivery 3-5 business days."
        },
        {
            "doc_id": "POL-003",
            "title": "Customer Policy",
            "content": "We love our clients, especially those who pay on time!"
        }
    ]
}

def retrieve_docs(query, top_k=2):
    query_lower=query.lower()
    scored_docs=[]

    for doc in knowledge_base["documents"]:
        score=0
        content= (doc["title"] + " " + doc["content"]).lower()
        for word in query_lower.split():
            if len(word)>3 and word in content:
                score+=content.count(word)
            if score>0:
                scored_docs.append((score,doc))
    scored_docs.sort(reverse=True,key=lambda x: x[0])
    return [doc for score, doc in scored_docs[:top_k]]


@app.route('/api/query', methods=['POST'])
def query():
    data = request.json
    question = data.get('question')
    
    if not question:
        return jsonify({"error": "Missing question"}), 400
    
    retrieved_docs = retrieve_docs(question)
    
    if not retrieved_docs:
        return jsonify({
            "question": question,
            "answer": "I don't have information about that.",
            "sources": []
        })
    
    # YOUR CODE: Build context string
    context = "\n\n".join([f"Doc {d['doc_id']}:\n{d['content']}" for d in retrieved_docs])
 
    # Provided: Build prompt
    prompt = f"""Answer based ONLY on these documents. Cite doc IDs.

Docs:
{context}

Question: {question}

Answer:"""
    
    # Provided: Call GPT-4
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    
    return jsonify({
        "question": question,
        "answer": response.choices[0].message.content,
        "sources": [d["doc_id"] for d in retrieved_docs]
    })
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    print("🚀 RAG API Starting...")
    print("📍 Endpoint: http://localhost:5000/api/query")
    app.run(host='0.0.0.0', port=5000, debug=True)
