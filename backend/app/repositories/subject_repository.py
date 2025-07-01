from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import and_, or_, func, desc, asc, text, case
from datetime import datetime

from app.models.subject import Subject, Topic
from app.schemas.subject import (
    SubjectCreate, SubjectUpdate, 
    TopicCreate, TopicUpdate
)
from app.repositories.base import BaseRepository

class SubjectRepository(BaseRepository[Subject, SubjectCreate, SubjectUpdate]):
    
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Subject]:
        return await self.get_by_attribute(db, attribute="name", value=name)
    
    async def get_by_code(self, db: AsyncSession, *, code: str) -> Optional[Subject]:
        return await self.get_by_attribute(db, attribute="code", value=code)
    
    async def get_by_department(self, db: AsyncSession, *, department: str, skip: int = 0, limit: int = 100) -> List[Subject]:
        return await self.get_multi_by_attribute(db, attribute="department", value=department, skip=skip, limit=limit)
    
    async def get_by_category(self, db: AsyncSession, *, category: str, skip: int = 0, limit: int = 100) -> List[Subject]:
        return await self.get_multi_by_attribute(db, attribute="category", value=category, skip=skip, limit=limit)
    
    async def get_by_level(self, db: AsyncSession, *, level: int, skip: int = 0, limit: int = 100) -> List[Subject]:
        return await self.get_multi_by_attribute(db, attribute="level", value=level, skip=skip, limit=limit)
    
    async def get_active_subjects(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[Subject]:
        """Get only active subjects"""
        statement = select(Subject).where(Subject.is_active == True).offset(skip).limit(limit)
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_popular_subjects(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[Subject]:
        """Get popular subjects"""
        statement = (
            select(Subject)
            .where(and_(Subject.is_active == True, Subject.is_popular == True))
            .order_by(desc(Subject.total_students))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_with_topics(self, db: AsyncSession, *, subject_id: int) -> Optional[Subject]:
        """Get subject with all its topics loaded"""
        statement = (
            select(Subject)
            .options(selectinload(Subject.topics))
            .where(Subject.id == subject_id)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_with_stats(self, db: AsyncSession, *, subject_id: int) -> Optional[Subject]:
        """Get subject with detailed statistics"""
        statement = (
            select(Subject)
            .options(
                selectinload(Subject.topics),
                selectinload(Subject.questions),
                selectinload(Subject.user_progress),
                selectinload(Subject.enrolled_users)
            )
            .where(Subject.id == subject_id)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def search_subjects(self, db: AsyncSession, *, query: str, skip: int = 0, limit: int = 100) -> List[Subject]:
        """Search subjects by name, code, or description"""
        statement = (
            select(Subject)
            .where(
                or_(
                    Subject.name.ilike(f"%{query}%"),
                    Subject.code.ilike(f"%{query}%"),
                    Subject.description.ilike(f"%{query}%"),
                    Subject.department.ilike(f"%{query}%")
                )
            )
            .where(Subject.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_by_tags(self, db: AsyncSession, *, tags: List[str], skip: int = 0, limit: int = 100) -> List[Subject]:
        """Get subjects by tags using PostgreSQL array operations"""
        statement = (
            select(Subject)
            .where(Subject.tags.op('@>')(tags))
            .where(Subject.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_by_prerequisites(self, db: AsyncSession, *, prerequisite_codes: List[str], skip: int = 0, limit: int = 100) -> List[Subject]:
        """Get subjects that have specific prerequisites"""
        statement = (
            select(Subject)
            .where(Subject.prerequisites.op('@>')(prerequisite_codes))
            .where(Subject.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_available_for_user(self, db: AsyncSession, *, user_completed_subjects: List[str], skip: int = 0, limit: int = 100) -> List[Subject]:
        """Get subjects available for a user based on completed prerequisites"""
        statement = (
            select(Subject)
            .where(Subject.is_active == True)
            .where(
                or_(
                    Subject.prerequisites == [],
                    Subject.prerequisites.is_(None),
                    Subject.prerequisites.op('<@')(user_completed_subjects)  # All prerequisites are in user's completed list
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def update_statistics(self, db: AsyncSession, *, subject_id: int) -> Optional[Subject]:
        """Update subject statistics (questions count, students count, etc.)"""
        subject = await self.get_with_stats(db, subject_id=subject_id)
        if subject:
            # Count questions
            from app.models.question import Question
            question_count = await db.execute(
                select(func.count(Question.id)).where(Question.subject_id == subject_id)
            )
            subject.total_questions = question_count.scalar()
            
            # Count enrolled students
            subject.total_students = len(subject.enrolled_users)
            
            # Calculate average difficulty
            if subject.questions:
                difficulty_map = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
                difficulties = [difficulty_map.get(q.difficulty_level.value, 2) for q in subject.questions]
                subject.difficulty_average = sum(difficulties) / len(difficulties)
            
            db.add(subject)
            await db.flush()
            await db.refresh(subject)
        
        return subject
    
    async def get_statistics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get overall subject statistics"""
        # Total subjects
        total_count = await db.execute(select(func.count(Subject.id)))
        total = total_count.scalar()
        
        # Active subjects
        active_count = await db.execute(select(func.count(Subject.id)).where(Subject.is_active == True))
        active = active_count.scalar()
        
        # By department
        dept_stats = await db.execute(
            select(Subject.department, func.count(Subject.id))
            .where(Subject.department.is_not(None))
            .group_by(Subject.department)
        )
        by_department = dict(dept_stats.all())
        
        # By category
        category_stats = await db.execute(
            select(Subject.category, func.count(Subject.id))
            .where(Subject.category.is_not(None))
            .group_by(Subject.category)
        )
        by_category = dict(category_stats.all())
        
        # By level
        level_stats = await db.execute(
            select(Subject.level, func.count(Subject.id))
            .where(Subject.level.is_not(None))
            .group_by(Subject.level)
        )
        by_level = dict(level_stats.all())
        
        # Average statistics
        avg_questions = await db.execute(select(func.avg(Subject.total_questions)))
        avg_students = await db.execute(select(func.avg(Subject.total_students)))
        
        return {
            "total_subjects": total,
            "active_subjects": active,
            "by_department": by_department,
            "by_category": by_category,
            "by_level": by_level,
            "average_questions_per_subject": float(avg_questions.scalar() or 0),
            "average_students_per_subject": float(avg_students.scalar() or 0)
        }

class TopicRepository(BaseRepository[Topic, TopicCreate, TopicUpdate]):
    
    async def get_by_name(self, db: AsyncSession, *, name: str, subject_id: Optional[int] = None) -> Optional[Topic]:
        """Get topic by name, optionally within a specific subject"""
        if subject_id:
            statement = select(Topic).where(and_(Topic.name == name, Topic.subject_id == subject_id))
        else:
            statement = select(Topic).where(Topic.name == name)
        
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_by_subject(self, db: AsyncSession, *, subject_id: int, skip: int = 0, limit: int = 100) -> List[Topic]:
        return await self.get_multi_by_attribute(db, attribute="subject_id", value=subject_id, skip=skip, limit=limit)
    
    async def get_root_topics(self, db: AsyncSession, *, subject_id: int) -> List[Topic]:
        """Get top-level topics (no parent) for a subject"""
        statement = (
            select(Topic)
            .where(and_(Topic.subject_id == subject_id, Topic.parent_topic_id.is_(None)))
            .order_by(asc(Topic.order_index))
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_subtopics(self, db: AsyncSession, *, parent_topic_id: int) -> List[Topic]:
        """Get all subtopics of a parent topic"""
        statement = (
            select(Topic)
            .where(Topic.parent_topic_id == parent_topic_id)
            .order_by(asc(Topic.order_index))
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_topic_hierarchy(self, db: AsyncSession, *, subject_id: int) -> List[Topic]:
        """Get complete topic hierarchy for a subject with relationships loaded"""
        statement = (
            select(Topic)
            .options(
                selectinload(Topic.subtopics),
                selectinload(Topic.parent_topic)
            )
            .where(Topic.subject_id == subject_id)
            .order_by(asc(Topic.level), asc(Topic.order_index))
        )
        result = await db.execute(statement)
        return result.scalars().all()
    
    async def get_with_questions(self, db: AsyncSession, *, topic_id: int) -> Optional[Topic]:
        """Get topic with all its questions loaded"""
        statement = (
            select(Topic)
            .options(selectinload(Topic.questions))
            .where(Topic.id == topic_id)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_active_topics(self, db: AsyncSession, *, subject_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Topic]:
        """Get active topics, optionally filtered by subject"""
        query = select(Topic).where(Topic.is_active == True)
        
        if subject_id:
            query = query.where(Topic.subject_id == subject_id)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def search_topics(self, db: AsyncSession, *, query: str, subject_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Topic]:
        """Search topics by name or description"""
        search_query = (
            select(Topic)
            .where(
                or_(
                    Topic.name.ilike(f"%{query}%"),
                    Topic.description.ilike(f"%{query}%")
                )
            )
            .where(Topic.is_active == True)
        )
        
        if subject_id:
            search_query = search_query.where(Topic.subject_id == subject_id)
        
        search_query = search_query.offset(skip).limit(limit)
        result = await db.execute(search_query)
        return result.scalars().all()
    
    async def get_by_tags(self, db: AsyncSession, *, tags: List[str], subject_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Topic]:
        """Get topics by tags"""
        query = (
            select(Topic)
            .where(Topic.tags.op('@>')(tags))
            .where(Topic.is_active == True)
        )
        
        if subject_id:
            query = query.where(Topic.subject_id == subject_id)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_difficulty(self, db: AsyncSession, *, difficulty_level: str, subject_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Topic]:
        """Get topics by difficulty level"""
        query = (
            select(Topic)
            .where(Topic.difficulty_level == difficulty_level)
            .where(Topic.is_active == True)
        )
        
        if subject_id:
            query = query.where(Topic.subject_id == subject_id)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def update_order(self, db: AsyncSession, *, topic_updates: List[Dict[int, int]]) -> List[Topic]:
        """Update the order of multiple topics"""
        updated_topics = []
        
        for topic_id, new_order in topic_updates:
            topic = await self.get(db, id=topic_id)
            if topic:
                topic.order_index = new_order
                db.add(topic)
                updated_topics.append(topic)
        
        if updated_topics:
            await db.flush()
            for topic in updated_topics:
                await db.refresh(topic)
        
        return updated_topics
    
    async def update_statistics(self, db: AsyncSession, *, topic_id: int) -> Optional[Topic]:
        """Update topic statistics"""
        topic = await self.get_with_questions(db, topic_id=topic_id)
        if topic:
            topic.total_questions = len(topic.questions)
            
            db.add(topic)
            await db.flush()
            await db.refresh(topic)
        
        return topic
    
    async def get_learning_path(self, db: AsyncSession, *, subject_id: int) -> List[Topic]:
        """Get suggested learning path (topics ordered by difficulty and prerequisites)"""
        statement = (
            select(Topic)
            .where(and_(Topic.subject_id == subject_id, Topic.is_active == True))
            .order_by(
                asc(Topic.level),
                asc(Topic.order_index),
                case(
                    (Topic.difficulty_level == "beginner", 1),
                    (Topic.difficulty_level == "intermediate", 2),
                    (Topic.difficulty_level == "advanced", 3),
                    (Topic.difficulty_level == "expert", 4),
                    else_=2
                )
            )
        )
        result = await db.execute(statement)
        return result.scalars().all()

# Initialize repository instances
subject_repo = SubjectRepository(Subject)
topic_repo = TopicRepository(Topic)
