import google.generativeai as genai
from google.generativeai import types
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProcessedContent:
    """Data class for processed content"""
    content_id: str
    text_content: str
    image_content: Optional[bytes] = None
    metadata: Dict[str, Any] = None
    content_type: str = "text"

@dataclass
class QuestionEmbedding:
    """Data class for question embeddings"""
    question_id: str
    embeddings: Dict[str, List[float]]
    metadata: Dict[str, Any]
    created_at: str

class GeminiServiceHub:
    def __init__(self, api_key: str):
        """Initialize Gemini Service with API key"""
        genai.configure(api_key=api_key)
        self.gemini_pro = genai.GenerativeModel('gemini-1.5-pro')
        self.gemini_flash = genai.GenerativeModel('gemini-1.5-flash')
        self.embedding_model = 'models/text-embedding-004'
        logger.info("GeminiServiceHub initialized successfully")
    
    async def generate_explanation(self, question: str, answer: str, context: dict) -> str:
        """Generate comprehensive explanation for a question and answer"""
        try:
            prompt = f"""
            As an expert tutor, provide a comprehensive explanation for this question:
            
            Question: {question}
            Correct Answer: {answer}
            Subject: {context.get('subject', 'General')}
            Difficulty Level: {context.get('difficulty', 'Medium')}
            
            Please provide:
            1. Step-by-step solution approach
            2. Key concepts involved
            3. Common mistakes to avoid
            4. Alternative solution methods (if applicable)
            
            Format your response in clear, educational language suitable for university students.
            """
            
            response = await self.gemini_pro.generate_content_async(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            return "Unable to generate explanation at this time."
    
    async def generate_progressive_hints(self, question: str, context: dict) -> List[str]:
        """Generate progressive hints for a question"""
        try:
            prompt = f"""
            Create 3 progressive hints for this question, each revealing more information:
            
            Question: {question}
            Subject: {context.get('subject', 'General')}
            
            Hint 1: Very subtle guidance (don't reveal key concepts)
            Hint 2: Point toward the approach (reveal some key concepts)
            Hint 3: Clear direction (reveal most concepts but not the final answer)
            
            Return as a JSON array of strings.
            """
            
            response = await self.gemini_flash.generate_content_async(prompt)
            
            # Parse JSON response
            try:
                hints = json.loads(response.text)
                if isinstance(hints, list) and len(hints) >= 3:
                    return hints[:3]  # Return first 3 hints
                else:
                    # Fallback if JSON parsing fails
                    return [
                        "Think about the fundamental concepts related to this topic.",
                        "Consider the key formula or principle that applies here.",
                        "Look at the specific steps needed to solve this type of problem."
                    ]
            except json.JSONDecodeError:
                # Fallback hints if JSON parsing fails
                return [
                    "Consider the basic principles involved in this question.",
                    "Think about the methodology typically used for this type of problem.",
                    "Focus on the key steps needed to reach the solution."
                ]
                
        except Exception as e:
            logger.error(f"Error generating hints: {str(e)}")
            return [
                "Try to identify the key concepts in the question.",
                "Consider what formulas or principles might apply.",
                "Break down the problem into smaller steps."
            ]
    
    async def generate_similar_questions(self, original_question: str, context: dict) -> List[str]:
        """Generate similar questions based on an original question"""
        try:
            prompt = f"""
            Generate 3 similar questions based on the original question below. 
            The questions should test the same concepts but with different scenarios or values.
            
            Original Question: {original_question}
            Subject: {context.get('subject', 'General')}
            Difficulty: {context.get('difficulty', 'Medium')}
            
            Requirements:
            - Same difficulty level as the original
            - Test the same underlying concepts
            - Use different numerical values or scenarios
            - Maintain educational value
            
            Return as a JSON array of strings.
            """
            
            response = await self.gemini_pro.generate_content_async(prompt)
            
            try:
                similar_questions = json.loads(response.text)
                if isinstance(similar_questions, list):
                    return similar_questions[:3]  # Return up to 3 questions
                else:
                    return []
            except json.JSONDecodeError:
                logger.warning("Failed to parse similar questions JSON")
                return []
                
        except Exception as e:
            logger.error(f"Error generating similar questions: {str(e)}")
            return []

    async def classify_question_content(self, question_text: str) -> Dict[str, Any]:
        """Classify question content to extract metadata"""
        try:
            prompt = f"""
            Analyze the following question and extract metadata:
            
            Question: {question_text}
            
            Please provide the following information in JSON format:
            {{
                "subject": "estimated subject (e.g., Mathematics, Physics, Chemistry, etc.)",
                "difficulty": "estimated difficulty (Easy, Medium, Hard)",
                "question_type": "type (Multiple Choice, Short Answer, Essay, Numerical, etc.)",
                "topics": ["list", "of", "key", "topics"],
                "keywords": ["important", "keywords", "from", "question"],
                "estimated_time": "estimated time to solve in minutes"
            }}
            """
            
            response = await self.gemini_flash.generate_content_async(prompt)
            
            try:
                classification = json.loads(response.text)
                return classification
            except json.JSONDecodeError:
                # Return default classification if parsing fails
                return {
                    "subject": "General",
                    "difficulty": "Medium",
                    "question_type": "Unknown",
                    "topics": [],
                    "keywords": [],
                    "estimated_time": "10"
                }
                
        except Exception as e:
            logger.error(f"Error classifying question: {str(e)}")
            return {
                "subject": "General",
                "difficulty": "Medium",
                "question_type": "Unknown",
                "topics": [],
                "keywords": [],
                "estimated_time": "10"
            }

    async def process_image_question(self, image_data: bytes) -> str:
        """Process image-based questions using Gemini Vision"""
        try:
            # Create image part for Gemini
            image_part = types.Part.from_data(image_data, mime_type="image/jpeg")
            
            prompt = """
            Analyze this image and extract any text content, mathematical expressions, or questions.
            If there are multiple questions, separate them clearly.
            Preserve mathematical notation and formatting as much as possible.
            """
            
            response = await self.gemini_pro.generate_content_async([prompt, image_part])
            return response.text
            
        except Exception as e:
            logger.error(f"Error processing image question: {str(e)}")
            return "Unable to process image content."

class EmbeddingPipeline:
    """Pipeline for generating embeddings for questions and content"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.embedding_model = 'models/text-embedding-004'
        logger.info("EmbeddingPipeline initialized successfully")
    
    async def generate_question_embeddings(self, content: ProcessedContent) -> QuestionEmbedding:
        """Generate embeddings for question content"""
        try:
            # Prepare text for embedding
            embedding_text = content.text_content
            
            # Add metadata context to improve embedding quality
            if content.metadata:
                context_parts = []
                if content.metadata.get('subject'):
                    context_parts.append(f"Subject: {content.metadata['subject']}")
                if content.metadata.get('topics'):
                    context_parts.append(f"Topics: {', '.join(content.metadata['topics'])}")
                
                if context_parts:
                    embedding_text = f"{' '.join(context_parts)}\n\n{embedding_text}"
            
            # Generate embedding
            embedding_response = await genai.embed_content_async(
                model=self.embedding_model,
                content=embedding_text,
                task_type="retrieval_document"
            )
            
            # Create embedding object
            question_embedding = QuestionEmbedding(
                question_id=content.content_id,
                embeddings={
                    "text": embedding_response['embedding']
                },
                metadata=content.metadata or {},
                created_at=datetime.now().isoformat()
            )
            
            return question_embedding
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            # Return empty embedding on error
            return QuestionEmbedding(
                question_id=content.content_id,
                embeddings={},
                metadata=content.metadata or {},
                created_at=datetime.now().isoformat()
            )
    
    async def generate_query_embedding(self, query: str, task_type: str = "retrieval_query") -> List[float]:
        """Generate embedding for search queries"""
        try:
            embedding_response = await genai.embed_content_async(
                model=self.embedding_model,
                content=query,
                task_type=task_type
            )
            
            return embedding_response['embedding']
            
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            return []

    async def batch_generate_embeddings(
        self, 
        contents: List[ProcessedContent],
        batch_size: int = 5
    ) -> List[QuestionEmbedding]:
        """Generate embeddings for multiple contents in batches"""
        embeddings = []
        
        for i in range(0, len(contents), batch_size):
            batch = contents[i:i + batch_size]
            
            # Process batch concurrently
            batch_tasks = [
                self.generate_question_embeddings(content) 
                for content in batch
            ]
            
            batch_embeddings = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Filter out exceptions and add valid embeddings
            for embedding in batch_embeddings:
                if isinstance(embedding, QuestionEmbedding):
                    embeddings.append(embedding)
                else:
                    logger.error(f"Error in batch embedding: {embedding}")
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)
        
        return embeddings


# Utility functions for integration
async def create_gemini_service(api_key: str) -> GeminiServiceHub:
    """Create and configure Gemini service"""
    return GeminiServiceHub(api_key=api_key)

async def create_embedding_pipeline(api_key: str) -> EmbeddingPipeline:
    """Create and configure embedding pipeline"""
    return EmbeddingPipeline(api_key=api_key)

# Test function
async def test_gemini_service():
    """Test Gemini service functionality"""
    # This would be used for testing
    pass

if __name__ == "__main__":
    asyncio.run(test_gemini_service())