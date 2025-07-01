import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import chromadb
import google.generativeai as genai
from google.generativeai import types
import json
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RAGResponse:
    """Response from RAG system"""
    answer: str
    source_documents: List[Dict[str, Any]]
    confidence_score: float
    response_time: float
    metadata: Dict[str, Any]

@dataclass
class RetrievalResult:
    """Single retrieval result"""
    content: str
    metadata: Dict[str, Any]
    similarity_score: float
    document_id: str

class RAGSystem:
    """
    Retrieval-Augmented Generation system using ChromaDB and Google Gemini
    Integrates with the existing backend architecture for the past questions app
    """
    
    def __init__(
        self, 
        gemini_api_key: str,
        chroma_persist_directory: str = "./chroma_db",
        embedding_model: str = "models/text-embedding-004"
    ):
        """Initialize RAG system with Gemini and ChromaDB"""
        self.gemini_api_key = gemini_api_key
        self.embedding_model = embedding_model
        
        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=chroma_persist_directory)
        
        # Collections for different content types
        self.collections = {
            'questions': self._get_or_create_collection('questions'),
            'explanations': self._get_or_create_collection('explanations'),
            'user_context': self._get_or_create_collection('user_context')
        }
        
        logger.info("RAG System initialized successfully")
    
    def _get_or_create_collection(self, collection_name: str):
        """Get or create ChromaDB collection with proper embedding function"""
        try:
            return self.chroma_client.get_collection(
                name=collection_name,
                embedding_function=chromadb.utils.embedding_functions.GoogleGenerativeAiEmbeddingFunction(
                    api_key=self.gemini_api_key,
                    model_name="models/text-embedding-004"
                )
            )
        except ValueError:
            # Collection doesn't exist, create it
            return self.chroma_client.create_collection(
                name=collection_name,
                embedding_function=chromadb.utils.embedding_functions.GoogleGenerativeAiEmbeddingFunction(
                    api_key=self.gemini_api_key,
                    model_name="models/text-embedding-004"
                ),
                metadata={"hnsw:space": "cosine"}
            )
    
    async def add_question_to_knowledge_base(
        self, 
        question_id: str,
        question_text: str,
        answer_text: str = None,
        subject: str = None,
        difficulty: str = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Add question and answer to the knowledge base"""
        try:
            # Prepare document content
            content = f"Question: {question_text}"
            if answer_text:
                content += f"\nAnswer: {answer_text}"
            
            # Prepare metadata
            doc_metadata = {
                "question_id": question_id,
                "subject": subject or "general",
                "difficulty": difficulty or "medium",
                "type": "question",
                "created_at": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            # Add to questions collection
            self.collections['questions'].add(
                documents=[content],
                metadatas=[doc_metadata],
                ids=[question_id]
            )
            
            logger.info(f"Added question {question_id} to knowledge base")
            return True
            
        except Exception as e:
            logger.error(f"Error adding question to knowledge base: {str(e)}")
            return False
    
    async def add_explanation_to_knowledge_base(
        self,
        explanation_id: str,
        question_id: str,
        explanation_text: str,
        explanation_type: str = "detailed",
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Add explanation to the knowledge base"""
        try:
            doc_metadata = {
                "explanation_id": explanation_id,
                "question_id": question_id,
                "type": "explanation",
                "explanation_type": explanation_type,
                "created_at": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            self.collections['explanations'].add(
                documents=[explanation_text],
                metadatas=[doc_metadata],
                ids=[explanation_id]
            )
            
            logger.info(f"Added explanation {explanation_id} to knowledge base")
            return True
            
        except Exception as e:
            logger.error(f"Error adding explanation to knowledge base: {str(e)}")
            return False
    
    async def retrieve_relevant_content(
        self,
        query: str,
        collection_name: str = 'questions',
        n_results: int = 5,
        filters: Dict[str, Any] = None
    ) -> List[RetrievalResult]:
        """Retrieve relevant content from knowledge base"""
        try:
            collection = self.collections[collection_name]
            
            # Perform similarity search
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filters,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Convert to RetrievalResult objects
            retrieval_results = []
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                retrieval_results.append(RetrievalResult(
                    content=doc,
                    metadata=metadata,
                    similarity_score=1 - distance,  # Convert distance to similarity
                    document_id=results['ids'][0][i]
                ))
            
            return retrieval_results
            
        except Exception as e:
            logger.error(f"Error retrieving content: {str(e)}")
            return []
    
    async def generate_answer_with_context(
        self,
        question: str,
        context_documents: List[RetrievalResult],
        user_context: Dict[str, Any] = None
    ) -> str:
        """Generate answer using retrieved context and Gemini"""
        try:
            # Prepare context from retrieved documents
            context_text = "\n\n".join([
                f"Context {i+1} (similarity: {doc.similarity_score:.3f}):\n{doc.content}"
                for i, doc in enumerate(context_documents)
            ])
            
            # Build prompt with context
            prompt = f"""
You are an expert tutor helping students with their academic questions. Use the provided context to answer the question accurately and comprehensively.

Context Information:
{context_text}

Student Question: {question}

Instructions:
1. Use the context information to provide a detailed, accurate answer
2. If the context doesn't fully answer the question, clearly state what information is missing
3. Structure your response clearly with step-by-step explanations when appropriate
4. Include relevant examples from the context when helpful
5. If multiple approaches are shown in the context, explain the different methods
6. Maintain an educational tone suitable for university students

Answer:"""

            # Add user context if available
            if user_context:
                user_info = f"""
Student Context:
- Subject: {user_context.get('subject', 'N/A')}
- Academic Level: {user_context.get('academic_level', 'N/A')}
- Difficulty Preference: {user_context.get('difficulty_preference', 'N/A')}

"""
                prompt = user_info + prompt
            
            # Generate response with Gemini
            response = await self.gemini_model.generate_content_async(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return "I apologize, but I encountered an error while generating the answer. Please try again."
    
    async def rag_query(
        self,
        question: str,
        user_id: str = None,
        subject_filter: str = None,
        difficulty_filter: str = None,
        max_context_docs: int = 5
    ) -> RAGResponse:
        """
        Main RAG query method that combines retrieval and generation
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Build filters for retrieval
            filters = {}
            if subject_filter:
                filters["subject"] = subject_filter
            if difficulty_filter:
                filters["difficulty"] = difficulty_filter
            
            # Retrieve relevant questions and explanations
            question_results = await self.retrieve_relevant_content(
                query=question,
                collection_name='questions',
                n_results=max_context_docs,
                filters=filters
            )
            
            explanation_results = await self.retrieve_relevant_content(
                query=question,
                collection_name='explanations',
                n_results=max_context_docs // 2,
                filters=filters
            )
            
            # Combine and rank results
            all_context = question_results + explanation_results
            all_context.sort(key=lambda x: x.similarity_score, reverse=True)
            top_context = all_context[:max_context_docs]
            
            # Get user context if user_id provided
            user_context = None
            if user_id:
                user_context = await self._get_user_context(user_id)
            
            # Generate answer
            answer = await self.generate_answer_with_context(
                question=question,
                context_documents=top_context,
                user_context=user_context
            )
            
            # Calculate response time and confidence
            response_time = asyncio.get_event_loop().time() - start_time
            confidence_score = self._calculate_confidence_score(top_context)
            
            # Prepare source documents for response
            source_documents = [
                {
                    "content": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                    "metadata": doc.metadata,
                    "similarity_score": doc.similarity_score,
                    "document_id": doc.document_id
                }
                for doc in top_context
            ]
            
            return RAGResponse(
                answer=answer,
                source_documents=source_documents,
                confidence_score=confidence_score,
                response_time=response_time,
                metadata={
                    "question": question,
                    "user_id": user_id,
                    "filters_applied": filters,
                    "context_docs_used": len(top_context)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in RAG query: {str(e)}")
            response_time = asyncio.get_event_loop().time() - start_time
            
            return RAGResponse(
                answer="I apologize, but I encountered an error while processing your question. Please try again.",
                source_documents=[],
                confidence_score=0.0,
                response_time=response_time,
                metadata={"error": str(e)}
            )
    
    async def _get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Retrieve user context from user_context collection"""
        try:
            results = self.collections['user_context'].query(
                query_texts=[f"user:{user_id}"],
                n_results=1,
                include=['metadatas']
            )
            
            if results['metadatas'] and results['metadatas'][0]:
                return results['metadatas'][0][0]
            return {}
            
        except Exception as e:
            logger.error(f"Error retrieving user context: {str(e)}")
            return {}
    
    def _calculate_confidence_score(self, context_documents: List[RetrievalResult]) -> float:
        """Calculate confidence score based on retrieval results"""
        if not context_documents:
            return 0.0
        
        # Average similarity score weighted by rank
        total_score = 0
        total_weight = 0
        
        for i, doc in enumerate(context_documents):
            weight = 1 / (i + 1)  # Higher weight for top results
            total_score += doc.similarity_score * weight
            total_weight += weight
        
        return min(total_score / total_weight, 1.0) if total_weight > 0 else 0.0
    
    async def batch_process_documents(
        self,
        documents: List[Dict[str, Any]],
        batch_size: int = 10
    ) -> Dict[str, Any]:
        """Process multiple documents in batches"""
        results = {"success": 0, "failed": 0, "errors": []}
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            for doc in batch:
                try:
                    success = await self.add_question_to_knowledge_base(
                        question_id=doc.get('question_id'),
                        question_text=doc.get('question_text'),
                        answer_text=doc.get('answer_text'),
                        subject=doc.get('subject'),
                        difficulty=doc.get('difficulty'),
                        metadata=doc.get('metadata', {})
                    )
                    
                    if success:
                        results["success"] += 1
                    else:
                        results["failed"] += 1
                        
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"Document {doc.get('question_id')}: {str(e)}")
            
            # Small delay between batches to avoid rate limiting
            await asyncio.sleep(0.1)
        
        return results
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base collections"""
        stats = {}
        
        for name, collection in self.collections.items():
            try:
                count = collection.count()
                stats[name] = {"document_count": count}
            except Exception as e:
                stats[name] = {"error": str(e)}
        
        return stats


# Utility functions for integration with existing backend
async def initialize_rag_system(gemini_api_key: str) -> RAGSystem:
    """Initialize RAG system for use in FastAPI backend"""
    return RAGSystem(gemini_api_key=gemini_api_key)

async def process_question_with_rag(
    rag_system: RAGSystem,
    question: str,
    user_id: str = None,
    subject: str = None,
    difficulty: str = None
) -> Dict[str, Any]:
    """Process a question using RAG system and return formatted response"""
    response = await rag_system.rag_query(
        question=question,
        user_id=user_id,
        subject_filter=subject,
        difficulty_filter=difficulty
    )
    
    return {
        "answer": response.answer,
        "sources": response.source_documents,
        "confidence": response.confidence_score,
        "response_time": response.response_time,
        "metadata": response.metadata
    }

# Example usage and testing functions
async def test_rag_system():
    """Test function to verify RAG system functionality"""
    # This would be used for testing
    pass

if __name__ == "__main__":
    # Basic test
    asyncio.run(test_rag_system())