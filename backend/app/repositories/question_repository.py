from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, or_, func, desc, asc, text
from datetime import datetime

from app.models.question import (
    Question, QuestionMetadata, QuestionImage, Explanation, 
    Hint, SimilarQuestion, QuestionType, DifficultyLevel
)
from app.models.subject import Subject, Topic
from app.schemas.question import (
    QuestionCreate, QuestionUpdate, QuestionFilter,
    QuestionMetadataCreate, QuestionMetadataUpdate,
    QuestionImageCreate, QuestionImageUpdate,
    ExplanationCreate, ExplanationUpdate,
    HintCreate, HintUpdate,
    SimilarQuestionCreate
)
from app.repositories.base import BaseRepository

class QuestionRepository(BaseRepository[Question, QuestionCreate, QuestionUpdate]):
    
    # Basic question operations
    async def get_by_title(self, db: AsyncSession, *, title: str) -> Optional[Question]:
        return await self.get_by_attribute(db, attribute="title", value=title)

    async def get_by_subject(self, db: AsyncSession, *, subject_id: int, skip: int = 0, limit: int = 100) -> List[Question]:
        return await self.get_multi_by_attribute(db, attribute="subject_id", value=subject_id, skip=skip, limit=limit)

    async def get_by_topic(self, db: AsyncSession, *, topic_id: int, skip: int = 0, limit: int = 100) -> List[Question]:
        return await self.get_multi_by_attribute(db, attribute="topic_id", value=topic_id, skip=skip, limit=limit)

    async def get_by_difficulty(self, db: AsyncSession, *, difficulty: DifficultyLevel, skip: int = 0, limit: int = 100) -> List[Question]:
        return await self.get_multi_by_attribute(db, attribute="difficulty_level", value=difficulty, skip=skip, limit=limit)

    async def get_by_type(self, db: AsyncSession, *, question_type: QuestionType, skip: int = 0, limit: int = 100) -> List[Question]:
        return await self.get_multi_by_attribute(db, attribute="question_type", value=question_type, skip=skip, limit=limit)

    async def get_with_details(self, db: AsyncSession, *, question_id: int) -> Optional[Question]:
        """Get question with all related data loaded"""
        statement = (
            select(Question)
            .options(
                selectinload(Question.subject),
                selectinload(Question.topic),
                selectinload(Question.question_metadata),
                selectinload(Question.images),
                selectinload(Question.explanations),
                selectinload(Question.hints)
            )
            .where(Question.id == question_id)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def get_active_questions(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[Question]:
        """Get only active questions"""
        statement = select(Question).where(Question.is_active == True).offset(skip).limit(limit)
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_verified_questions(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[Question]:
        """Get only verified questions"""
        statement = select(Question).where(Question.is_verified == True).offset(skip).limit(limit)
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_high_priority_questions(self, db: AsyncSession, *, min_priority: float = 0.7, skip: int = 0, limit: int = 100) -> List[Question]:
        """Get questions with high priority score"""
        statement = (
            select(Question)
            .where(Question.priority_score >= min_priority)
            .order_by(desc(Question.priority_score))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()

    async def search_questions(self, db: AsyncSession, *, filters: QuestionFilter, skip: int = 0, limit: int = 100) -> tuple[List[Question], int]:
        """Advanced search with filters"""
        query = select(Question)
        count_query = select(func.count(Question.id))
        
        conditions = []
        
        if filters.subject_ids:
            conditions.append(Question.subject_id.in_(filters.subject_ids))
        
        if filters.topic_ids:
            conditions.append(Question.topic_id.in_(filters.topic_ids))
        
        if filters.question_types:
            conditions.append(Question.question_type.in_(filters.question_types))
        
        if filters.difficulty_levels:
            conditions.append(Question.difficulty_level.in_(filters.difficulty_levels))
        
        if filters.min_points is not None:
            conditions.append(Question.points >= filters.min_points)
        
        if filters.max_points is not None:
            conditions.append(Question.points <= filters.max_points)
        
        if filters.is_verified is not None:
            conditions.append(Question.is_verified == filters.is_verified)
        
        if filters.min_priority_score is not None:
            conditions.append(Question.priority_score >= filters.min_priority_score)
        
        if filters.created_after:
            conditions.append(Question.created_at >= filters.created_after)
        
        if filters.created_before:
            conditions.append(Question.created_at <= filters.created_before)
        
        # Handle metadata filters if needed
        if any([filters.tags, filters.keywords, filters.year, filters.semester, filters.institution, filters.exam_type]):
            query = query.join(QuestionMetadata)
            count_query = count_query.join(QuestionMetadata)
            
            if filters.tags:
                conditions.append(QuestionMetadata.tags.op('@>')([filters.tags]))
            
            if filters.keywords:
                conditions.append(QuestionMetadata.keywords.op('@>')([filters.keywords]))
            
            if filters.year:
                conditions.append(QuestionMetadata.year == filters.year)
            
            if filters.semester:
                conditions.append(QuestionMetadata.semester == filters.semester)
            
            if filters.institution:
                conditions.append(QuestionMetadata.institution.ilike(f"%{filters.institution}%"))
            
            if filters.exam_type:
                conditions.append(QuestionMetadata.exam_type.ilike(f"%{filters.exam_type}%"))
        
        # Handle relationship filters
        if filters.has_explanation is not None:
            if filters.has_explanation:
                query = query.join(Explanation)
                count_query = count_query.join(Explanation)
            else:
                query = query.outerjoin(Explanation).where(Explanation.id.is_(None))
                count_query = count_query.outerjoin(Explanation).where(Explanation.id.is_(None))
        
        if filters.has_hints is not None:
            if filters.has_hints:
                query = query.join(Hint)
                count_query = count_query.join(Hint)
            else:
                query = query.outerjoin(Hint).where(Hint.id.is_(None))
                count_query = count_query.outerjoin(Hint).where(Hint.id.is_(None))
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Execute count query
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        # Execute main query
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        questions = result.scalars().all()
        
        return questions, total_count

    async def text_search(self, db: AsyncSession, *, search_text: str, skip: int = 0, limit: int = 100) -> List[Question]:
        """Full-text search on question content and title"""
        # PostgreSQL full-text search
        statement = (
            select(Question)
            .where(
                or_(
                    Question.title.ilike(f"%{search_text}%"),
                    Question.content.ilike(f"%{search_text}%")
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_random_questions(self, db: AsyncSession, *, count: int = 10, subject_id: Optional[int] = None) -> List[Question]:
        """Get random questions for practice"""
        query = select(Question).where(Question.is_active == True)
        
        if subject_id:
            query = query.where(Question.subject_id == subject_id)
        
        query = query.order_by(func.random()).limit(count)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_questions_by_vector_ids(self, db: AsyncSession, *, vector_ids: List[str]) -> List[Question]:
        """Get questions by their vector database IDs"""
        statement = select(Question).where(Question.vector_id.in_(vector_ids))
        result = await db.execute(statement)
        return result.scalars().all()

    async def update_priority_score(self, db: AsyncSession, *, question_id: int, priority_score: float) -> Optional[Question]:
        """Update question priority score"""
        question = await self.get(db, id=question_id)
        if question:
            question.priority_score = priority_score
            db.add(question)
            await db.flush()
            await db.refresh(question)
        return question

    async def update_vector_id(self, db: AsyncSession, *, question_id: int, vector_id: str) -> Optional[Question]:
        """Update question vector database ID"""
        question = await self.get(db, id=question_id)
        if question:
            question.vector_id = vector_id
            question.is_processed_for_embedding = True
            db.add(question)
            await db.flush()
            await db.refresh(question)
        return question

    async def mark_as_processed(self, db: AsyncSession, *, question_id: int, error_log: Optional[str] = None) -> Optional[Question]:
        """Mark question as processed for embedding"""
        question = await self.get(db, id=question_id)
        if question:
            question.is_processed_for_embedding = True
            if error_log:
                question.processing_error_log = error_log
            db.add(question)
            await db.flush()
            await db.refresh(question)
        return question

    async def get_statistics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get question statistics"""
        # Total questions
        total_count = await db.execute(select(func.count(Question.id)))
        total = total_count.scalar()
        
        # By subject
        subject_stats = await db.execute(
            select(Subject.name, func.count(Question.id))
            .join(Subject)
            .group_by(Subject.name)
        )
        by_subject = dict(subject_stats.all())
        
        # By difficulty
        difficulty_stats = await db.execute(
            select(Question.difficulty_level, func.count(Question.id))
            .group_by(Question.difficulty_level)
        )
        by_difficulty = {level.value: count for level, count in difficulty_stats.all()}
        
        # By type
        type_stats = await db.execute(
            select(Question.question_type, func.count(Question.id))
            .group_by(Question.question_type)
        )
        by_type = {qtype.value: count for qtype, count in type_stats.all()}
        
        # Verified percentage
        verified_count = await db.execute(select(func.count(Question.id)).where(Question.is_verified == True))
        verified = verified_count.scalar()
        verified_percentage = (verified / total * 100) if total > 0 else 0
        
        # With explanations/hints
        with_explanations = await db.execute(
            select(func.count(func.distinct(Question.id)))
            .join(Explanation)
        )
        explanations_count = with_explanations.scalar()
        
        with_hints = await db.execute(
            select(func.count(func.distinct(Question.id)))
            .join(Hint)
        )
        hints_count = with_hints.scalar()
        
        # Average points
        avg_points = await db.execute(select(func.avg(Question.points)))
        average_points = float(avg_points.scalar() or 0)
        
        return {
            "total_questions": total,
            "by_subject": by_subject,
            "by_difficulty": by_difficulty,
            "by_type": by_type,
            "verified_percentage": verified_percentage,
            "with_explanations": explanations_count,
            "with_hints": hints_count,
            "average_points": average_points
        }

class QuestionMetadataRepository(BaseRepository[QuestionMetadata, QuestionMetadataCreate, QuestionMetadataUpdate]):
    
    async def get_by_question_id(self, db: AsyncSession, *, question_id: int) -> Optional[QuestionMetadata]:
        return await self.get_by_attribute(db, attribute="question_id", value=question_id)
    
    async def get_by_source(self, db: AsyncSession, *, source: str, skip: int = 0, limit: int = 100) -> List[QuestionMetadata]:
        return await self.get_multi_by_attribute(db, attribute="source", value=source, skip=skip, limit=limit)
    
    async def get_by_year(self, db: AsyncSession, *, year: int, skip: int = 0, limit: int = 100) -> List[QuestionMetadata]:
        return await self.get_multi_by_attribute(db, attribute="year", value=year, skip=skip, limit=limit)
    
    async def search_by_tags(self, db: AsyncSession, *, tags: List[str], skip: int = 0, limit: int = 100) -> List[QuestionMetadata]:
        """Search metadata by tags using PostgreSQL array operations"""
        statement = (
            select(QuestionMetadata)
            .where(QuestionMetadata.tags.op('@>')(tags))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()

class QuestionImageRepository(BaseRepository[QuestionImage, QuestionImageCreate, QuestionImageUpdate]):
    
    async def get_by_question_id(self, db: AsyncSession, *, question_id: int) -> List[QuestionImage]:
        return await self.get_multi_by_attribute(db, attribute="question_id", value=question_id)
    
    async def get_unprocessed(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[QuestionImage]:
        """Get images that haven't been processed by OCR"""
        statement = (
            select(QuestionImage)
            .where(QuestionImage.is_processed == False)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def mark_as_processed(self, db: AsyncSession, *, image_id: int, ocr_text: str, confidence: float) -> Optional[QuestionImage]:
        """Mark image as processed and store OCR results"""
        image = await self.get(db, id=image_id)
        if image:
            image.is_processed = True
            image.processed_at = datetime.utcnow()
            image.ocr_text = ocr_text
            image.ocr_confidence = confidence
            db.add(image)
            await db.flush()
            await db.refresh(image)
        return image

class ExplanationRepository(BaseRepository[Explanation, ExplanationCreate, ExplanationUpdate]):
    
    async def get_by_question_id(self, db: AsyncSession, *, question_id: int) -> List[Explanation]:
        return await self.get_multi_by_attribute(db, attribute="question_id", value=question_id)
    
    async def get_verified(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[Explanation]:
        statement = (
            select(Explanation)
            .where(Explanation.is_verified == True)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_ai_generated(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[Explanation]:
        statement = (
            select(Explanation)
            .where(Explanation.is_ai_generated == True)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def vote_helpful(self, db: AsyncSession, *, explanation_id: int, is_helpful: bool) -> Optional[Explanation]:
        """Record a helpful/not helpful vote"""
        explanation = await self.get(db, id=explanation_id)
        if explanation:
            explanation.total_votes += 1
            if is_helpful:
                explanation.helpful_votes += 1
            db.add(explanation)
            await db.flush()
            await db.refresh(explanation)
        return explanation

class HintRepository(BaseRepository[Hint, HintCreate, HintUpdate]):
    
    async def get_by_question_id(self, db: AsyncSession, *, question_id: int) -> List[Hint]:
        """Get hints for a question ordered by level"""
        statement = (
            select(Hint)
            .where(Hint.question_id == question_id)
            .order_by(asc(Hint.level))
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_by_level(self, db: AsyncSession, *, question_id: int, level: int) -> Optional[Hint]:
        """Get specific hint level for a question"""
        statement = (
            select(Hint)
            .where(and_(Hint.question_id == question_id, Hint.level == level))
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def increment_usage(self, db: AsyncSession, *, hint_id: int) -> Optional[Hint]:
        """Increment usage count for a hint"""
        hint = await self.get(db, id=hint_id)
        if hint:
            hint.usage_count += 1
            db.add(hint)
            await db.flush()
            await db.refresh(hint)
        return hint

class SimilarQuestionRepository(BaseRepository[SimilarQuestion, SimilarQuestionCreate, dict]):
    
    async def get_similar_to(self, db: AsyncSession, *, question_id: int, min_score: float = 0.5) -> List[SimilarQuestion]:
        """Get questions similar to the given question"""
        statement = (
            select(SimilarQuestion)
            .where(and_(
                SimilarQuestion.original_question_id == question_id,
                SimilarQuestion.similarity_score >= min_score
            ))
            .order_by(desc(SimilarQuestion.similarity_score))
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_similar_from(self, db: AsyncSession, *, question_id: int, min_score: float = 0.5) -> List[SimilarQuestion]:
        """Get questions that are similar to the given question (reverse lookup)"""
        statement = (
            select(SimilarQuestion)
            .where(and_(
                SimilarQuestion.similar_question_id == question_id,
                SimilarQuestion.similarity_score >= min_score
            ))
            .order_by(desc(SimilarQuestion.similarity_score))
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def create_bidirectional(self, db: AsyncSession, *, question1_id: int, question2_id: int, similarity_score: float, similarity_type: str = "content") -> List[SimilarQuestion]:
        """Create bidirectional similarity relationship"""
        # Check if relationships already exist
        existing1 = await db.execute(
            select(SimilarQuestion).where(and_(
                SimilarQuestion.original_question_id == question1_id,
                SimilarQuestion.similar_question_id == question2_id
            ))
        )
        existing2 = await db.execute(
            select(SimilarQuestion).where(and_(
                SimilarQuestion.original_question_id == question2_id,
                SimilarQuestion.similar_question_id == question1_id
            ))
        )
        
        relationships = []
        
        if not existing1.scalar_one_or_none():
            rel1 = SimilarQuestion(
                original_question_id=question1_id,
                similar_question_id=question2_id,
                similarity_score=similarity_score,
                similarity_type=similarity_type,
                calculated_at=datetime.utcnow()
            )
            db.add(rel1)
            relationships.append(rel1)
        
        if not existing2.scalar_one_or_none():
            rel2 = SimilarQuestion(
                original_question_id=question2_id,
                similar_question_id=question1_id,
                similarity_score=similarity_score,
                similarity_type=similarity_type,
                calculated_at=datetime.utcnow()
            )
            db.add(rel2)
            relationships.append(rel2)
        
        if relationships:
            await db.flush()
            for rel in relationships:
                await db.refresh(rel)
        
        return relationships

# Initialize repository instances
question_repo = QuestionRepository(Question)
question_metadata_repo = QuestionMetadataRepository(QuestionMetadata)
question_image_repo = QuestionImageRepository(QuestionImage)
explanation_repo = ExplanationRepository(Explanation)
hint_repo = HintRepository(Hint)
similar_question_repo = SimilarQuestionRepository(SimilarQuestion)
