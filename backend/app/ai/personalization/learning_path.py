from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
from collections import defaultdict, deque
import heapq

from .user_modeling import UserProfile, QuestionInteraction, PerformanceLevel
from .difficulty_adapter import DifficultyAdapter, AdaptationStrategy

class PathType(Enum):
    SEQUENTIAL = "sequential"           # Follow topic prerequisites
    SPIRAL = "spiral"                   # Revisit topics at increasing difficulty
    WEAKNESS_FOCUSED = "weakness_focused"  # Target identified weak areas
    SPACED_REPETITION = "spaced_repetition"  # Optimize for retention
    EXAM_PREPARATION = "exam_preparation"     # Intensive exam-focused path
    EXPLORATION = "exploration"         # Broad coverage for discovery

class LearningObjective(Enum):
    MASTERY = "mastery"                # Deep understanding
    COVERAGE = "coverage"              # Broad topic coverage
    RETENTION = "retention"            # Long-term memory
    SPEED = "speed"                    # Quick completion
    CONFIDENCE = "confidence"          # Build confidence

@dataclass
class Topic:
    id: str
    name: str
    subject: str
    prerequisites: List[str] = field(default_factory=list)
    difficulty_level: int = 1
    estimated_duration: int = 30  # minutes
    importance_weight: float = 1.0
    question_count: int = 0

@dataclass
class LearningStep:
    topic_id: str
    topic_name: str
    difficulty: int
    estimated_duration: int
    question_count: int
    step_type: str  # "learn", "practice", "review", "assessment"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StudySession:
    steps: List[LearningStep]
    total_duration: int
    session_type: str
    focus_areas: List[str]
    difficulty_range: Tuple[int, int]
    objectives: List[LearningObjective]

@dataclass
class LearningPath:
    id: str
    user_id: str
    subject: str
    path_type: PathType
    objectives: List[LearningObjective]
    sessions: List[StudySession]
    total_duration: int  # minutes
    estimated_completion: datetime
    created_at: datetime
    progress: float = 0.0
    current_session: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TopicMastery:
    topic_id: str
    mastery_level: float  # 0.0 to 1.0
    last_practiced: datetime
    question_attempts: int
    correct_answers: int
    average_time: float
    confidence_score: float
    retention_score: float  # Based on spaced repetition
    needs_review: bool = False

class LearningPathGenerator:
    def __init__(self, difficulty_adapter: Optional[DifficultyAdapter] = None):
        self.difficulty_adapter = difficulty_adapter or DifficultyAdapter()
        self.logger = logging.getLogger(__name__)
        
        # Spaced repetition intervals (in days)
        self.spaced_intervals = [1, 3, 7, 14, 30, 90]
        
        # Session duration preferences (in minutes)
        self.session_durations = {
            'short': 15,
            'medium': 30,
            'long': 45,
            'extended': 60
        }

    async def generate_personalized_path(
        self,
        user_profile: UserProfile,
        subject: str,
        objectives: List[LearningObjective],
        path_type: PathType = PathType.SEQUENTIAL,
        available_topics: List[Topic] = None,
        time_constraints: Optional[Dict[str, Any]] = None
    ) -> LearningPath:
        """
        Generate a personalized learning path for the user
        """
        try:
            # Analyze current mastery levels
            mastery_analysis = await self._analyze_topic_mastery(
                user_profile, subject, available_topics or []
            )
            
            # Identify learning priorities
            priorities = await self._identify_learning_priorities(
                user_profile, mastery_analysis, objectives
            )
            
            # Generate session structure
            sessions = await self._generate_sessions(
                user_profile, priorities, path_type, objectives, time_constraints
            )
            
            # Calculate total duration
            total_duration = sum(session.total_duration for session in sessions)
            
            # Estimate completion date
            daily_study_time = user_profile.study_preferences.get('daily_minutes', 30)
            days_to_complete = max(1, total_duration // daily_study_time)
            estimated_completion = datetime.now() + timedelta(days=days_to_complete)
            
            path = LearningPath(
                id=f"path_{user_profile.user_id}_{subject}_{datetime.now().timestamp()}",
                user_id=user_profile.user_id,
                subject=subject,
                path_type=path_type,
                objectives=objectives,
                sessions=sessions,
                total_duration=total_duration,
                estimated_completion=estimated_completion,
                created_at=datetime.now(),
                metadata={
                    'mastery_analysis': mastery_analysis,
                    'priorities': priorities,
                    'adaptation_strategy': self.difficulty_adapter.adaptation_strategy.value
                }
            )
            
            return path
            
        except Exception as e:
            self.logger.error(f"Error generating learning path: {e}")
            # Return minimal fallback path
            return await self._generate_fallback_path(user_profile, subject, objectives)

    async def _analyze_topic_mastery(
        self,
        user_profile: UserProfile,
        subject: str,
        available_topics: List[Topic]
    ) -> Dict[str, TopicMastery]:
        """
        Analyze user's current mastery level for each topic
        """
        mastery_map = {}
        
        # Initialize mastery for all available topics
        for topic in available_topics:
            mastery_map[topic.id] = TopicMastery(
                topic_id=topic.id,
                mastery_level=0.0,
                last_practiced=datetime.now() - timedelta(days=365),
                question_attempts=0,
                correct_answers=0,
                average_time=0.0,
                confidence_score=0.0,
                retention_score=0.0
            )
        
        # Analyze from user interactions
        subject_interactions = [
            interaction for interaction in user_profile.recent_interactions
            if interaction.subject == subject
        ]
        
        # Group interactions by topic
        topic_interactions = defaultdict(list)
        for interaction in subject_interactions:
            topic_id = interaction.metadata.get('topic_id', 'unknown')
            if topic_id in mastery_map:
                topic_interactions[topic_id].append(interaction)
        
        # Calculate mastery metrics for each topic
        for topic_id, interactions in topic_interactions.items():
            if not interactions:
                continue
                
            mastery = mastery_map[topic_id]
            
            # Basic metrics
            mastery.question_attempts = len(interactions)
            mastery.correct_answers = sum(1 for i in interactions if i.is_correct)
            mastery.last_practiced = max(i.timestamp for i in interactions)
            mastery.average_time = sum(i.time_taken for i in interactions) / len(interactions)
            
            # Mastery level calculation
            accuracy = mastery.correct_answers / mastery.question_attempts
            recency_factor = self._calculate_recency_factor(mastery.last_practiced)
            attempt_factor = min(1.0, mastery.question_attempts / 10)  # Normalize to 10 attempts
            
            mastery.mastery_level = (accuracy * 0.6 + recency_factor * 0.2 + attempt_factor * 0.2)
            
            # Confidence score (based on consistency)
            recent_interactions = sorted(interactions, key=lambda x: x.timestamp)[-5:]
            if len(recent_interactions) >= 3:
                recent_accuracy = sum(1 for i in recent_interactions if i.is_correct) / len(recent_interactions)
                mastery.confidence_score = min(1.0, recent_accuracy * 1.2)
            else:
                mastery.confidence_score = accuracy * 0.8
            
            # Retention score (spaced repetition)
            mastery.retention_score = self._calculate_retention_score(interactions)
            
            # Needs review flag
            days_since_practice = (datetime.now() - mastery.last_practiced).days
            mastery.needs_review = (
                days_since_practice > 7 and mastery.mastery_level < 0.8
            ) or (
                days_since_practice > 30 and mastery.mastery_level < 0.9
            )
        
        return mastery_map

    def _calculate_recency_factor(self, last_practiced: datetime) -> float:
        """Calculate recency factor for mastery calculation"""
        days_ago = (datetime.now() - last_practiced).days
        
        if days_ago <= 1:
            return 1.0
        elif days_ago <= 7:
            return 0.8
        elif days_ago <= 30:
            return 0.6
        elif days_ago <= 90:
            return 0.4
        else:
            return 0.2

    def _calculate_retention_score(self, interactions: List[QuestionInteraction]) -> float:
        """Calculate retention score based on spaced repetition principles"""
        if len(interactions) < 2:
            return 0.5
        
        # Sort by timestamp
        sorted_interactions = sorted(interactions, key=lambda x: x.timestamp)
        
        # Look for patterns in repeated correct answers
        retention_events = []
        
        for i in range(1, len(sorted_interactions)):
            current = sorted_interactions[i]
            previous = sorted_interactions[i-1]
            
            days_between = (current.timestamp - previous.timestamp).days
            
            if current.is_correct and previous.is_correct and days_between > 0:
                # Successful retention event
                optimal_interval = self._get_optimal_interval(days_between)
                retention_strength = min(1.0, days_between / optimal_interval)
                retention_events.append(retention_strength)
        
        if retention_events:
            return sum(retention_events) / len(retention_events)
        else:
            # Fallback to recent accuracy
            recent_interactions = sorted_interactions[-3:]
            return sum(1 for i in recent_interactions if i.is_correct) / len(recent_interactions)

    def _get_optimal_interval(self, actual_interval: int) -> int:
        """Get optimal spaced repetition interval"""
        for interval in self.spaced_intervals:
            if actual_interval <= interval:
                return interval
        return self.spaced_intervals[-1]

    async def _identify_learning_priorities(
        self,
        user_profile: UserProfile,
        mastery_analysis: Dict[str, TopicMastery],
        objectives: List[LearningObjective]
    ) -> List[Tuple[str, float]]:
        """
        Identify learning priorities based on mastery analysis and objectives
        """
        priorities = []
        
        for topic_id, mastery in mastery_analysis.items():
            priority_score = 0.0
            
            # Base priority on mastery level (lower mastery = higher priority)
            mastery_priority = 1.0 - mastery.mastery_level
            priority_score += mastery_priority * 0.4
            
            # Adjust based on objectives
            for objective in objectives:
                if objective == LearningObjective.MASTERY:
                    # Prioritize topics with medium mastery for deep learning
                    if 0.3 <= mastery.mastery_level <= 0.7:
                        priority_score += 0.3
                elif objective == LearningObjective.COVERAGE:
                    # Prioritize unlearned topics
                    if mastery.mastery_level < 0.5:
                        priority_score += 0.2
                elif objective == LearningObjective.RETENTION:
                    # Prioritize topics that need review
                    if mastery.needs_review:
                        priority_score += 0.4
                elif objective == LearningObjective.CONFIDENCE:
                    # Prioritize topics with low confidence
                    confidence_priority = 1.0 - mastery.confidence_score
                    priority_score += confidence_priority * 0.2
            
            # Boost priority for recently incorrect topics
            if mastery.question_attempts > 0:
                recent_performance = mastery.correct_answers / mastery.question_attempts
                if recent_performance < 0.6:
                    priority_score += 0.2
            
            # Boost priority for topics not practiced recently
            days_since_practice = (datetime.now() - mastery.last_practiced).days
            if days_since_practice > 14:
                priority_score += 0.1
            
            priorities.append((topic_id, priority_score))
        
        # Sort by priority score (descending)
        priorities.sort(key=lambda x: x[1], reverse=True)
        
        return priorities

    async def _generate_sessions(
        self,
        user_profile: UserProfile,
        priorities: List[Tuple[str, float]],
        path_type: PathType,
        objectives: List[LearningObjective],
        time_constraints: Optional[Dict[str, Any]] = None
    ) -> List[StudySession]:
        """
        Generate study sessions based on priorities and path type
        """
        sessions = []
        
        # Get user preferences
        preferred_session_duration = user_profile.study_preferences.get('session_duration', 'medium')
        session_duration = self.session_durations.get(preferred_session_duration, 30)
        max_sessions = time_constraints.get('max_sessions', 10) if time_constraints else 10
        
        # Generate sessions based on path type
        if path_type == PathType.WEAKNESS_FOCUSED:
            sessions = await self._generate_weakness_focused_sessions(
                priorities, session_duration, max_sessions, objectives
            )
        elif path_type == PathType.SPACED_REPETITION:
            sessions = await self._generate_spaced_repetition_sessions(
                user_profile, priorities, session_duration, max_sessions
            )
        elif path_type == PathType.SPIRAL:
            sessions = await self._generate_spiral_sessions(
                priorities, session_duration, max_sessions, objectives
            )
        elif path_type == PathType.EXAM_PREPARATION:
            sessions = await self._generate_exam_prep_sessions(
                priorities, session_duration, max_sessions, time_constraints
            )
        else:  # SEQUENTIAL or EXPLORATION
            sessions = await self._generate_sequential_sessions(
                priorities, session_duration, max_sessions, objectives
            )
        
        return sessions

    async def _generate_weakness_focused_sessions(
        self,
        priorities: List[Tuple[str, float]],
        session_duration: int,
        max_sessions: int,
        objectives: List[LearningObjective]
    ) -> List[StudySession]:
        """Generate sessions focused on weak areas"""
        sessions = []
        
        # Take top priority topics (weakest areas)
        weak_topics = priorities[:max_sessions * 2]  # Allow multiple sessions per topic
        
        for i in range(max_sessions):
            if i >= len(weak_topics):
                break
            
            topic_id, priority_score = weak_topics[i]
            
            # Create intensive session for this weak topic
            steps = [
                LearningStep(
                    topic_id=topic_id,
                    topic_name=topic_id,  # Would be resolved from topic data
                    difficulty=2,  # Start with moderate difficulty
                    estimated_duration=session_duration // 2,
                    question_count=5,
                    step_type="learn",
                    metadata={'focus': 'weakness_remediation'}
                ),
                LearningStep(
                    topic_id=topic_id,
                    topic_name=topic_id,
                    difficulty=2,
                    estimated_duration=session_duration // 2,
                    question_count=8,
                    step_type="practice",
                    metadata={'focus': 'weakness_remediation'}
                )
            ]
            
            session = StudySession(
                steps=steps,
                total_duration=session_duration,
                session_type="weakness_focused",
                focus_areas=[topic_id],
                difficulty_range=(2, 3),
                objectives=objectives
            )
            
            sessions.append(session)
        
        return sessions

    async def _generate_spaced_repetition_sessions(
        self,
        user_profile: UserProfile,
        priorities: List[Tuple[str, float]],
        session_duration: int,
        max_sessions: int
    ) -> List[StudySession]:
        """Generate sessions optimized for spaced repetition"""
        sessions = []
        
        # Create a schedule based on spaced repetition intervals
        current_date = datetime.now()
        
        for session_idx in range(max_sessions):
            session_date = current_date + timedelta(days=session_idx)
            
            # Determine which topics need review on this date
            topics_for_session = []
            
            for topic_id, priority_score in priorities:
                # Simplified spaced repetition logic
                days_since_last_session = session_idx
                
                # Check if topic should be reviewed based on interval
                for interval in self.spaced_intervals:
                    if days_since_last_session % interval == 0:
                        topics_for_session.append(topic_id)
                        break
            
            if not topics_for_session:
                # Fallback to highest priority topics
                topics_for_session = [priorities[session_idx % len(priorities)][0]]
            
            # Create mixed review session
            steps = []
            time_per_topic = session_duration // max(1, len(topics_for_session))
            
            for topic_id in topics_for_session:
                steps.append(
                    LearningStep(
                        topic_id=topic_id,
                        topic_name=topic_id,
                        difficulty=2,
                        estimated_duration=time_per_topic,
                        question_count=max(1, time_per_topic // 4),
                        step_type="review",
                        metadata={'spaced_repetition': True}
                    )
                )
            
            session = StudySession(
                steps=steps,
                total_duration=session_duration,
                session_type="spaced_repetition",
                focus_areas=topics_for_session,
                difficulty_range=(1, 3),
                objectives=[LearningObjective.RETENTION]
            )
            
            sessions.append(session)
        
        return sessions

    async def _generate_spiral_sessions(
        self,
        priorities: List[Tuple[str, float]],
        session_duration: int,
        max_sessions: int,
        objectives: List[LearningObjective]
    ) -> List[StudySession]:
        """Generate spiral learning sessions that revisit topics at increasing difficulty"""
        sessions = []
        
        # Select core topics to spiral through
        core_topics = [topic_id for topic_id, _ in priorities[:6]]  # Top 6 topics
        
        for session_idx in range(max_sessions):
            # Cycle through topics
            topics_in_session = []
            difficulty_level = min(4, 1 + (session_idx // len(core_topics)))
            
            # Select 2-3 topics for this session
            session_topic_count = min(3, len(core_topics))
            start_idx = (session_idx * session_topic_count) % len(core_topics)
            
            for i in range(session_topic_count):
                topic_idx = (start_idx + i) % len(core_topics)
                topics_in_session.append(core_topics[topic_idx])
            
            # Create steps for each topic
            steps = []
            time_per_topic = session_duration // len(topics_in_session)
            
            for topic_id in topics_in_session:
                steps.append(
                    LearningStep(
                        topic_id=topic_id,
                        topic_name=topic_id,
                        difficulty=difficulty_level,
                        estimated_duration=time_per_topic,
                        question_count=max(2, time_per_topic // 5),
                        step_type="practice",
                        metadata={'spiral_level': difficulty_level}
                    )
                )
            
            session = StudySession(
                steps=steps,
                total_duration=session_duration,
                session_type="spiral",
                focus_areas=topics_in_session,
                difficulty_range=(difficulty_level, difficulty_level),
                objectives=objectives
            )
            
            sessions.append(session)
        
        return sessions

    async def _generate_exam_prep_sessions(
        self,
        priorities: List[Tuple[str, float]],
        session_duration: int,
        max_sessions: int,
        time_constraints: Optional[Dict[str, Any]]
    ) -> List[StudySession]:
        """Generate intensive exam preparation sessions"""
        sessions = []
        
        # Exam prep is more intensive and comprehensive
        exam_date = time_constraints.get('exam_date') if time_constraints else None
        days_until_exam = 14  # Default 2 weeks
        
        if exam_date:
            days_until_exam = (exam_date - datetime.now()).days
        
        # Adjust session intensity based on time remaining
        if days_until_exam <= 7:
            # Intensive review mode
            session_type = "intensive_review"
            difficulty_range = (2, 4)
            questions_per_session = 15
        elif days_until_exam <= 14:
            # Focused practice mode
            session_type = "focused_practice"
            difficulty_range = (2, 3)
            questions_per_session = 12
        else:
            # Comprehensive preparation mode
            session_type = "comprehensive_prep"
            difficulty_range = (1, 4)
            questions_per_session = 10
        
        # Cover all priority topics
        topics_per_session = max(1, len(priorities) // max_sessions)
        
        for session_idx in range(max_sessions):
            start_topic_idx = session_idx * topics_per_session
            end_topic_idx = min(len(priorities), start_topic_idx + topics_per_session)
            
            session_topics = [
                priorities[i][0] for i in range(start_topic_idx, end_topic_idx)
            ]
            
            if not session_topics:
                break
            
            # Create comprehensive practice steps
            steps = []
            time_per_topic = session_duration // len(session_topics)
            
            for topic_id in session_topics:
                # Practice step
                steps.append(
                    LearningStep(
                        topic_id=topic_id,
                        topic_name=topic_id,
                        difficulty=difficulty_range[1],
                        estimated_duration=time_per_topic * 0.7,
                        question_count=max(1, questions_per_session // len(session_topics)),
                        step_type="practice",
                        metadata={'exam_prep': True, 'intensity': 'high'}
                    )
                )
                
                # Quick review step
                steps.append(
                    LearningStep(
                        topic_id=topic_id,
                        topic_name=topic_id,
                        difficulty=difficulty_range[0],
                        estimated_duration=time_per_topic * 0.3,
                        question_count=max(1, 3),
                        step_type="review",
                        metadata={'exam_prep': True, 'quick_review': True}
                    )
                )
            
            session = StudySession(
                steps=steps,
                total_duration=session_duration,
                session_type=session_type,
                focus_areas=session_topics,
                difficulty_range=difficulty_range,
                objectives=[LearningObjective.CONFIDENCE, LearningObjective.RETENTION]
            )
            
            sessions.append(session)
        
        return sessions

    async def _generate_sequential_sessions(
        self,
        priorities: List[Tuple[str, float]],
        session_duration: int,
        max_sessions: int,
        objectives: List[LearningObjective]
    ) -> List[StudySession]:
        """Generate sequential learning sessions"""
        sessions = []
        
        # Sequential learning follows topic order
        topics_per_session = max(1, len(priorities) // max_sessions)
        
        for session_idx in range(max_sessions):
            start_idx = session_idx * topics_per_session
            end_idx = min(len(priorities), start_idx + topics_per_session)
            
            session_topics = [
                priorities[i][0] for i in range(start_idx, end_idx)
            ]
            
            if not session_topics:
                break
            
            steps = []
            time_per_topic = session_duration // len(session_topics)
            
            for topic_id in session_topics:
                # Learn then practice pattern
                steps.extend([
                    LearningStep(
                        topic_id=topic_id,
                        topic_name=topic_id,
                        difficulty=1,
                        estimated_duration=time_per_topic // 2,
                        question_count=3,
                        step_type="learn",
                        metadata={'sequential_order': session_idx}
                    ),
                    LearningStep(
                        topic_id=topic_id,
                        topic_name=topic_id,
                        difficulty=2,
                        estimated_duration=time_per_topic // 2,
                        question_count=5,
                        step_type="practice",
                        metadata={'sequential_order': session_idx}
                    )
                ])
            
            session = StudySession(
                steps=steps,
                total_duration=session_duration,
                session_type="sequential",
                focus_areas=session_topics,
                difficulty_range=(1, 2),
                objectives=objectives
            )
            
            sessions.append(session)
        
        return sessions

    async def _generate_fallback_path(
        self,
        user_profile: UserProfile,
        subject: str,
        objectives: List[LearningObjective]
    ) -> LearningPath:
        """Generate a simple fallback learning path"""
        
        # Create a basic session
        steps = [
            LearningStep(
                topic_id="general",
                topic_name="General Practice",
                difficulty=user_profile.preferred_difficulty,
                estimated_duration=30,
                question_count=10,
                step_type="practice"
            )
        ]
        
        session = StudySession(
            steps=steps,
            total_duration=30,
            session_type="general",
            focus_areas=["general"],
            difficulty_range=(user_profile.preferred_difficulty, user_profile.preferred_difficulty),
            objectives=objectives
        )
        
        return LearningPath(
            id=f"fallback_{user_profile.user_id}_{subject}",
            user_id=user_profile.user_id,
            subject=subject,
            path_type=PathType.SEQUENTIAL,
            objectives=objectives,
            sessions=[session],
            total_duration=30,
            estimated_completion=datetime.now() + timedelta(days=1),
            created_at=datetime.now()
        )

    async def update_path_progress(
        self,
        path: LearningPath,
        completed_session_idx: int,
        session_results: Dict[str, Any]
    ) -> LearningPath:
        """
        Update learning path progress based on completed session
        """
        try:
            # Update progress
            path.current_session = min(completed_session_idx + 1, len(path.sessions))
            path.progress = path.current_session / len(path.sessions)
            
            # Store session results in metadata
            if 'session_results' not in path.metadata:
                path.metadata['session_results'] = {}
            
            path.metadata['session_results'][str(completed_session_idx)] = {
                'completed_at': datetime.now().isoformat(),
                'results': session_results
            }
            
            # Adjust future sessions based on performance
            if completed_session_idx < len(path.sessions) - 1:
                await self._adjust_future_sessions(path, session_results)
            
            return path
            
        except Exception as e:
            self.logger.error(f"Error updating path progress: {e}")
            return path

    async def _adjust_future_sessions(
        self,
        path: LearningPath,
        session_results: Dict[str, Any]
    ) -> None:
        """
        Adjust future sessions based on performance in completed session
        """
        try:
            session_accuracy = session_results.get('accuracy', 0.5)
            avg_time = session_results.get('average_time', 120)
            
            # Determine if adjustments are needed
            if session_accuracy > 0.8 and avg_time < 90:
                # Performing very well - can increase difficulty
                adjustment = 1
            elif session_accuracy < 0.4 or avg_time > 300:
                # Struggling - decrease difficulty
                adjustment = -1
            else:
                # No adjustment needed
                adjustment = 0
            
            if adjustment != 0:
                # Apply adjustment to remaining sessions
                for i in range(path.current_session, len(path.sessions)):
                    session = path.sessions[i]
                    for step in session.steps:
                        new_difficulty = max(1, min(4, step.difficulty + adjustment))
                        step.difficulty = new_difficulty
                    
                    # Update session difficulty range
                    min_diff = min(step.difficulty for step in session.steps)
                    max_diff = max(step.difficulty for step in session.steps)
                    session.difficulty_range = (min_diff, max_diff)
            
        except Exception as e:
            self.logger.error(f"Error adjusting future sessions: {e}")

    async def get_next_study_session(
        self,
        path: LearningPath,
        available_time: Optional[int] = None
    ) -> Optional[StudySession]:
        """
        Get the next study session from the learning path
        """
        try:
            if path.current_session >= len(path.sessions):
                return None  # Path completed
            
            next_session = path.sessions[path.current_session]
            
            # Adjust session if time constraints are provided
            if available_time and available_time < next_session.total_duration:
                # Create shortened version of the session
                adjusted_session = await self._adjust_session_for_time(
                    next_session, available_time
                )
                return adjusted_session
            
            return next_session
            
        except Exception as e:
            self.logger.error(f"Error getting next study session: {e}")
            return None

    async def _adjust_session_for_time(
        self,
        session: StudySession,
        available_time: int
    ) -> StudySession:
        """
        Adjust session to fit available time
        """
        if available_time >= session.total_duration:
            return session
        
        # Proportionally reduce each step
        time_ratio = available_time / session.total_duration
        
        adjusted_steps = []
        for step in session.steps:
            adjusted_duration = max(5, int(step.estimated_duration * time_ratio))
            adjusted_questions = max(1, int(step.question_count * time_ratio))
            
            adjusted_step = LearningStep(
                topic_id=step.topic_id,
                topic_name=step.topic_name,
                difficulty=step.difficulty,
                estimated_duration=adjusted_duration,
                question_count=adjusted_questions,
                step_type=step.step_type,
                metadata={**step.metadata, 'time_adjusted': True}
            )
            adjusted_steps.append(adjusted_step)
        
        return StudySession(
            steps=adjusted_steps,
            total_duration=available_time,
            session_type=f"{session.session_type}_adjusted",
            focus_areas=session.focus_areas,
            difficulty_range=session.difficulty_range,
            objectives=session.objectives
        )

    def get_path_analytics(self, path: LearningPath) -> Dict[str, Any]:
        """
        Get analytics and insights about the learning path
        """
        session_results = path.metadata.get('session_results', {})
        
        if not session_results:
            return {
                'completion_rate': path.progress,
                'average_accuracy': 0.0,
                'total_study_time': 0,
                'weak_areas': [],
                'strong_areas': [],
                'recommendations': []
            }
        
        # Calculate metrics from completed sessions
        accuracies = []
        study_times = []
        topic_performance = defaultdict(list)
        
        for session_idx, results in session_results.items():
            session_data = results.get('results', {})
            accuracy = session_data.get('accuracy', 0)
            time_spent = session_data.get('time_spent', 0)
            
            accuracies.append(accuracy)
            study_times.append(time_spent)
            
            # Track topic performance
            if int(session_idx) < len(path.sessions):
                session = path.sessions[int(session_idx)]
                for topic in session.focus_areas:
                    topic_performance[topic].append(accuracy)
        
        # Calculate topic strengths and weaknesses
        weak_areas = []
        strong_areas = []
        
        for topic, accuracies_list in topic_performance.items():
            avg_accuracy = sum(accuracies_list) / len(accuracies_list)
            if avg_accuracy < 0.6:
                weak_areas.append(topic)
            elif avg_accuracy > 0.8:
                strong_areas.append(topic)
        
        # Generate recommendations
        recommendations = []
        avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
        
        if avg_accuracy < 0.6:
            recommendations.append("Consider reviewing fundamental concepts")
        if weak_areas:
            recommendations.append(f"Focus additional practice on: {', '.join(weak_areas[:3])}")
        if path.progress < 0.5 and len(accuracies) > 2:
            recent_trend = accuracies[-2:]
            if recent_trend[1] > recent_trend[0]:
                recommendations.append("Good progress! Keep up the current pace")
            else:
                recommendations.append("Consider adjusting study approach or taking a short break")
        
        return {
            'completion_rate': path.progress,
            'average_accuracy': avg_accuracy,
            'total_study_time': sum(study_times),
            'sessions_completed': len(session_results),
            'weak_areas': weak_areas,
            'strong_areas': strong_areas,
            'recommendations': recommendations,
            'estimated_completion': path.estimated_completion.isoformat()
        }