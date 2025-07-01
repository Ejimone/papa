from typing import Optional, List, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
import logging
import re

from app.models.question import Question, QuestionType, DifficultyLevel
from app.models.subject import Subject, Topic
from app.models.practice import UserBookmark
from app.schemas.question import QuestionFilter, QuestionSearch
from app.services.base import BaseService

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def search_questions(
        self,
        query: str,
        filters: Optional[QuestionFilter] = None,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Search questions with text search and filters"""
        try:
            # Build base query
            base_query = select(Question).options(
                selectinload(Question.subject),
                selectinload(Question.topic)
            )
            
            # Apply text search
            conditions = []
            if query:
                search_terms = self._process_search_query(query)
                text_conditions = []
                
                for term in search_terms:
                    text_conditions.append(
                        or_(
                            Question.title.ilike(f"%{term}%"),
                            Question.content.ilike(f"%{term}%"),
                            Question.answer.ilike(f"%{term}%")
                        )
                    )
                
                if text_conditions:
                    conditions.append(and_(*text_conditions))
            
            # Apply filters
            if filters:
                filter_conditions = self._build_filter_conditions(filters)
                conditions.extend(filter_conditions)
            
            # Apply all conditions
            if conditions:
                base_query = base_query.where(and_(*conditions))
            
            # Count total results
            count_query = select(func.count(Question.id))
            if conditions:
                count_query = count_query.where(and_(*conditions))
            
            total_result = await self.db.execute(count_query)
            total_count = total_result.scalar()
            
            # Apply ordering and pagination
            base_query = base_query.order_by(
                Question.priority_score.desc(),
                Question.created_at.desc()
            )
            base_query = base_query.offset(skip).limit(limit)
            
            # Execute search
            result = await self.db.execute(base_query)
            questions = result.scalars().all()
            
            # Get search suggestions
            suggestions = await self._get_search_suggestions(query) if query else []
            
            return {
                "questions": questions,
                "total_count": total_count,
                "query": query,
                "filters_applied": filters.dict() if filters else {},
                "suggestions": suggestions,
                "search_time_ms": 0.0,  # Would be calculated in real implementation
                "page": skip // limit + 1,
                "total_pages": (total_count + limit - 1) // limit
            }
        except Exception as e:
            logger.error(f"Error searching questions: {str(e)}")
            raise HTTPException(status_code=500, detail="Search error")
    
    async def search_subjects_and_topics(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Search subjects and topics"""
        try:
            search_term = f"%{query}%"
            
            # Search subjects
            subjects_query = select(Subject).where(
                or_(
                    Subject.name.ilike(search_term),
                    Subject.description.ilike(search_term)
                )
            ).limit(limit // 2)
            
            subjects_result = await self.db.execute(subjects_query)
            subjects = subjects_result.scalars().all()
            
            # Search topics
            topics_query = select(Topic).options(
                selectinload(Topic.subject)
            ).where(
                or_(
                    Topic.name.ilike(search_term),
                    Topic.description.ilike(search_term)
                )
            ).limit(limit // 2)
            
            topics_result = await self.db.execute(topics_query)
            topics = topics_result.scalars().all()
            
            return {
                "subjects": subjects,
                "topics": topics,
                "query": query,
                "total_subjects": len(subjects),
                "total_topics": len(topics)
            }
        except Exception as e:
            logger.error(f"Error searching subjects and topics: {str(e)}")
            raise HTTPException(status_code=500, detail="Search error")
    
    async def search_user_bookmarks(
        self,
        user_id: int,
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Search user bookmarks"""
        try:
            search_term = f"%{query}%"
            
            bookmarks_query = select(UserBookmark).options(
                selectinload(UserBookmark.question).selectinload(Question.subject),
                selectinload(UserBookmark.question).selectinload(Question.topic)
            ).join(Question).where(
                and_(
                    UserBookmark.user_id == user_id,
                    or_(
                        Question.title.ilike(search_term),
                        Question.content.ilike(search_term),
                        UserBookmark.notes.ilike(search_term)
                    )
                )
            ).order_by(UserBookmark.created_at.desc())
            
            bookmarks_query = bookmarks_query.offset(skip).limit(limit)
            
            result = await self.db.execute(bookmarks_query)
            bookmarks = result.scalars().all()
            
            # Count total
            count_query = select(func.count(UserBookmark.id)).join(Question).where(
                and_(
                    UserBookmark.user_id == user_id,
                    or_(
                        Question.title.ilike(search_term),
                        Question.content.ilike(search_term),
                        UserBookmark.notes.ilike(search_term)
                    )
                )
            )
            
            count_result = await self.db.execute(count_query)
            total_count = count_result.scalar()
            
            return {
                "bookmarks": bookmarks,
                "total_count": total_count,
                "query": query
            }
        except Exception as e:
            logger.error(f"Error searching user bookmarks: {str(e)}")
            raise HTTPException(status_code=500, detail="Search error")
    
    async def get_popular_searches(self, limit: int = 10) -> List[str]:
        """Get popular search terms (would be based on search logs in real implementation)"""
        try:
            # This is a placeholder - in a real implementation, you'd track search queries
            # and return the most popular ones
            popular_searches = [
                "algebra",
                "calculus",
                "physics",
                "chemistry",
                "biology",
                "geometry",
                "trigonometry",
                "statistics",
                "probability",
                "linear equations"
            ]
            
            return popular_searches[:limit]
        except Exception as e:
            logger.error(f"Error getting popular searches: {str(e)}")
            return []
    
    async def get_search_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """Get search suggestions based on partial query"""
        try:
            if not query or len(query) < 2:
                return []
            
            suggestions = await self._get_search_suggestions(query)
            return suggestions[:limit]
        except Exception as e:
            logger.error(f"Error getting search suggestions: {str(e)}")
            return []
    
    async def advanced_search(
        self,
        search_params: Dict[str, Any],
        skip: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Perform advanced search with multiple criteria"""
        try:
            query = select(Question).options(
                selectinload(Question.subject),
                selectinload(Question.topic)
            )
            
            conditions = []
            
            # Text search in multiple fields
            if search_params.get("text_query"):
                text_query = search_params["text_query"]
                text_conditions = [
                    Question.title.ilike(f"%{text_query}%"),
                    Question.content.ilike(f"%{text_query}%")
                ]
                
                if search_params.get("search_answers"):
                    text_conditions.append(Question.answer.ilike(f"%{text_query}%"))
                
                conditions.append(or_(*text_conditions))
            
            # Subject filter
            if search_params.get("subject_ids"):
                conditions.append(Question.subject_id.in_(search_params["subject_ids"]))
            
            # Topic filter
            if search_params.get("topic_ids"):
                conditions.append(Question.topic_id.in_(search_params["topic_ids"]))
            
            # Difficulty filter
            if search_params.get("difficulty_levels"):
                conditions.append(Question.difficulty_level.in_(search_params["difficulty_levels"]))
            
            # Question type filter
            if search_params.get("question_types"):
                conditions.append(Question.question_type.in_(search_params["question_types"]))
            
            # Points range
            if search_params.get("min_points"):
                conditions.append(Question.points >= search_params["min_points"])
            if search_params.get("max_points"):
                conditions.append(Question.points <= search_params["max_points"])
            
            # Verification status
            if search_params.get("verified_only"):
                conditions.append(Question.is_verified == True)
            
            # Date range
            if search_params.get("created_after"):
                conditions.append(Question.created_at >= search_params["created_after"])
            if search_params.get("created_before"):
                conditions.append(Question.created_at <= search_params["created_before"])
            
            # Apply conditions
            if conditions:
                query = query.where(and_(*conditions))
            
            # Count total
            count_query = select(func.count(Question.id))
            if conditions:
                count_query = count_query.where(and_(*conditions))
            
            total_result = await self.db.execute(count_query)
            total_count = total_result.scalar()
            
            # Apply sorting
            sort_by = search_params.get("sort_by", "relevance")
            if sort_by == "newest":
                query = query.order_by(Question.created_at.desc())
            elif sort_by == "oldest":
                query = query.order_by(Question.created_at.asc())
            elif sort_by == "difficulty":
                query = query.order_by(Question.difficulty_level, Question.points)
            elif sort_by == "points":
                query = query.order_by(Question.points.desc())
            else:  # relevance
                query = query.order_by(Question.priority_score.desc(), Question.created_at.desc())
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            
            # Execute query
            result = await self.db.execute(query)
            questions = result.scalars().all()
            
            return {
                "questions": questions,
                "total_count": total_count,
                "search_params": search_params,
                "page": skip // limit + 1,
                "total_pages": (total_count + limit - 1) // limit
            }
        except Exception as e:
            logger.error(f"Error in advanced search: {str(e)}")
            raise HTTPException(status_code=500, detail="Advanced search error")
    
    def _process_search_query(self, query: str) -> List[str]:
        """Process search query into terms"""
        # Remove special characters and split into terms
        cleaned_query = re.sub(r'[^\w\s]', ' ', query)
        terms = [term.strip() for term in cleaned_query.split() if len(term.strip()) > 2]
        return terms
    
    def _build_filter_conditions(self, filters: QuestionFilter) -> List:
        """Build SQLAlchemy filter conditions from QuestionFilter"""
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
        
        return conditions
    
    async def _get_search_suggestions(self, query: str) -> List[str]:
        """Get search suggestions based on query"""
        try:
            suggestions = []
            
            # Get subject/topic name suggestions
            search_term = f"%{query}%"
            
            # Subject suggestions
            subjects_query = select(Subject.name).where(
                Subject.name.ilike(search_term)
            ).limit(3)
            
            subjects_result = await self.db.execute(subjects_query)
            subject_names = subjects_result.scalars().all()
            suggestions.extend(subject_names)
            
            # Topic suggestions
            topics_query = select(Topic.name).where(
                Topic.name.ilike(search_term)
            ).limit(3)
            
            topics_result = await self.db.execute(topics_query)
            topic_names = topics_result.scalars().all()
            suggestions.extend(topic_names)
            
            # Question title suggestions
            questions_query = select(Question.title).where(
                Question.title.ilike(search_term)
            ).limit(2)
            
            questions_result = await self.db.execute(questions_query)
            question_titles = questions_result.scalars().all()
            suggestions.extend(question_titles)
            
            # Remove duplicates and return
            unique_suggestions = list(set(suggestions))
            return unique_suggestions[:5]
        except Exception as e:
            logger.error(f"Error getting search suggestions: {str(e)}")
            return []
