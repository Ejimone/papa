from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from typing import List, Dict, Any, Optional, Union
import asyncio
import logging
import base64
from datetime import datetime
import uuid
from pydantic import BaseModel

from app.schemas.user import UserRead
from app.schemas.question import QuestionCreate, QuestionResponse
from app.api.deps import get_current_user
from app.core.config import settings

# AI Service imports
from app.ai.processing.text_processor import TextProcessor
from app.ai.processing.image_processor import ImageProcessor
from app.ai.vector_db.client import ChromaDBClient
from app.ai.vector_db.queries import VectorQueries
from app.ai.personalization.user_modeling import UserModelingService, QuestionInteraction
from app.ai.personalization.recommendation import RecommendationEngine
from app.ai.personalization.difficulty_adapter import DifficultyAdapter, AdaptationStrategy
from app.ai.personalization.learning_path import LearningPathGenerator, PathType, LearningObjective

# New AI Services
from app.ai.embeddings.text_embeddings import TextEmbeddingService
from app.ai.embeddings.image_embeddings import ImageEmbeddingService
from app.ai.embeddings.hybrid_embeddings import HybridEmbeddingService
from app.ai.llm.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

router = APIRouter()

# Chat request/response models
class AskQuestionRequest(BaseModel):
    question: str
    context: Optional[str] = "general_study_help"
    subject: Optional[str] = None
    previous_messages: Optional[List[Dict[str, str]]] = []

class AskQuestionResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[str] = []
    suggestions: List[str] = []

# Initialize AI services (these would typically be dependency injected)
text_processor = TextProcessor(use_advanced_nlp=False)
image_processor = ImageProcessor(use_mock=settings.DEBUG)
chroma_client = ChromaDBClient(in_memory=settings.DEBUG)
vector_queries = VectorQueries(chroma_client)
user_modeling_service = UserModelingService()
recommendation_engine = RecommendationEngine(vector_queries, None)
difficulty_adapter = DifficultyAdapter(AdaptationStrategy.MODERATE)
learning_path_generator = LearningPathGenerator(difficulty_adapter)

# New AI service instances
try:
    text_embedding_service = TextEmbeddingService()
    image_embedding_service = ImageEmbeddingService()
    hybrid_embedding_service = HybridEmbeddingService(text_embedding_service, image_embedding_service)
    gemini_client = GeminiClient() if settings.GEMINI_API_KEY else None
    logger.info("AI services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize AI services: {e}")
    text_embedding_service = None
    image_embedding_service = None
    hybrid_embedding_service = None
    gemini_client = None

@router.post("/ask-question")
async def ask_ai_question(
    request: AskQuestionRequest,
    current_user: UserRead = Depends(get_current_user)
):
    """
    Ask the AI assistant a general question about studies, subjects, or practice questions.
    """
    try:
        # Simple AI response for now
        ai_response = f"I understand you're asking about: {request.question}. This is a great question about {request.subject or 'your studies'}! While I'm still learning, I can help you explore the app to find practice questions, study materials, and track your progress."
        
        # Generate helpful suggestions
        suggestions = [
            "Try the Practice section for hands-on questions",
            "Check the Learn section for study materials",
            "Use the Search feature to find specific topics"
        ]
        
        return {
            "answer": ai_response,
            "confidence": 0.7,
            "sources": ["AI Study Assistant"],
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error(f"Error processing AI question: {e}")
        return {
            "answer": "I'm here to help! Try asking me about specific subjects, practice questions, or study tips. You can also explore the app's Practice and Learn sections for immediate help.",
            "confidence": 0.5,
            "sources": ["AI Study Assistant"],
            "suggestions": [
                "Try rephrasing your question",
                "Explore the Practice section",
                "Check the Learn materials"
            ]
        }

# Pydantic schemas for AI endpoints
from pydantic import BaseModel, Field
from enum import Enum

# Existing schemas
class QuestionAnalysisRequest(BaseModel):
    text: str
    subject: Optional[str] = None
    expected_difficulty: Optional[int] = None

class QuestionAnalysisResponse(BaseModel):
    question_type: str
    difficulty_score: float
    keywords: List[str]
    mathematical_expressions: List[str]
    estimated_time: int  # seconds
    confidence: float
    
class ImageAnalysisRequest(BaseModel):
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    
class ImageAnalysisResponse(BaseModel):
    extracted_text: str
    confidence: float
    language: str
    has_mathematical_content: bool
    mathematical_expressions: List[str]
    processing_time: float

# New schemas for embedding functionality
class TextEmbeddingRequest(BaseModel):
    text: str
    task_type: str = "RETRIEVAL_DOCUMENT"

class TextEmbeddingResponse(BaseModel):
    embedding: List[float]
    dimension: int
    task_type: str
    processing_time: float

class ImageEmbeddingRequest(BaseModel):
    image_base64: Optional[str] = None

class ImageEmbeddingResponse(BaseModel):
    embedding: List[float]
    dimension: int
    ocr_text: str
    ocr_confidence: float
    description: str
    content_analysis: Dict[str, Any]
    processing_time: float

class HybridEmbeddingRequest(BaseModel):
    question_text: str
    image_base64: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    fusion_method: str = "concatenation"

class HybridEmbeddingResponse(BaseModel):
    hybrid_embedding: List[float]
    text_embedding: List[float]
    image_embedding: List[float]
    fusion_method: str
    text_weight: float
    image_weight: float
    dimension: int
    processing_time: float

class QuestionProcessingRequest(BaseModel):
    question_id: Optional[int] = None
    question_text: str
    answer: Optional[str] = None
    subject: Optional[str] = None
    topic: Optional[str] = None
    difficulty_level: Optional[str] = None
    question_type: Optional[str] = None
    image_urls: Optional[List[str]] = []
    generate_explanations: bool = True
    generate_hints: bool = True
    find_similar: bool = True

class QuestionProcessingResponse(BaseModel):
    question_id: Optional[int]
    processing_status: str
    metadata_extracted: Dict[str, Any]
    embeddings_generated: bool
    vector_id: Optional[str]
    explanations: List[str]
    hints: List[str]
    similar_questions: List[Dict[str, Any]]
    processing_time: float
    errors: List[str]

class SimilarityCalculationRequest(BaseModel):
    embedding1: List[float]
    embedding2: List[float]
    similarity_type: str = "cosine"

class SimilarityCalculationResponse(BaseModel):
    similarity_score: float
    similarity_type: str
    embedding_dimension: int

class SimilarQuestionSearchRequest(BaseModel):
    question_text: Optional[str] = None
    question_id: Optional[int] = None
    embedding: Optional[List[float]] = None
    subject_filter: Optional[str] = None
    difficulty_filter: Optional[List[int]] = None
    limit: int = 10
    threshold: float = 0.5

class SimilarQuestionSearchResponse(BaseModel):
    query_info: Dict[str, Any]
    similar_questions: List[Dict[str, Any]]
    total_found: int
    search_time: float

class MetadataExtractionRequest(BaseModel):
    question_text: str
    answer: Optional[str] = None
    subject: Optional[str] = None
    image_data: Optional[str] = None  # base64 encoded

class MetadataExtractionResponse(BaseModel):
    keywords: List[str]
    concepts: List[str]
    prerequisites: List[str]
    learning_objectives: List[str]
    clarity_score: float
    completeness_score: float
    difficulty_confidence: float
    processing_time: float

class BatchProcessingRequest(BaseModel):
    question_ids: Optional[List[int]] = None
    subject_id: Optional[int] = None
    batch_size: int = 10
    reprocess: bool = False
    generate_embeddings: bool = True
    extract_metadata: bool = True
    process_images: bool = True

class BatchProcessingResponse(BaseModel):
    job_id: str
    status: str
    total_questions: int
    estimated_completion_time: str
    batch_size: int

class ProcessingStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: float
    processed: int
    failed: int
    total: int
    current_question: Optional[str]
    estimated_remaining_time: Optional[str]
    errors: List[str]

# New endpoints for embedding functionality

@router.post("/embeddings/text", response_model=TextEmbeddingResponse)
async def generate_text_embedding(
    request: TextEmbeddingRequest,
    current_user: UserRead = Depends(get_current_user)
):
    """Generate text embeddings for a given text."""
    try:
        if not text_embedding_service:
            raise HTTPException(status_code=503, detail="Text embedding service not available")
        
        start_time = datetime.now()
        
        embedding = await text_embedding_service.get_single_embedding(
            request.text, 
            task_type=request.task_type
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return TextEmbeddingResponse(
            embedding=embedding,
            dimension=len(embedding),
            task_type=request.task_type,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error generating text embedding: {e}")
        raise HTTPException(status_code=500, detail=f"Text embedding generation failed: {str(e)}")

@router.post("/embeddings/image", response_model=ImageEmbeddingResponse)
async def generate_image_embedding(
    file: UploadFile = File(None),
    image_base64: Optional[str] = Form(None),
    current_user: UserRead = Depends(get_current_user)
):
    """Generate embeddings for an image (either uploaded file or base64)."""
    try:
        if not image_embedding_service:
            raise HTTPException(status_code=503, detail="Image embedding service not available")
        
        start_time = datetime.now()
        
        # Get image data
        if file:
            image_data = await file.read()
        elif image_base64:
            image_data = base64.b64decode(image_base64)
        else:
            raise HTTPException(status_code=400, detail="Either file or image_base64 must be provided")
        
        # Process the image
        result = await image_embedding_service.process_question_image(
            image_data, 
            "uploaded_image"
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        if result['success']:
            return ImageEmbeddingResponse(
                embedding=result['embedding'],
                dimension=len(result['embedding']),
                ocr_text=result['ocr_text'],
                ocr_confidence=result['ocr_confidence'],
                description=result['description'],
                content_analysis=result['content_analysis'],
                processing_time=processing_time
            )
        else:
            raise HTTPException(status_code=500, detail=f"Image processing failed: {result.get('processing_error')}")
        
    except Exception as e:
        logger.error(f"Error generating image embedding: {e}")
        raise HTTPException(status_code=500, detail=f"Image embedding generation failed: {str(e)}")

@router.post("/embeddings/hybrid", response_model=HybridEmbeddingResponse)
async def generate_hybrid_embedding(
    request: HybridEmbeddingRequest,
    current_user: UserRead = Depends(get_current_user)
):
    """Generate hybrid embeddings combining text and optional image data."""
    try:
        if not hybrid_embedding_service:
            raise HTTPException(status_code=503, detail="Hybrid embedding service not available")
        
        start_time = datetime.now()
        
        # Prepare image data if provided
        question_images = None
        if request.image_base64:
            image_data = base64.b64decode(request.image_base64)
            question_images = [image_data]
        
        # Generate hybrid embedding
        result = await hybrid_embedding_service.create_question_embedding(
            question_text=request.question_text,
            question_images=question_images,
            question_metadata=request.metadata
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        if result['success']:
            return HybridEmbeddingResponse(
                hybrid_embedding=result['hybrid_embedding'],
                text_embedding=result['text_embedding'],
                image_embedding=result['image_embedding'],
                fusion_method=result['fusion_method'],
                text_weight=result['text_weight'],
                image_weight=result['image_weight'],
                dimension=len(result['hybrid_embedding']),
                processing_time=processing_time
            )
        else:
            raise HTTPException(status_code=500, detail=f"Hybrid embedding generation failed: {result.get('error')}")
        
    except Exception as e:
        logger.error(f"Error generating hybrid embedding: {e}")
        raise HTTPException(status_code=500, detail=f"Hybrid embedding generation failed: {str(e)}")

@router.post("/process-question", response_model=QuestionProcessingResponse)
async def process_single_question(
    request: QuestionProcessingRequest,
    current_user: UserRead = Depends(get_current_user)
):
    """Process a single question with AI analysis, embeddings, and content generation."""
    try:
        start_time = datetime.now()
        errors = []
        
        # Extract metadata
        metadata = {}
        if gemini_client:
            try:
                # For now, create sample metadata - in production, use AI extraction
                metadata = {
                    "keywords": ["sample", "keyword"],
                    "concepts": ["sample concept"],
                    "prerequisites": [],
                    "learning_objectives": ["understand the concept"],
                    "clarity_score": 0.8,
                    "completeness_score": 0.7,
                    "difficulty_confidence": 0.8
                }
            except Exception as e:
                errors.append(f"Metadata extraction failed: {e}")
        
        # Generate embeddings
        embeddings_generated = False
        vector_id = None
        if hybrid_embedding_service:
            try:
                embedding_result = await hybrid_embedding_service.create_question_embedding(
                    question_text=request.question_text,
                    question_metadata=metadata
                )
                if embedding_result['success']:
                    embeddings_generated = True
                    vector_id = f"question_{request.question_id or uuid.uuid4()}"
            except Exception as e:
                errors.append(f"Embedding generation failed: {e}")
        
        # Generate explanations
        explanations = []
        if request.generate_explanations and gemini_client:
            try:
                explanation = await gemini_client.generate_explanation(
                    request.question_text, 
                    request.answer
                )
                explanations.append(explanation)
            except Exception as e:
                errors.append(f"Explanation generation failed: {e}")
        
        # Generate hints
        hints = []
        if request.generate_hints:
            try:
                hint = f"Consider the {request.question_type or 'question'} format and think about the key concepts involved."
                hints.append(hint)
            except Exception as e:
                errors.append(f"Hint generation failed: {e}")
        
        # Find similar questions
        similar_questions = []
        if request.find_similar and embeddings_generated:
            try:
                # Mock similar questions for now
                similar_questions = [
                    {
                        "question_id": f"similar_{i}",
                        "similarity_score": 0.9 - (i * 0.1),
                        "question_text": f"Similar question {i}"
                    }
                    for i in range(3)
                ]
            except Exception as e:
                errors.append(f"Similar question search failed: {e}")
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return QuestionProcessingResponse(
            question_id=request.question_id,
            processing_status="completed" if not errors else "completed_with_errors",
            metadata_extracted=metadata,
            embeddings_generated=embeddings_generated,
            vector_id=vector_id,
            explanations=explanations,
            hints=hints,
            similar_questions=similar_questions,
            processing_time=processing_time,
            errors=errors
        )
        
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=f"Question processing failed: {str(e)}")

@router.post("/extract-metadata", response_model=MetadataExtractionResponse)
async def extract_question_metadata(
    request: MetadataExtractionRequest,
    current_user: UserRead = Depends(get_current_user)
):
    """Extract comprehensive metadata from a question using AI."""
    try:
        start_time = datetime.now()
        
        if not gemini_client:
            # Return mock metadata if Gemini is not available
            return MetadataExtractionResponse(
                keywords=["sample", "keyword", "mathematics"],
                concepts=["basic algebra", "problem solving"],
                prerequisites=["arithmetic", "basic math"],
                learning_objectives=["understand the concept", "apply knowledge"],
                clarity_score=0.8,
                completeness_score=0.7,
                difficulty_confidence=0.8,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
        
        # Prepare content for analysis
        content = f"Question: {request.question_text}"
        if request.answer:
            content += f"\nAnswer: {request.answer}"
        if request.subject:
            content += f"\nSubject: {request.subject}"
        
        # Generate metadata using AI (mock implementation)
        metadata = {
            "keywords": [word for word in request.question_text.split()[:5] if len(word) > 3],
            "concepts": ["problem solving", "critical thinking"],
            "prerequisites": ["basic knowledge"],
            "learning_objectives": ["understand the question", "apply knowledge"],
            "clarity_score": 0.8,
            "completeness_score": 0.7,
            "difficulty_confidence": 0.8
        }
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return MetadataExtractionResponse(
            keywords=metadata["keywords"],
            concepts=metadata["concepts"],
            prerequisites=metadata["prerequisites"],
            learning_objectives=metadata["learning_objectives"],
            clarity_score=metadata["clarity_score"],
            completeness_score=metadata["completeness_score"],
            difficulty_confidence=metadata["difficulty_confidence"],
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error extracting metadata: {e}")
        raise HTTPException(status_code=500, detail=f"Metadata extraction failed: {str(e)}")

@router.post("/calculate-similarity", response_model=SimilarityCalculationResponse)
async def calculate_similarity(
    request: SimilarityCalculationRequest,
    current_user: UserRead = Depends(get_current_user)
):
    """Calculate similarity between two embeddings."""
    try:
        if not hybrid_embedding_service:
            raise HTTPException(status_code=503, detail="Hybrid embedding service not available")
        
        similarity_score = hybrid_embedding_service.calculate_hybrid_similarity(
            request.embedding1,
            request.embedding2,
            similarity_type=request.similarity_type
        )
        
        return SimilarityCalculationResponse(
            similarity_score=similarity_score,
            similarity_type=request.similarity_type,
            embedding_dimension=len(request.embedding1)
        )
        
    except Exception as e:
        logger.error(f"Error calculating similarity: {e}")
        raise HTTPException(status_code=500, detail=f"Similarity calculation failed: {str(e)}")

@router.post("/find-similar-questions", response_model=SimilarQuestionSearchResponse)
async def find_similar_questions_advanced(
    request: SimilarQuestionSearchRequest,
    current_user: UserRead = Depends(get_current_user)
):
    """Find similar questions using advanced search capabilities."""
    try:
        start_time = datetime.now()
        
        # For now, return mock similar questions
        # In production, this would query the vector database
        similar_questions = [
            {
                "question_id": f"similar_{i}",
                "question_text": f"Sample similar question {i}",
                "similarity_score": 0.9 - (i * 0.1),
                "subject": request.subject_filter or "general",
                "difficulty": 2,
                "question_type": "multiple_choice"
            }
            for i in range(min(request.limit, 5))
            if 0.9 - (i * 0.1) >= request.threshold
        ]
        
        search_time = (datetime.now() - start_time).total_seconds()
        
        query_info = {
            "query_type": "text" if request.question_text else "embedding",
            "subject_filter": request.subject_filter,
            "difficulty_filter": request.difficulty_filter,
            "threshold": request.threshold
        }
        
        return SimilarQuestionSearchResponse(
            query_info=query_info,
            similar_questions=similar_questions,
            total_found=len(similar_questions),
            search_time=search_time
        )
        
    except Exception as e:
        logger.error(f"Error finding similar questions: {e}")
        raise HTTPException(status_code=500, detail=f"Similar question search failed: {str(e)}")

# Background task storage (in production, use Redis or database)
processing_jobs = {}

@router.post("/process-questions-batch", response_model=BatchProcessingResponse)
async def process_questions_batch(
    request: BatchProcessingRequest,
    background_tasks: BackgroundTasks,
    current_user: UserRead = Depends(get_current_user)
):
    """Start batch processing of questions in the background."""
    try:
        job_id = str(uuid.uuid4())
        
        # Initialize job status
        processing_jobs[job_id] = {
            "status": "started",
            "progress": 0.0,
            "processed": 0,
            "failed": 0,
            "total": len(request.question_ids) if request.question_ids else 0,
            "current_question": None,
            "errors": [],
            "started_at": datetime.now()
        }
        
        # Add background task
        background_tasks.add_task(
            process_questions_background,
            job_id,
            request
        )
        
        return BatchProcessingResponse(
            job_id=job_id,
            status="started",
            total_questions=processing_jobs[job_id]["total"],
            estimated_completion_time="Calculating...",
            batch_size=request.batch_size
        )
        
    except Exception as e:
        logger.error(f"Error starting batch processing: {e}")
        raise HTTPException(status_code=500, detail=f"Batch processing failed to start: {str(e)}")

@router.get("/processing-status/{job_id}", response_model=ProcessingStatusResponse)
async def get_processing_status(
    job_id: str,
    current_user: UserRead = Depends(get_current_user)
):
    """Get the status of a batch processing job."""
    try:
        if job_id not in processing_jobs:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job = processing_jobs[job_id]
        
        # Calculate estimated remaining time
        estimated_remaining_time = None
        if job["processed"] > 0 and job["status"] == "processing":
            elapsed_time = (datetime.now() - job["started_at"]).total_seconds()
            avg_time_per_question = elapsed_time / job["processed"]
            remaining_questions = job["total"] - job["processed"]
            estimated_remaining_time = f"{remaining_questions * avg_time_per_question:.0f} seconds"
        
        return ProcessingStatusResponse(
            job_id=job_id,
            status=job["status"],
            progress=job["progress"],
            processed=job["processed"],
            failed=job["failed"],
            total=job["total"],
            current_question=job["current_question"],
            estimated_remaining_time=estimated_remaining_time,
            errors=job["errors"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting processing status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get processing status: {str(e)}")

async def process_questions_background(job_id: str, request: BatchProcessingRequest):
    """Background task for processing questions."""
    try:
        job = processing_jobs[job_id]
        job["status"] = "processing"
        
        # Mock processing - in production, this would process actual questions
        question_ids = request.question_ids or []
        total = len(question_ids)
        job["total"] = total
        
        for i, question_id in enumerate(question_ids):
            try:
                job["current_question"] = f"Question {question_id}"
                
                # Simulate processing time
                await asyncio.sleep(0.1)
                
                job["processed"] += 1
                job["progress"] = (job["processed"] / total) * 100
                
            except Exception as e:
                job["failed"] += 1
                job["errors"].append(f"Failed to process question {question_id}: {e}")
        
        job["status"] = "completed"
        job["current_question"] = None
        
    except Exception as e:
        processing_jobs[job_id]["status"] = "failed"
        processing_jobs[job_id]["errors"].append(f"Batch processing failed: {e}")
        logger.error(f"Background processing failed for job {job_id}: {e}")

@router.get("/embedding-info")
async def get_embedding_info(
    current_user: UserRead = Depends(get_current_user)
):
    """Get information about embedding services configuration."""
    try:
        if not hybrid_embedding_service:
            return {
                "status": "unavailable",
                "message": "Embedding services not initialized"
            }
        
        info = hybrid_embedding_service.get_embedding_info()
        
        return {
            "status": "available",
            "embedding_config": info,
            "services": {
                "text_embeddings": text_embedding_service is not None,
                "image_embeddings": image_embedding_service is not None,
                "hybrid_embeddings": hybrid_embedding_service is not None,
                "gemini_client": gemini_client is not None
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting embedding info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get embedding info: {str(e)}")

# Existing endpoints (keeping all original functionality)
class RecommendationRequest(BaseModel):
    subject: str
    limit: int = 10
    difficulty_range: Optional[tuple[int, int]] = None
    exclude_attempted: bool = True

class RecommendationResponse(BaseModel):
    question_id: str
    recommendation_strategy: str
    confidence_score: float
    reasoning: str
    estimated_difficulty: int

class LearningPathRequest(BaseModel):
    subject: str
    objectives: List[str]  # Will be converted to LearningObjective enum
    path_type: str = "sequential"  # Will be converted to PathType enum
    max_sessions: int = 10
    session_duration_minutes: int = 30

class LearningPathResponse(BaseModel):
    path_id: str
    subject: str
    path_type: str
    total_sessions: int
    total_duration_minutes: int
    estimated_completion_days: int
    sessions: List[Dict[str, Any]]

class DifficultyAdaptationRequest(BaseModel):
    subject: str
    recent_interactions_count: int = 10

class DifficultyAdaptationResponse(BaseModel):
    current_difficulty: int
    recommended_difficulty: Optional[int]
    confidence: str
    reasoning: List[str]
    should_adapt: bool

@router.post("/analyze-question", response_model=QuestionAnalysisResponse)
async def analyze_question_text(
    request: QuestionAnalysisRequest,
    current_user: UserRead = Depends(get_current_user)
):
    """
    Analyze question text to determine type, difficulty, and extract metadata
    """
    try:
        # Process the question text
        analysis_result = await text_processor.process_text(request.text)
        
        # Estimate time based on difficulty and type
        base_time = 60  # Base 60 seconds
        type_multiplier = {
            "multiple_choice": 1.0,
            "short_answer": 1.5,
            "essay": 3.0,
            "numerical": 1.2,
            "fill_blank": 0.8,
            "matching": 1.3
        }
        
        estimated_time = int(base_time * type_multiplier.get(analysis_result.question_type.value, 1.0) * analysis_result.difficulty_score)
        
        return QuestionAnalysisResponse(
            question_type=analysis_result.question_type.value,
            difficulty_score=analysis_result.difficulty_score,
            keywords=analysis_result.keywords[:10],  # Limit to top 10
            mathematical_expressions=analysis_result.mathematical_expressions,
            estimated_time=estimated_time,
            confidence=0.85  # Would be calculated from various factors
        )
        
    except Exception as e:
        logger.error(f"Error analyzing question: {e}")
        raise HTTPException(status_code=500, detail=f"Question analysis failed: {str(e)}")

@router.post("/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_question_image(
    file: UploadFile = File(...),
    current_user: UserRead = Depends(get_current_user)
):
    """
    Extract text and analyze content from uploaded question images
    """
    try:
        # Read the uploaded file
        image_bytes = await file.read()
        
        # Process the image
        start_time = datetime.now()
        ocr_result = await image_processor.ocr_image_from_bytes(image_bytes)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # For mock implementation, return structured response
        if image_processor.use_mock:
            return ImageAnalysisResponse(
                extracted_text="Sample extracted text from image: What is the derivative of f(x) = x^2 + 3x?",
                confidence=0.92,
                language="en",
                has_mathematical_content=True,
                mathematical_expressions=["f(x) = x^2 + 3x", "derivative"],
                processing_time=processing_time
            )
        
        # For real implementation, process the OCR result
        return ImageAnalysisResponse(
            extracted_text=ocr_result.text if hasattr(ocr_result, 'text') else str(ocr_result),
            confidence=ocr_result.confidence if hasattr(ocr_result, 'confidence') else 0.8,
            language=ocr_result.language if hasattr(ocr_result, 'language') else "en",
            has_mathematical_content=ocr_result.has_mathematical_content if hasattr(ocr_result, 'has_mathematical_content') else False,
            mathematical_expressions=ocr_result.mathematical_expressions if hasattr(ocr_result, 'mathematical_expressions') else [],
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

@router.post("/recommendations", response_model=List[RecommendationResponse])
async def get_personalized_recommendations(
    request: RecommendationRequest,
    current_user: UserRead = Depends(get_current_user)
):
    """
    Get personalized question recommendations for the user
    """
    try:
        # Mock user profile for now
        from app.ai.personalization.user_modeling import UserProfile, LearningStyle, PerformanceLevel
        
        mock_profile = UserProfile(
            user_id=str(current_user.id),
            academic_level="undergraduate",
            subjects=[request.subject],
            learning_style=LearningStyle.MIXED,
            study_goals=["mastery"],
            performance_levels={request.subject: PerformanceLevel.DEVELOPING},
            weak_areas=[],
            strong_areas=[]
        )
        
        # Generate mock recommendations
        recommendations = []
        for i in range(min(request.limit, 5)):
            recommendations.append(RecommendationResponse(
                question_id=f"rec_question_{i}",
                recommendation_strategy="adaptive_learning",
                confidence_score=0.8 - (i * 0.1),
                reasoning=f"Based on your performance in {request.subject}",
                estimated_difficulty=2 + (i % 3)
            ))
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation generation failed: {str(e)}")

@router.post("/learning-path", response_model=LearningPathResponse)
async def generate_learning_path(
    request: LearningPathRequest,
    current_user: UserRead = Depends(get_current_user)
):
    """
    Generate a personalized learning path for the user
    """
    try:
        # Mock learning path response
        sessions_data = []
        for i in range(min(request.max_sessions, 5)):
            session_data = {
                "session_type": "practice",
                "total_duration": request.session_duration_minutes,
                "steps_count": 3,
                "focus_areas": request.objectives,
                "difficulty_range": [1, 3],
                "steps": [
                    {
                        "topic_id": f"topic_{j}",
                        "topic_name": f"Topic {j}",
                        "difficulty": 2,
                        "duration": request.session_duration_minutes // 3,
                        "question_count": 5,
                        "step_type": "practice"
                    }
                    for j in range(3)
                ]
            }
            sessions_data.append(session_data)
        
        return LearningPathResponse(
            path_id=str(uuid.uuid4()),
            subject=request.subject,
            path_type=request.path_type,
            total_sessions=len(sessions_data),
            total_duration_minutes=request.session_duration_minutes * len(sessions_data),
            estimated_completion_days=len(sessions_data),
            sessions=sessions_data
        )
        
    except Exception as e:
        logger.error(f"Error generating learning path: {e}")
        raise HTTPException(status_code=500, detail=f"Learning path generation failed: {str(e)}")

@router.post("/adapt-difficulty", response_model=DifficultyAdaptationResponse)
async def adapt_user_difficulty(
    request: DifficultyAdaptationRequest,
    current_user: UserRead = Depends(get_current_user)
):
    """
    Analyze user performance and recommend difficulty adjustments
    """
    try:
        # Mock difficulty adaptation
        return DifficultyAdaptationResponse(
            current_difficulty=2,
            recommended_difficulty=3,
            confidence="medium",
            reasoning=["User showing consistent improvement", "Ready for more challenging questions"],
            should_adapt=True
        )
        
    except Exception as e:
        logger.error(f"Error in difficulty adaptation: {e}")
        raise HTTPException(status_code=500, detail=f"Difficulty adaptation failed: {str(e)}")

@router.get("/user-profile")
async def get_user_ai_profile(
    current_user: UserRead = Depends(get_current_user)
):
    """
    Get the user's AI-generated profile and learning analytics
    """
    try:
        return {
            "user_id": str(current_user.id),
            "performance_level": "developing",
            "learning_style": "mixed",
            "preferred_difficulty": 2,
            "strong_subjects": ["mathematics"],
            "weak_subjects": ["physics"],
            "study_preferences": ["visual", "practice"],
            "learning_patterns": {"peak_hours": "evening", "preferred_session_length": 30},
            "total_interactions": 45
        }
        
    except Exception as e:
        logger.error(f"Error getting user AI profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user AI profile: {str(e)}")

@router.post("/submit-interaction")
async def submit_question_interaction(
    question_id: str = Form(...),
    subject: str = Form(...),
    difficulty: int = Form(...),
    is_correct: bool = Form(...),
    time_taken: int = Form(...),
    attempts: int = Form(1),
    hint_used: bool = Form(False),
    current_user: UserRead = Depends(get_current_user)
):
    """
    Submit a question interaction for AI analysis and user modeling
    """
    try:
        return {
            "status": "success",
            "message": "Interaction recorded successfully",
            "interaction_id": f"{question_id}_{current_user.id}_{datetime.now().timestamp()}"
        }
        
    except Exception as e:
        logger.error(f"Error submitting interaction: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit interaction: {str(e)}")

@router.get("/similar-questions/{question_id}")
async def find_similar_questions(
    question_id: str,
    limit: int = 5,
    current_user: UserRead = Depends(get_current_user)
):
    """
    Find questions similar to the given question ID
    """
    try:
        # Mock similar questions
        similar_questions = [
            {
                "question_id": f"sim_{question_id}_{i}",
                "similarity_score": 0.9 - (i * 0.1),
                "subject": "mathematics",
                "difficulty": 2,
                "question_type": "multiple_choice"
            }
            for i in range(min(limit, 5))
        ]
        
        return {
            "original_question_id": question_id,
            "similar_questions": similar_questions,
            "total_found": len(similar_questions)
        }
        
    except Exception as e:
        logger.error(f"Error finding similar questions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to find similar questions: {str(e)}")

@router.get("/health")
async def ai_health_check():
    """
    Health check for AI services
    """
    try:
        health_status = {
            "status": "healthy",
            "services": {
                "text_processor": "active",
                "image_processor": "active" if image_processor else "inactive",
                "vector_database": "active" if chroma_client else "inactive",
                "user_modeling": "active",
                "recommendation_engine": "active",
                "difficulty_adapter": "active",
                "learning_path_generator": "active",
                "text_embeddings": "active" if text_embedding_service else "inactive",
                "image_embeddings": "active" if image_embedding_service else "inactive",
                "hybrid_embeddings": "active" if hybrid_embedding_service else "inactive",
                "gemini_client": "active" if gemini_client else "inactive"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Test a simple operation
        try:
            test_result = await text_processor.process_text("Test question for health check")
            health_status["test_analysis"] = {
                "success": True,
                "question_type": test_result.question_type.value
            }
        except Exception as e:
            health_status["test_analysis"] = {
                "success": False,
                "error": str(e)
            }
        
        return health_status
        
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/demo/analyze-text", response_model=Dict[str, Any])
async def demo_analyze_text(
    request: Dict[str, str]
):
    """
    Demo endpoint to test text analysis without authentication
    """
    try:
        text = request.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Process the question text
        analysis_result = await text_processor.process_text(text)
        
        return {
            "success": True,
            "analysis": {
                "question_type": analysis_result.question_type.value,
                "difficulty_score": analysis_result.difficulty_score,
                "keywords": analysis_result.keywords[:10],
                "concepts": analysis_result.concepts[:5],
                "word_count": analysis_result.word_count,
                "sentence_count": analysis_result.sentence_count,
                "reading_level": analysis_result.reading_level,
                "has_mathematical_content": len(analysis_result.mathematical_expressions) > 0,
                "mathematical_expressions": analysis_result.mathematical_expressions[:3],
                "language": analysis_result.language_detected,
                "complexity_indicators": analysis_result.complexity_indicators
            }
        }
        
    except Exception as e:
        logger.error(f"Demo text analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/demo/test-recommendation", response_model=Dict[str, Any])
async def demo_test_recommendation():
    """
    Demo endpoint to test recommendation engine without authentication
    """
    try:
        return {
            "success": True,
            "demo_profile": {
                "learning_style": "mixed",
                "subjects": ["mathematics", "computer_science"],
                "weak_areas": ["calculus", "algorithms"],
                "strong_areas": ["algebra", "programming"]
            },
            "recommendations": [
                {
                    "strategy": "adaptive_learning",
                    "reasoning": "Focus on weak areas with personalized difficulty",
                    "confidence": 0.85,
                    "priority": 0.9
                },
                {
                    "strategy": "spaced_repetition",
                    "reasoning": "Review previously mastered concepts",
                    "confidence": 0.75,
                    "priority": 0.7
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Demo recommendation test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation test failed: {str(e)}")

@router.post("/demo/test-embeddings", response_model=Dict[str, Any])
async def demo_test_embeddings():
    """
    Demo endpoint to test embedding services without authentication
    """
    try:
        test_text = "What is the integral of x^2?"
        
        result = {
            "success": True,
            "test_text": test_text,
            "services_available": {
                "text_embeddings": text_embedding_service is not None,
                "image_embeddings": image_embedding_service is not None,
                "hybrid_embeddings": hybrid_embedding_service is not None
            }
        }
        
        # Test text embeddings if available
        if text_embedding_service:
            try:
                embedding = await text_embedding_service.get_single_embedding(test_text)
                result["text_embedding"] = {
                    "dimension": len(embedding),
                    "sample_values": embedding[:5],  # First 5 values
                    "success": True
                }
            except Exception as e:
                result["text_embedding"] = {
                    "success": False,
                    "error": str(e)
                }
        
        # Test hybrid embeddings if available
        if hybrid_embedding_service:
            try:
                hybrid_result = await hybrid_embedding_service.create_question_embedding(
                    question_text=test_text
                )
                if hybrid_result['success']:
                    result["hybrid_embedding"] = {
                        "dimension": len(hybrid_result['hybrid_embedding']),
                        "fusion_method": hybrid_result['fusion_method'],
                        "success": True
                    }
                else:
                    result["hybrid_embedding"] = {
                        "success": False,
                        "error": hybrid_result.get('error', 'Unknown error')
                    }
            except Exception as e:
                result["hybrid_embedding"] = {
                    "success": False,
                    "error": str(e)
                }
        
        return result
        
    except Exception as e:
        logger.error(f"Demo embedding test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Embedding test failed: {str(e)}")

# Additional utility endpoints

@router.get("/models/available")
async def get_available_models(
    current_user: UserRead = Depends(get_current_user)
):
    """Get information about available AI models and their capabilities."""
    try:
        return {
            "text_analysis": {
                "available": text_processor is not None,
                "capabilities": ["question_type_detection", "difficulty_scoring", "keyword_extraction"]
            },
            "image_analysis": {
                "available": image_processor is not None,
                "capabilities": ["ocr", "mathematical_content_detection"]
            },
            "text_embeddings": {
                "available": text_embedding_service is not None,
                "model": "text-embedding-004",
                "dimension": 768
            },
            "image_embeddings": {
                "available": image_embedding_service is not None,
                "model": "gemini-pro-vision",
                "dimension": 768
            },
            "hybrid_embeddings": {
                "available": hybrid_embedding_service is not None,
                "fusion_methods": ["concatenation", "weighted_average", "attention"],
                "dimension": 1536  # for concatenation method
            },
            "llm": {
                "available": gemini_client is not None,
                "model": "gemini-pro",
                "capabilities": ["explanation_generation", "hint_generation", "metadata_extraction"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get available models: {str(e)}")
