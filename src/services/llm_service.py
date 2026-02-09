"""
LLM Service - Handles all interactions with OpenAI API.

Responsibilities:
- Generate embeddings for text
- Generate chat completions
- Handle retries and errors
- Track token usage
"""

from openai import OpenAI
from typing import List, Dict, Any
from src.config.settings import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


class LLMService:
    """Service for OpenAI API interactions."""
    
    def __init__(self):
        """Initialize OpenAI client with configuration."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.temperature = settings.openai_temperature
        self.max_tokens = settings.openai_max_tokens
        
        logger.info("LLM Service initialized", extra={
            "model": self.model,
            "temperature": self.temperature
        })
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate vector embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
            
        Example:
            embedding = llm_service.generate_embedding("return policy")
            # Returns: [0.23, -0.45, 0.67, ..., 0.12]
        """
        try:
            logger.debug("Generating embedding", extra={
                "text_length": len(text)
            })
            
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            
            embedding = response.data[0].embedding
            
            logger.debug("Embedding generated", extra={
                "vector_dimension": len(embedding)
            })
            
            return embedding
            
        except Exception as e:
            logger.error("Embedding generation failed", extra={
                "error": str(e),
                "text_length": len(text)
            })
            raise
    
    def generate_completion(
        self,
        prompt: str,
        system_message: str = None
    ) -> Dict[str, Any]:
        """
        Generate chat completion from GPT-4.
        
        Args:
            prompt: User message/prompt
            system_message: Optional system message for context
            
        Returns:
            Dict containing:
                - answer: Generated text
                - tokens_used: Token count
                - model: Model used
                
        Example:
            result = llm_service.generate_completion(
                prompt="What is your return policy?",
                system_message="You are a helpful assistant."
            )
            print(result["answer"])
        """
        try:
            logger.info("Generating completion", extra={
                "prompt_length": len(prompt),
                "model": self.model
            })
            
            # Build messages
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            # Call OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract result
            answer = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            logger.info("Completion generated", extra={
                "tokens_used": tokens_used,
                "answer_length": len(answer)
            })
            
            return {
                "answer": answer,
                "tokens_used": tokens_used,
                "model": self.model
            }
            
        except Exception as e:
            logger.error("Completion generation failed", extra={
                "error": str(e),
                "model": self.model
            })
            raise
    
    def generate_rag_response(
        self,
        question: str,
        context_documents: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Generate RAG response using retrieved documents.
        
        Args:
            question: User's question
            context_documents: List of retrieved documents
                Each doc should have: doc_id, content
                
        Returns:
            Dict with answer, tokens_used, sources
            
        Example:
            docs = [
                {"doc_id": "POL-001", "content": "We accept returns..."},
                {"doc_id": "POL-002", "content": "Shipping is free..."}
            ]
            result = llm_service.generate_rag_response(
                question="What is your return policy?",
                context_documents=docs
            )
        """
        try:
            # Build context from documents
            context = "\n\n".join([
                f"Document {doc['doc_id']}:\n{doc['content']}"
                for doc in context_documents
            ])
            
            # Build RAG prompt
            prompt = f"""Answer the question based ONLY on the following documents.
Cite the document IDs in your answer.

Documents:
{context}

Question: {question}

Answer:"""
            
            # Generate completion
            result = self.generate_completion(prompt)
            
            # Add source document IDs
            result["sources"] = [doc["doc_id"] for doc in context_documents]
            
            return result
            
        except Exception as e:
            logger.error("RAG response generation failed", extra={
                "error": str(e),
                "question": question,
                "num_documents": len(context_documents)
            })
            raise