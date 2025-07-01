from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Dict, Any, Optional
import asyncio
import logging
from datetime import datetime

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

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize AI services (these would typically be dependency injected)
text_processor = TextProcessor(use_advanced_nlp=False)
image_processor = ImageProcessor(use_mock=settings.DEBUG)
chroma_client = ChromaDBClient(in_memory=settings.DEBUG)
vector_queries = VectorQueries(chroma_client)
user_modeling_service = UserModelingService()
recommendation_engine = RecommendationEngine(vector_queries, None)  # No embedding service for now
difficulty_adapter = DifficultyAdapter(AdaptationStrategy.MODERATE)
learning_path_generator = LearningPathGenerator(difficulty_adapter)

# Pydantic schemas for AI endpoints
from pydantic import BaseModel
from enum import Enum

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
        # Get user profile (this would typically come from the database)
        # For now, we'll create a mock profile
        user_profile = await user_modeling_service.get_or_create_user_profile(
            user_id=str(current_user.id),
            academic_level="undergraduate"
        )
        
        # Generate recommendations
        recommendations = await recommendation_engine.generate_personalized_recommendations(
            user_profile=user_profile,
            subject=request.subject,
            limit=request.limit
        )
        
        # Convert to response format
        response_recommendations = []
        for rec in recommendations:
            response_recommendations.append(RecommendationResponse(
                question_id=rec.question_id,
                recommendation_strategy=rec.recommendation_strategy,
                confidence_score=rec.confidence_score,
                reasoning=rec.reasoning,
                estimated_difficulty=rec.estimated_difficulty
            ))
        
        return response_recommendations
        
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
        # Get user profile
        user_profile = await user_modeling_service.get_or_create_user_profile(
            user_id=str(current_user.id),
            academic_level="undergraduate"
        )
        
        # Convert string enums to actual enums
        try:
            path_type = PathType(request.path_type.lower())
        except ValueError:
            path_type = PathType.SEQUENTIAL
            
        objectives = []
        for obj_str in request.objectives:
            try:
                objectives.append(LearningObjective(obj_str.lower()))
            except ValueError:
                continue
                
        if not objectives:
            objectives = [LearningObjective.MASTERY]
        
        # Generate learning path
        learning_path = await learning_path_generator.generate_personalized_path(
            user_profile=user_profile,
            subject=request.subject,
            objectives=objectives,
            path_type=path_type,
            time_constraints={"max_sessions": request.max_sessions}
        )
        
        # Convert sessions to serializable format
        sessions_data = []
        for session in learning_path.sessions:
            session_data = {
                "session_type": session.session_type,
                "total_duration": session.total_duration,
                "steps_count": len(session.steps),
                "focus_areas": session.focus_areas,
                "difficulty_range": session.difficulty_range,
                "steps": [
                    {
                        "topic_id": step.topic_id,
                        "topic_name": step.topic_name,
                        "difficulty": step.difficulty,
                        "duration": step.estimated_duration,
                        "question_count": step.question_count,
                        "step_type": step.step_type
                    }
                    for step in session.steps
                ]
            }
            sessions_data.append(session_data)
        
        return LearningPathResponse(
            path_id=learning_path.id,
            subject=learning_path.subject,
            path_type=learning_path.path_type.value,
            total_sessions=len(learning_path.sessions),
            total_duration_minutes=learning_path.total_duration,
            estimated_completion_days=(learning_path.estimated_completion - learning_path.created_at).days,
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
        # Get user profile and recent interactions
        user_profile = await user_modeling_service.get_or_create_user_profile(
            user_id=str(current_user.id),
            academic_level="undergraduate"
        )
        
        # Get recent interactions (this would come from the database)
        # For now, we'll use mock data or empty list
        recent_interactions = user_profile.recent_interactions[-request.recent_interactions_count:] if user_profile.recent_interactions else []
        
        # Analyze for difficulty adaptation
        adjustment = await difficulty_adapter.adapt_difficulty(
            user_profile=user_profile,
            recent_interactions=recent_interactions,
            subject=request.subject
        )
        
        if adjustment:
            return DifficultyAdaptationResponse(
                current_difficulty=adjustment.old_difficulty,
                recommended_difficulty=adjustment.new_difficulty,
                confidence=adjustment.confidence.value,
                reasoning=adjustment.reasoning,
                should_adapt=True
            )
        else:
            return DifficultyAdaptationResponse(
                current_difficulty=user_profile.preferred_difficulty,
                recommended_difficulty=None,
                confidence="low",
                reasoning=["Insufficient data for reliable adaptation"],
                should_adapt=False
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
        # Get user profile
        user_profile = await user_modeling_service.get_or_create_user_profile(
            user_id=str(current_user.id),
            academic_level="undergraduate"
        )
        
        # Get learning patterns
        if user_profile.recent_interactions:
            learning_patterns = await user_modeling_service.analyze_learning_patterns(
                user_profile.recent_interactions
            )
        else:
            learning_patterns = {}
        
        return {
            "user_id": user_profile.user_id,
            "performance_level": user_profile.performance_level.value,
            "learning_style": user_profile.learning_style,
            "preferred_difficulty": user_profile.preferred_difficulty,
            "strong_subjects": user_profile.strong_subjects,
            "weak_subjects": user_profile.weak_subjects,
            "study_preferences": user_profile.study_preferences,
            "learning_patterns": learning_patterns,
            "total_interactions": len(user_profile.recent_interactions)
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
        # Create interaction record
        interaction = QuestionInteraction(
            question_id=question_id,
            subject=subject,
            difficulty=difficulty,
            is_correct=is_correct,
            time_taken=time_taken,
            attempts=attempts,
            hint_used=hint_used,
            timestamp=datetime.now()
        )
        
        # Update user profile with the interaction
        await user_modeling_service.update_user_profile_with_interaction(
            user_id=str(current_user.id),
            interaction=interaction
        )
        
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
        # This would typically query the vector database
        # For now, return mock similar questions
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
                "learning_path_generator": "active"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Test a simple operation
        test_result = await text_processor.process_text("Test question for health check")
        health_status["test_analysis"] = {
            "success": True,
            "question_type": test_result.question_type.value
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
                "keywords": analysis_result.keywords[:10],  # Limit to 10 keywords
                "concepts": analysis_result.concepts[:5],  # Limit to 5 concepts
                "word_count": analysis_result.word_count,
                "sentence_count": analysis_result.sentence_count,
                "reading_level": analysis_result.reading_level,
                "has_mathematical_content": len(analysis_result.mathematical_expressions) > 0,
                "mathematical_expressions": analysis_result.mathematical_expressions[:3],  # Limit to 3
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
        # Create a dummy user profile for testing
        from app.ai.personalization.user_modeling import UserProfile, LearningStyle, PerformanceLevel
        
        dummy_profile = UserProfile(
            user_id="demo_user",
            academic_level="undergraduate",
            subjects=["mathematics", "computer_science"],
            learning_style=LearningStyle.MIXED,
            study_goals=["mastery", "exam_prep"],
            performance_levels={"mathematics": PerformanceLevel.DEVELOPING},
            weak_areas=["calculus", "algorithms"],
            strong_areas=["algebra", "programming"]
        )
        
        # Get recommendations
        recommendations = await recommendation_engine.generate_personalized_recommendations(
            user_profile=dummy_profile,
            subject_filter="mathematics",
            limit=3
        )
        
        return {
            "success": True,
            "demo_profile": {
                "learning_style": dummy_profile.learning_style.value,
                "subjects": dummy_profile.subjects,
                "weak_areas": dummy_profile.weak_areas,
                "strong_areas": dummy_profile.strong_areas
            },
            "recommendations": [
                {
                    "strategy": rec.recommendation_strategy,
                    "reasoning": rec.reasoning,
                    "confidence": rec.confidence_score,
                    "priority": rec.priority_score
                }
                for rec in recommendations
            ]
        }
        
    except Exception as e:
        logger.error(f"Demo recommendation test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation test failed: {str(e)}")
