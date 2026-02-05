# Enterprise RAG Testing Framework

AI model testing framework for evaluating LLMs with Azure AI services.

## Features

- RAG (Retrieval-Augmented Generation) API
- Azure AI Search integration
- Hallucination detection
- Bias & toxicity testing
- Compliance reporting (EU AI Act, NIST)

## Tech Stack

- Python, Flask
- OpenAI GPT-4
- Azure AI Search
- Azure Content Safety
- Docker

## Setup

1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add credentials
4. Run: `python app.py`

## Project Structure
```
├── app.py              # Main API
├── requirements.txt    # Dependencies
├── .env.example        # Environment template
└── tests/             # Test files
```

## Author

Tristan Gitman @TRUOS.io
