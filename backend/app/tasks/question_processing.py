from celery import shared_task
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_question_embeddings(self, question_id: int) -> Dict[str, Any]:
    """
    Process a question to generate embeddings and store in vector database
    """
    try:
        from app.ai.embeddings.text_embeddings import generate_text_embedding
        from app.ai.vector_db.client import get_vector_db_client
        from app.repositories.question_repository import QuestionRepository
        from app.core.database import AsyncSessionLocal
        
        # Get question data
        async with AsyncSessionLocal() as session:
            question_repo = QuestionRepository(session)
            question = await question_repo.get(question_id)
            
            if not question:
                raise ValueError(f"Question with ID {question_id} not found")
            
            # Generate embedding
            text_content = f"{question.title} {question.content}"
            if question.question_metadata and question.question_metadata.keywords:
                text_content += " " + " ".join(question.question_metadata.keywords)
            
            embedding = await generate_text_embedding(text_content)
            
            # Store in vector database
            vector_client = get_vector_db_client()
            vector_id = await vector_client.store_question_embedding(
                question_id=question_id,
                embedding=embedding,
                metadata={
                    "subject_id": question.subject_id,
                    "topic_id": question.topic_id,
                    "difficulty_level": question.difficulty_level.value,
                    "question_type": question.question_type.value,
                    "priority_score": question.priority_score
                }
            )
            
            # Update question with vector ID
            await question_repo.update(
                question_id,
                {
                    "vector_id": vector_id,
                    "is_processed_for_embedding": True,
                    "processing_error_log": None
                }
            )
            
        return {
            "status": "success",
            "question_id": question_id,
            "vector_id": vector_id,
            "processed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing question {question_id}: {str(e)}")
        
        # Update question with error
        try:
            async with AsyncSessionLocal() as session:
                question_repo = QuestionRepository(session)
                await question_repo.update(
                    question_id,
                    {
                        "is_processed_for_embedding": False,
                        "processing_error_log": str(e)
                    }
                )
        except Exception as update_error:
            logger.error(f"Failed to update question error log: {str(update_error)}")
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying question processing for ID {question_id}")
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        
        return {
            "status": "failed",
            "question_id": question_id,
            "error": str(e)
        }

@shared_task(bind=True)
def process_question_ocr(self, question_id: int, image_urls: List[str]) -> Dict[str, Any]:
    """
    Process images associated with a question using OCR
    """
    try:
        from app.ai.processing.image_processor import extract_text_from_image
        from app.repositories.question_repository import QuestionRepository
        from app.core.database import AsyncSessionLocal
        
        results = []
        
        async with AsyncSessionLocal() as session:
            question_repo = QuestionRepository(session)
            
            for image_url in image_urls:
                try:
                    # Extract text from image
                    ocr_result = await extract_text_from_image(image_url)
                    
                    # Store OCR result in question_images table
                    image_data = {
                        "question_id": question_id,
                        "image_url": image_url,
                        "ocr_text": ocr_result.get("text", ""),
                        "ocr_confidence": ocr_result.get("confidence", 0.0),
                        "is_processed": True,
                        "processed_at": datetime.utcnow()
                    }
                    
                    # This would need a QuestionImageRepository
                    # await question_image_repo.create(image_data)
                    
                    results.append({
                        "image_url": image_url,
                        "status": "success",
                        "text_length": len(ocr_result.get("text", "")),
                        "confidence": ocr_result.get("confidence", 0.0)
                    })
                    
                except Exception as img_error:
                    logger.error(f"Error processing image {image_url}: {str(img_error)}")
                    results.append({
                        "image_url": image_url,
                        "status": "failed",
                        "error": str(img_error)
                    })
        
        return {
            "status": "completed",
            "question_id": question_id,
            "results": results,
            "processed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in OCR processing for question {question_id}: {str(e)}")
        return {
            "status": "failed",
            "question_id": question_id,
            "error": str(e)
        }

@shared_task(bind=True)
def generate_question_explanation(self, question_id: int, explanation_type: str = "step_by_step") -> Dict[str, Any]:
    """
    Generate AI explanation for a question
    """
    try:
        from app.ai.llm.gemini_client import generate_explanation
        from app.repositories.question_repository import QuestionRepository
        from app.core.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as session:
            question_repo = QuestionRepository(session)
            question = await question_repo.get(question_id)
            
            if not question:
                raise ValueError(f"Question with ID {question_id} not found")
            
            # Generate explanation using AI
            explanation_content = await generate_explanation(
                question_text=question.content,
                question_type=question.question_type.value,
                difficulty_level=question.difficulty_level.value,
                explanation_type=explanation_type,
                answer=question.answer
            )
            
            # Store explanation
            explanation_data = {
                "question_id": question_id,
                "content": explanation_content,
                "explanation_type": explanation_type,
                "is_ai_generated": True,
                "ai_model": "gemini-pro",
                "confidence_score": 0.85  # This would come from the AI response
            }
            
            # This would need an ExplanationRepository
            # explanation_id = await explanation_repo.create(explanation_data)
            
        return {
            "status": "success",
            "question_id": question_id,
            "explanation_type": explanation_type,
            "explanation_length": len(explanation_content),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating explanation for question {question_id}: {str(e)}")
        return {
            "status": "failed",
            "question_id": question_id,
            "error": str(e)
        }

@shared_task(bind=True)
def generate_question_hints(self, question_id: int, num_hints: int = 3) -> Dict[str, Any]:
    """
    Generate progressive hints for a question
    """
    try:
        from app.ai.llm.gemini_client import generate_hints
        from app.repositories.question_repository import QuestionRepository
        from app.core.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as session:
            question_repo = QuestionRepository(session)
            question = await question_repo.get(question_id)
            
            if not question:
                raise ValueError(f"Question with ID {question_id} not found")
            
            # Generate hints using AI
            hints = await generate_hints(
                question_text=question.content,
                question_type=question.question_type.value,
                difficulty_level=question.difficulty_level.value,
                num_hints=num_hints,
                answer=question.answer
            )
            
            # Store hints
            created_hints = []
            for i, hint_content in enumerate(hints, 1):
                hint_data = {
                    "question_id": question_id,
                    "level": i,
                    "content": hint_content,
                    "hint_type": "concept",
                    "is_ai_generated": True,
                    "ai_model": "gemini-pro"
                }
                
                # This would need a HintRepository
                # hint_id = await hint_repo.create(hint_data)
                created_hints.append(hint_data)
            
        return {
            "status": "success",
            "question_id": question_id,
            "hints_created": len(created_hints),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating hints for question {question_id}: {str(e)}")
        return {
            "status": "failed",
            "question_id": question_id,
            "error": str(e)
        }

@shared_task(bind=True)
def find_similar_questions(self, question_id: int, similarity_threshold: float = 0.7) -> Dict[str, Any]:
    """
    Find similar questions using vector similarity search
    """
    try:
        from app.ai.vector_db.client import get_vector_db_client
        from app.repositories.question_repository import QuestionRepository
        from app.core.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as session:
            question_repo = QuestionRepository(session)
            question = await question_repo.get(question_id)
            
            if not question or not question.vector_id:
                raise ValueError(f"Question {question_id} not found or not processed for embeddings")
            
            # Find similar questions
            vector_client = get_vector_db_client()
            similar_questions = await vector_client.find_similar_questions(
                vector_id=question.vector_id,
                threshold=similarity_threshold,
                limit=10
            )
            
            # Store similarity relationships
            stored_similarities = []
            for similar in similar_questions:
                similarity_data = {
                    "original_question_id": question_id,
                    "similar_question_id": similar["question_id"],
                    "similarity_score": similar["similarity_score"],
                    "similarity_type": "content",
                    "algorithm_used": "vector_embedding",
                    "calculated_at": datetime.utcnow(),
                    "is_verified": False
                }
                
                # This would need a SimilarQuestionRepository
                # await similar_question_repo.create(similarity_data)
                stored_similarities.append(similarity_data)
            
        return {
            "status": "success",
            "question_id": question_id,
            "similar_questions_found": len(stored_similarities),
            "average_similarity": sum(s["similarity_score"] for s in stored_similarities) / len(stored_similarities) if stored_similarities else 0,
            "processed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error finding similar questions for {question_id}: {str(e)}")
        return {
            "status": "failed",
            "question_id": question_id,
            "error": str(e)
        }

@shared_task(bind=True)
def extract_question_metadata(self, question_id: int) -> Dict[str, Any]:
    """
    Extract and analyze metadata from question content
    """
    try:
        from app.ai.processing.metadata_extractor import extract_metadata
        from app.repositories.question_repository import QuestionRepository
        from app.core.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as session:
            question_repo = QuestionRepository(session)
            question = await question_repo.get(question_id)
            
            if not question:
                raise ValueError(f"Question with ID {question_id} not found")
            
            # Extract metadata using AI
            metadata = await extract_metadata(
                question_text=question.content,
                question_type=question.question_type.value,
                existing_metadata=question.question_metadata.__dict__ if question.question_metadata else {}
            )
            
            # Update or create metadata
            metadata_data = {
                "question_id": question_id,
                "keywords": metadata.get("keywords", []),
                "concepts": metadata.get("concepts", []),
                "prerequisites": metadata.get("prerequisites", []),
                "learning_objectives": metadata.get("learning_objectives", []),
                "clarity_score": metadata.get("clarity_score", 0.0),
                "completeness_score": metadata.get("completeness_score", 0.0),
                "difficulty_confidence": metadata.get("difficulty_confidence", 0.0)
            }
            
            # This would need a QuestionMetadataRepository
            # await question_metadata_repo.upsert(metadata_data)
            
        return {
            "status": "success",
            "question_id": question_id,
            "metadata_extracted": True,
            "keywords_count": len(metadata.get("keywords", [])),
            "concepts_count": len(metadata.get("concepts", [])),
            "processed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error extracting metadata for question {question_id}: {str(e)}")
        return {
            "status": "failed",
            "question_id": question_id,
            "error": str(e)
        }

@shared_task(bind=True)
def process_question_batch(self, question_ids: List[int], processing_steps: List[str]) -> Dict[str, Any]:
    """
    Process multiple questions in batch
    """
    try:
        results = {
            "total_questions": len(question_ids),
            "successful": 0,
            "failed": 0,
            "results": [],
            "processing_steps": processing_steps
        }
        
        for question_id in question_ids:
            question_results = {"question_id": question_id, "steps": {}}
            
            try:
                # Process each step for the question
                for step in processing_steps:
                    if step == "embeddings":
                        result = process_question_embeddings.delay(question_id)
                        question_results["steps"]["embeddings"] = "queued"
                    elif step == "metadata":
                        result = extract_question_metadata.delay(question_id)
                        question_results["steps"]["metadata"] = "queued"
                    elif step == "explanation":
                        result = generate_question_explanation.delay(question_id)
                        question_results["steps"]["explanation"] = "queued"
                    elif step == "hints":
                        result = generate_question_hints.delay(question_id)
                        question_results["steps"]["hints"] = "queued"
                    elif step == "similar":
                        result = find_similar_questions.delay(question_id)
                        question_results["steps"]["similar"] = "queued"
                
                results["successful"] += 1
                question_results["status"] = "queued"
                
            except Exception as e:
                logger.error(f"Error processing question {question_id}: {str(e)}")
                results["failed"] += 1
                question_results["status"] = "failed"
                question_results["error"] = str(e)
            
            results["results"].append(question_results)
        
        return results
        
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "processed_at": datetime.utcnow().isoformat()
        }

@shared_task(bind=True)
def update_question_priority_scores(self) -> Dict[str, Any]:
    """
    Update priority scores for all questions based on various factors
    """
    try:
        from app.repositories.question_repository import QuestionRepository
        from app.core.database import AsyncSessionLocal
        from app.ai.utils.similarity import calculate_priority_score
        
        updated_count = 0
        error_count = 0
        
        async with AsyncSessionLocal() as session:
            question_repo = QuestionRepository(session)
            
            # Get all questions that need priority score updates
            questions = await question_repo.get_all(filters={"is_active": True})
            
            for question in questions:
                try:
                    # Calculate new priority score based on various factors
                    priority_score = await calculate_priority_score(
                        question_id=question.id,
                        session=session
                    )
                    
                    # Update question
                    await question_repo.update(
                        question.id,
                        {"priority_score": priority_score}
                    )
                    
                    updated_count += 1
                    
                except Exception as e:
                    logger.error(f"Error updating priority for question {question.id}: {str(e)}")
                    error_count += 1
        
        return {
            "status": "completed",
            "updated_count": updated_count,
            "error_count": error_count,
            "processed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating priority scores: {str(e)}")
        return {
            "status": "failed",
            "error": str(e)
        }

# Periodic task to clean up old processing logs
@shared_task(bind=True)
def cleanup_processing_logs(self, days_old: int = 30) -> Dict[str, Any]:
    """
    Clean up old processing error logs and temporary data
    """
    try:
        from app.repositories.question_repository import QuestionRepository
        from app.core.database import AsyncSessionLocal
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        cleaned_count = 0
        
        async with AsyncSessionLocal() as session:
            question_repo = QuestionRepository(session)
            
            # Clear old error logs
            questions_with_old_errors = await question_repo.get_all(
                filters={
                    "processing_error_log__isnot": None,
                    "updated_at__lt": cutoff_date
                }
            )
            
            for question in questions_with_old_errors:
                await question_repo.update(
                    question.id,
                    {"processing_error_log": None}
                )
                cleaned_count += 1
        
        return {
            "status": "completed",
            "cleaned_count": cleaned_count,
            "cutoff_date": cutoff_date.isoformat(),
            "processed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up processing logs: {str(e)}")
        return {
            "status": "failed",
            "error": str(e)
        }
