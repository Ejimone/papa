from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from fastapi import HTTPException
import logging

from app.models.question import Question, QuestionMetadata, QuestionImage, Explanation, Hint, SimilarQuestion, QuestionType, DifficultyLevel
from app.models.subject import Subject, Topic
from app.schemas.question import (
    QuestionCreate, QuestionUpdate, QuestionFilter, QuestionSearch,
    QuestionMetadataCreate, QuestionMetadataUpdate,
    ExplanationCreate, HintCreate
)
from app.services.base import BaseService

logger = logging.getLogger(__name__)

class QuestionService(BaseService[Question, QuestionCreate, QuestionUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Question, db)
    
    async def get_with_details(self, question_id: int) -> Optional[Question]:
        """Get question with all related data (metadata, images, explanations, hints)"""
        try:
            query = select(Question).options(
                selectinload(Question.question_metadata),
                selectinload(Question.images),
                selectinload(Question.explanations),
                selectinload(Question.hints),
                selectinload(Question.subject),
                selectinload(Question.topic)
            ).where(Question.id == question_id)
            
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting question with details {question_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def get_filtered(
        self,
        filters: QuestionFilter,
        skip: int = 0,
        limit: int = 20
    ) -> List[Question]:
        """Get questions with advanced filtering"""
        try:
            query = select(Question).options(
                selectinload(Question.subject),
                selectinload(Question.topic)
            )
            
            # Apply filters
            conditions = []
            
            if filters.subject_ids:
                conditions.append(Question.subject_id.in_(filters.subject_ids))
            
            if filters.topic_ids:
                conditions.append(Question.topic_id.in_(filters.topic_ids))
            
            if filters.question_types:
                conditions.append(Question.question_type.in_(filters.question_types))
            
            if filters.difficulty_levels:
                conditions.append(Question.difficulty_level.in_(filters.difficulty_levels))
            
            if filters.min_points:
                conditions.append(Question.points >= filters.min_points)
            
            if filters.max_points:
                conditions.append(Question.points <= filters.max_points)
            
            if filters.is_verified is not None:
                conditions.append(Question.is_verified == filters.is_verified)
            
            if filters.min_priority_score:
                conditions.append(Question.priority_score >= filters.min_priority_score)
            
            if filters.created_after:
                conditions.append(Question.created_at >= filters.created_after)
            
            if filters.created_before:
                conditions.append(Question.created_at <= filters.created_before)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            # Add ordering and pagination
            query = query.order_by(Question.priority_score.desc(), Question.created_at.desc())
            query = query.offset(skip).limit(limit)
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting filtered questions: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def search_questions(self, search_params: QuestionSearch) -> Dict[str, Any]:
        """Search questions with text search and filters"""
        try:
            query = select(Question).options(
                selectinload(Question.subject),
                selectinload(Question.topic)
            )
            
            # Text search in title and content
            if search_params.query:
                search_condition = or_(
                    Question.title.ilike(f"%{search_params.query}%"),
                    Question.content.ilike(f"%{search_params.query}%")
                )
                query = query.where(search_condition)
            
            # Apply filters if provided
            if search_params.filters:
                filtered_query = await self._apply_search_filters(query, search_params.filters)
                query = filtered_query
            
            # Count total results
            count_query = select(func.count(Question.id))
            if search_params.query:
                count_query = count_query.where(search_condition)
            if search_params.filters:
                count_query = await self._apply_search_filters(count_query, search_params.filters)
            
            total_count = await self.db.execute(count_query)
            total = total_count.scalar()
            
            # Apply ordering and pagination
            query = query.order_by(Question.priority_score.desc())
            query = query.offset(search_params.offset).limit(search_params.limit)
            
            result = await self.db.execute(query)
            questions = result.scalars().all()
            
            return {
                "questions": questions,
                "total_count": total,
                "search_time_ms": 0.0,  # Would be calculated in a real implementation
                "suggestions": []  # Would contain search suggestions
            }
        except Exception as e:
            logger.error(f"Error searching questions: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def _apply_search_filters(self, query, filters: QuestionFilter):
        """Helper method to apply filters to a query"""
        conditions = []
        
        if filters.subject_ids:
            conditions.append(Question.subject_id.in_(filters.subject_ids))
        
        if filters.difficulty_levels:
            conditions.append(Question.difficulty_level.in_(filters.difficulty_levels))
        
        if filters.is_verified is not None:
            conditions.append(Question.is_verified == filters.is_verified)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        return query
    
    async def get_by_subject(self, subject_id: int, skip: int = 0, limit: int = 20) -> List[Question]:
        """Get questions by subject"""
        try:
            query = select(Question).options(
                selectinload(Question.topic)
            ).where(Question.subject_id == subject_id)
            
            query = query.order_by(Question.priority_score.desc())
            query = query.offset(skip).limit(limit)
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting questions by subject {subject_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def get_by_topic(self, topic_id: int, skip: int = 0, limit: int = 20) -> List[Question]:
        """Get questions by topic"""
        try:
            query = select(Question).options(
                selectinload(Question.subject)
            ).where(Question.topic_id == topic_id)
            
            query = query.order_by(Question.priority_score.desc())
            query = query.offset(skip).limit(limit)
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting questions by topic {topic_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def get_random_questions(
        self,
        count: int = 10,
        filters: Optional[QuestionFilter] = None
    ) -> List[Question]:
        """Get random questions for practice"""
        try:
            query = select(Question).options(
                selectinload(Question.subject),
                selectinload(Question.topic)
            )
            
            # Apply filters if provided
            if filters:
                if filters.subject_ids:
                    query = query.where(Question.subject_id.in_(filters.subject_ids))
                if filters.difficulty_levels:
                    query = query.where(Question.difficulty_level.in_(filters.difficulty_levels))
                if filters.question_types:
                    query = query.where(Question.question_type.in_(filters.question_types))
            
            # Order randomly and limit
            query = query.order_by(func.random()).limit(count)
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting random questions: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def get_similar_questions(self, question_id: int, limit: int = 5) -> List[Question]:
        """Get similar questions"""
        try:
            # Get similar question relationships
            query = select(Question).join(
                SimilarQuestion, 
                Question.id == SimilarQuestion.similar_question_id
            ).where(
                SimilarQuestion.original_question_id == question_id
            ).order_by(
                SimilarQuestion.similarity_score.desc()
            ).limit(limit)
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting similar questions for {question_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def add_metadata(self, question_id: int, metadata_data: QuestionMetadataCreate) -> QuestionMetadata:
        """Add metadata to a question"""
        try:
            # Check if question exists
            question = await self.get(question_id)
            if not question:
                raise HTTPException(status_code=404, detail="Question not found")
            
            # Create metadata
            metadata = QuestionMetadata(**metadata_data.dict(), question_id=question_id)
            self.db.add(metadata)
            await self.db.commit()
            await self.db.refresh(metadata)
            return metadata
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error adding metadata to question {question_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def add_explanation(self, question_id: int, explanation_data: ExplanationCreate) -> Explanation:
        """Add an explanation to a question"""
        try:
            # Check if question exists
            question = await self.get(question_id)
            if not question:
                raise HTTPException(status_code=404, detail="Question not found")
            
            # Create explanation
            explanation = Explanation(**explanation_data.dict(), question_id=question_id)
            self.db.add(explanation)
            await self.db.commit()
            await self.db.refresh(explanation)
            return explanation
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error adding explanation to question {question_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def add_hint(self, question_id: int, hint_data: HintCreate) -> Hint:
        """Add a hint to a question"""
        try:
            # Check if question exists
            question = await self.get(question_id)
            if not question:
                raise HTTPException(status_code=404, detail="Question not found")
            
            # Create hint
            hint = Hint(**hint_data.dict(), question_id=question_id)
            self.db.add(hint)
            await self.db.commit()
            await self.db.refresh(hint)
            return hint
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error adding hint to question {question_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def get_question_stats(self) -> Dict[str, Any]:
        """Get question statistics"""
        try:
            # Total questions
            total_query = select(func.count(Question.id))
            total_result = await self.db.execute(total_query)
            total_questions = total_result.scalar()
            
            # Questions by difficulty
            difficulty_query = select(
                Question.difficulty_level,
                func.count(Question.id)
            ).group_by(Question.difficulty_level)
            difficulty_result = await self.db.execute(difficulty_query)
            by_difficulty = {row[0]: row[1] for row in difficulty_result}
            
            # Questions by type
            type_query = select(
                Question.question_type,
                func.count(Question.id)
            ).group_by(Question.question_type)
            type_result = await self.db.execute(type_query)
            by_type = {row[0]: row[1] for row in type_result}
            
            # Verified questions
            verified_query = select(func.count(Question.id)).where(Question.is_verified == True)
            verified_result = await self.db.execute(verified_query)
            verified_count = verified_result.scalar()
            
            return {
                "total_questions": total_questions,
                "by_difficulty": by_difficulty,
                "by_type": by_type,
                "verified_count": verified_count,
                "verified_percentage": (verified_count / total_questions * 100) if total_questions > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting question stats: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def create_from_dict(self, question_data: Dict[str, Any]) -> Question:
        """Create question from dictionary data (useful for AI-generated questions)"""
        try:
            # Extract question data
            question_create = QuestionCreate(
                title=question_data.get('title', ''),
                content=question_data.get('content', ''),
                answer=question_data.get('answer', ''),
                question_type=question_data.get('question_type', 'short_answer'),
                difficulty_level=question_data.get('difficulty_level', 'intermediate'),
                subject_id=question_data.get('subject_id'),
                topic_id=question_data.get('topic_id'),
                points=question_data.get('points', 1),
                time_limit=question_data.get('time_limit'),
                options=question_data.get('options', []),
                created_by=question_data.get('created_by')
            )
            
            # Create the question
            question = await self.create(question_create)
            
            # Add metadata if provided
            if question_data.get('keywords') or question_data.get('source'):
                metadata_create = QuestionMetadataCreate(
                    tags=question_data.get('keywords', []),
                    source=question_data.get('source', 'AI_extracted'),
                    priority_score=1.0,
                    frequency_score=1.0
                )
                await self.add_metadata(question.id, metadata_create)
            
            return question
            
        except Exception as e:
            logger.error(f"Error creating question from dict: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create question")
