from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import math
from collections import defaultdict, Counter

class LearningStyle(Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"
    MIXED = "mixed"

class PerformanceLevel(Enum):
    STRUGGLING = "struggling"
    DEVELOPING = "developing"
    PROFICIENT = "proficient"
    ADVANCED = "advanced"

@dataclass
class UserProfile:
    user_id: str
    academic_level: str
    subjects: List[str]
    learning_style: LearningStyle
    study_goals: List[str]
    performance_levels: Dict[str, PerformanceLevel] = field(default_factory=dict)
    weak_areas: List[str] = field(default_factory=list)
    strong_areas: List[str] = field(default_factory=list)
    preferred_difficulty: int = 2
    study_time_preference: int = 30  # minutes
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class QuestionInteraction:
    question_id: str
    subject: str
    topic: str
    difficulty: int
    question_type: str
    is_correct: bool
    time_taken: int  # seconds
    attempts: int
    hint_used: bool
    timestamp: datetime
    confidence_level: Optional[float] = None

@dataclass
class RecommendationScore:
    question_id: str
    score: float
    reasons: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

class UserModelingService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.min_interactions_for_modeling = 5
        self.confidence_threshold = 0.6
        
    async def build_user_profile(
        self, 
        user_id: str, 
        interactions: List[QuestionInteraction],
        initial_preferences: Optional[Dict[str, Any]] = None
    ) -> UserProfile:
        """
        Build comprehensive user profile from interaction history
        """
        try:
            # Initialize profile with defaults or provided preferences
            profile = UserProfile(
                user_id=user_id,
                academic_level=initial_preferences.get('academic_level', 'undergraduate') if initial_preferences else 'undergraduate',
                subjects=initial_preferences.get('subjects', []) if initial_preferences else [],
                learning_style=LearningStyle(initial_preferences.get('learning_style', 'mixed')) if initial_preferences else LearningStyle.MIXED,
                study_goals=initial_preferences.get('study_goals', []) if initial_preferences else []
            )
            
            if len(interactions) < self.min_interactions_for_modeling:
                self.logger.info(f"Insufficient interactions ({len(interactions)}) for user {user_id}, using defaults")
                return profile
            
            # Analyze performance by subject
            profile.performance_levels = await self._analyze_subject_performance(interactions)
            
            # Identify weak and strong areas
            profile.weak_areas, profile.strong_areas = await self._identify_strength_weaknesses(interactions)
            
            # Determine preferred difficulty
            profile.preferred_difficulty = await self._calculate_preferred_difficulty(interactions)
            
            # Infer learning style from interaction patterns
            profile.learning_style = await self._infer_learning_style(interactions)
            
            # Calculate optimal study time
            profile.study_time_preference = await self._calculate_optimal_study_time(interactions)
            
            profile.last_updated = datetime.now()
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Error building user profile for {user_id}: {e}")
            raise

    async def _analyze_subject_performance(self, interactions: List[QuestionInteraction]) -> Dict[str, PerformanceLevel]:
        """Analyze performance by subject"""
        subject_stats = defaultdict(lambda: {'correct': 0, 'total': 0, 'avg_time': 0, 'avg_attempts': 0})
        
        for interaction in interactions:
            stats = subject_stats[interaction.subject]
            stats['total'] += 1
            if interaction.is_correct:
                stats['correct'] += 1
            stats['avg_time'] += interaction.time_taken
            stats['avg_attempts'] += interaction.attempts
        
        performance_levels = {}
        for subject, stats in subject_stats.items():
            if stats['total'] > 0:
                accuracy = stats['correct'] / stats['total']
                avg_time = stats['avg_time'] / stats['total']
                avg_attempts = stats['avg_attempts'] / stats['total']
                
                # Calculate performance score (0-1)
                time_score = max(0, 1 - (avg_time - 60) / 300)  # Normalize around 1-5 minutes
                attempt_score = max(0, 2 - avg_attempts)  # Penalize multiple attempts
                
                overall_score = (accuracy * 0.6) + (time_score * 0.2) + (attempt_score * 0.2)
                
                if overall_score >= 0.8:
                    performance_levels[subject] = PerformanceLevel.ADVANCED
                elif overall_score >= 0.65:
                    performance_levels[subject] = PerformanceLevel.PROFICIENT
                elif overall_score >= 0.4:
                    performance_levels[subject] = PerformanceLevel.DEVELOPING
                else:
                    performance_levels[subject] = PerformanceLevel.STRUGGLING
        
        return performance_levels

    async def _identify_strength_weaknesses(self, interactions: List[QuestionInteraction]) -> Tuple[List[str], List[str]]:
        """Identify weak and strong topic areas"""
        topic_performance = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        for interaction in interactions:
            topic_performance[interaction.topic]['total'] += 1
            if interaction.is_correct:
                topic_performance[interaction.topic]['correct'] += 1
        
        weak_areas = []
        strong_areas = []
        
        for topic, stats in topic_performance.items():
            if stats['total'] >= 3:  # Minimum interactions to consider
                accuracy = stats['correct'] / stats['total']
                if accuracy < 0.5:
                    weak_areas.append(topic)
                elif accuracy > 0.8:
                    strong_areas.append(topic)
        
        # Sort by performance (worst first for weak areas, best first for strong areas)
        weak_areas.sort(key=lambda t: topic_performance[t]['correct'] / topic_performance[t]['total'])
        strong_areas.sort(key=lambda t: topic_performance[t]['correct'] / topic_performance[t]['total'], reverse=True)
        
        return weak_areas[:10], strong_areas[:10]  # Limit to top 10 each

    async def _calculate_preferred_difficulty(self, interactions: List[QuestionInteraction]) -> int:
        """Calculate user's preferred difficulty level based on performance"""
        difficulty_performance = defaultdict(lambda: {'correct': 0, 'total': 0, 'satisfaction': 0})
        
        for interaction in interactions:
            diff_stats = difficulty_performance[interaction.difficulty]
            diff_stats['total'] += 1
            if interaction.is_correct:
                diff_stats['correct'] += 1
            
            # Calculate satisfaction score based on time and attempts
            if interaction.is_correct and interaction.attempts == 1 and 30 <= interaction.time_taken <= 180:
                diff_stats['satisfaction'] += 1
        
        best_difficulty = 2  # Default
        best_score = 0
        
        for difficulty, stats in difficulty_performance.items():
            if stats['total'] >= 3:
                accuracy = stats['correct'] / stats['total']
                satisfaction = stats['satisfaction'] / stats['total']
                
                # Optimal difficulty balances accuracy (60-80%) with satisfaction
                target_accuracy = 0.7
                accuracy_score = 1 - abs(accuracy - target_accuracy) / target_accuracy
                combined_score = (accuracy_score * 0.7) + (satisfaction * 0.3)
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_difficulty = difficulty
        
        return max(1, min(4, best_difficulty))

    async def _infer_learning_style(self, interactions: List[QuestionInteraction]) -> LearningStyle:
        """Infer learning style from interaction patterns"""
        style_indicators = {
            LearningStyle.VISUAL: 0,
            LearningStyle.READING_WRITING: 0,
            LearningStyle.KINESTHETIC: 0,
            LearningStyle.AUDITORY: 0
        }
        
        # Analyze question type preferences
        type_performance = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        for interaction in interactions:
            type_performance[interaction.question_type]['total'] += 1
            if interaction.is_correct:
                type_performance[interaction.question_type]['correct'] += 1
        
        # Map question types to learning styles
        for q_type, stats in type_performance.items():
            if stats['total'] >= 2:
                accuracy = stats['correct'] / stats['total']
                
                # Visual learners perform better with diagrams, charts, images
                if q_type in ['diagram', 'chart', 'image_based', 'multiple_choice']:
                    style_indicators[LearningStyle.VISUAL] += accuracy
                
                # Reading/Writing learners prefer text-based questions
                elif q_type in ['essay', 'short_answer', 'fill_in_blank']:
                    style_indicators[LearningStyle.READING_WRITING] += accuracy
                
                # Kinesthetic learners prefer hands-on, problem-solving
                elif q_type in ['numerical', 'calculation', 'practical']:
                    style_indicators[LearningStyle.KINESTHETIC] += accuracy
        
        # Find dominant style
        max_score = max(style_indicators.values())
        if max_score > 0:
            for style, score in style_indicators.items():
                if score == max_score:
                    return style
        
        return LearningStyle.MIXED

    async def _calculate_optimal_study_time(self, interactions: List[QuestionInteraction]) -> int:
        """Calculate optimal study session duration"""
        # Analyze performance over time in sessions
        sessions = self._group_interactions_by_session(interactions)
        
        best_duration = 30  # Default
        best_performance = 0
        
        for session in sessions:
            if len(session) >= 3:
                duration_minutes = (session[-1].timestamp - session[0].timestamp).total_seconds() / 60
                
                # Calculate session performance
                correct_answers = sum(1 for i in session if i.is_correct)
                accuracy = correct_answers / len(session)
                
                # Factor in diminishing returns over time
                time_efficiency = min(1.0, 60 / max(duration_minutes, 10))
                performance_score = accuracy * time_efficiency
                
                if performance_score > best_performance and 10 <= duration_minutes <= 120:
                    best_performance = performance_score
                    best_duration = int(duration_minutes)
        
        return max(15, min(90, best_duration))

    def _group_interactions_by_session(self, interactions: List[QuestionInteraction]) -> List[List[QuestionInteraction]]:
        """Group interactions into study sessions based on time gaps"""
        if not interactions:
            return []
        
        # Sort by timestamp
        sorted_interactions = sorted(interactions, key=lambda x: x.timestamp)
        
        sessions = []
        current_session = [sorted_interactions[0]]
        
        for i in range(1, len(sorted_interactions)):
            # If gap is more than 30 minutes, start new session
            time_gap = (sorted_interactions[i].timestamp - sorted_interactions[i-1].timestamp).total_seconds()
            
            if time_gap > 1800:  # 30 minutes
                sessions.append(current_session)
                current_session = [sorted_interactions[i]]
            else:
                current_session.append(sorted_interactions[i])
        
        sessions.append(current_session)
        return sessions

    async def predict_performance(
        self, 
        profile: UserProfile, 
        question_metadata: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Predict user performance on a given question
        """
        try:
            prediction = {
                'success_probability': 0.5,
                'estimated_time': 120,  # seconds
                'difficulty_match': 0.5,
                'confidence': 0.5
            }
            
            subject = question_metadata.get('subject', '')
            topic = question_metadata.get('topic', '')
            difficulty = question_metadata.get('difficulty', 2)
            question_type = question_metadata.get('type', '')
            
            # Base probability from subject performance
            if subject in profile.performance_levels:
                performance_level = profile.performance_levels[subject]
                if performance_level == PerformanceLevel.ADVANCED:
                    prediction['success_probability'] = 0.85
                elif performance_level == PerformanceLevel.PROFICIENT:
                    prediction['success_probability'] = 0.7
                elif performance_level == PerformanceLevel.DEVELOPING:
                    prediction['success_probability'] = 0.55
                else:  # STRUGGLING
                    prediction['success_probability'] = 0.3
            
            # Adjust for topic-specific weaknesses/strengths
            if topic in profile.weak_areas:
                prediction['success_probability'] *= 0.7
            elif topic in profile.strong_areas:
                prediction['success_probability'] *= 1.2
            
            # Adjust for difficulty match
            difficulty_diff = abs(difficulty - profile.preferred_difficulty)
            if difficulty_diff == 0:
                prediction['difficulty_match'] = 1.0
                prediction['success_probability'] *= 1.1
            elif difficulty_diff == 1:
                prediction['difficulty_match'] = 0.8
                prediction['success_probability'] *= 0.95
            elif difficulty_diff == 2:
                prediction['difficulty_match'] = 0.6
                prediction['success_probability'] *= 0.85
            else:
                prediction['difficulty_match'] = 0.3
                prediction['success_probability'] *= 0.7
            
            # Adjust for learning style compatibility
            learning_style_match = self._calculate_learning_style_match(
                profile.learning_style, question_type
            )
            prediction['success_probability'] *= learning_style_match
            
            # Estimate time based on difficulty and user performance
            base_time = 60 + (difficulty * 30)  # Base time increases with difficulty
            performance_multiplier = 2.0 - prediction['success_probability']  # Worse performance = more time
            prediction['estimated_time'] = int(base_time * performance_multiplier)
            
            # Calculate overall confidence in prediction
            factors_considered = [
                1.0 if subject in profile.performance_levels else 0.5,
                1.0 if topic in (profile.weak_areas + profile.strong_areas) else 0.5,
                prediction['difficulty_match'],
                learning_style_match
            ]
            prediction['confidence'] = sum(factors_considered) / len(factors_considered)
            
            # Ensure probabilities are within valid range
            prediction['success_probability'] = max(0.1, min(0.95, prediction['success_probability']))
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error predicting performance: {e}")
            return {
                'success_probability': 0.5,
                'estimated_time': 120,
                'difficulty_match': 0.5,
                'confidence': 0.3
            }

    def _calculate_learning_style_match(self, learning_style: LearningStyle, question_type: str) -> float:
        """Calculate how well a question type matches the user's learning style"""
        matches = {
            LearningStyle.VISUAL: {
                'diagram': 1.0, 'chart': 1.0, 'image_based': 1.0, 'multiple_choice': 0.8,
                'graph': 1.0, 'flowchart': 1.0
            },
            LearningStyle.READING_WRITING: {
                'essay': 1.0, 'short_answer': 0.9, 'fill_in_blank': 0.8, 'text_analysis': 1.0,
                'definition': 0.9
            },
            LearningStyle.KINESTHETIC: {
                'numerical': 1.0, 'calculation': 1.0, 'practical': 1.0, 'problem_solving': 0.9,
                'simulation': 1.0
            },
            LearningStyle.AUDITORY: {
                'listening': 1.0, 'pronunciation': 1.0, 'audio_based': 1.0
            },
            LearningStyle.MIXED: {}  # Mixed learners adapt to all types
        }
        
        if learning_style == LearningStyle.MIXED:
            return 0.9  # Mixed learners are adaptable
        
        style_matches = matches.get(learning_style, {})
        return style_matches.get(question_type, 0.7)  # Default moderate match

    async def update_profile_with_interaction(
        self, 
        profile: UserProfile, 
        interaction: QuestionInteraction
    ) -> UserProfile:
        """
        Update user profile based on new interaction
        """
        try:
            # This would typically involve re-analyzing with the new interaction
            # For now, we'll do simple updates
            
            # Update weak/strong areas based on recent performance
            if not interaction.is_correct and interaction.topic not in profile.weak_areas:
                profile.weak_areas.append(interaction.topic)
                # Limit weak areas list
                profile.weak_areas = profile.weak_areas[-15:]
            
            elif interaction.is_correct and interaction.topic in profile.weak_areas:
                # Remove from weak areas if showing improvement
                profile.weak_areas.remove(interaction.topic)
                if interaction.topic not in profile.strong_areas:
                    profile.strong_areas.append(interaction.topic)
            
            # Update performance level for subject
            if interaction.subject in profile.performance_levels:
                current_level = profile.performance_levels[interaction.subject]
                
                # Simple adjustment based on recent performance
                if interaction.is_correct and interaction.attempts == 1:
                    # Good performance - potentially move up
                    if current_level == PerformanceLevel.STRUGGLING:
                        profile.performance_levels[interaction.subject] = PerformanceLevel.DEVELOPING
                    elif current_level == PerformanceLevel.DEVELOPING:
                        profile.performance_levels[interaction.subject] = PerformanceLevel.PROFICIENT
                    elif current_level == PerformanceLevel.PROFICIENT:
                        profile.performance_levels[interaction.subject] = PerformanceLevel.ADVANCED
                
                elif not interaction.is_correct or interaction.attempts > 2:
                    # Poor performance - potentially move down
                    if current_level == PerformanceLevel.ADVANCED:
                        profile.performance_levels[interaction.subject] = PerformanceLevel.PROFICIENT
                    elif current_level == PerformanceLevel.PROFICIENT:
                        profile.performance_levels[interaction.subject] = PerformanceLevel.DEVELOPING
                    elif current_level == PerformanceLevel.DEVELOPING:
                        profile.performance_levels[interaction.subject] = PerformanceLevel.STRUGGLING
            
            profile.last_updated = datetime.now()
            return profile
            
        except Exception as e:
            self.logger.error(f"Error updating profile with interaction: {e}")
            return profile

    async def generate_learning_insights(self, profile: UserProfile, recent_interactions: List[QuestionInteraction]) -> Dict[str, Any]:
        """
        Generate insights about user's learning patterns and progress
        """
        try:
            insights = {
                'progress_summary': {},
                'recommendations': [],
                'learning_patterns': {},
                'performance_trends': {},
                'study_habits': {}
            }
            
            if not recent_interactions:
                return insights
            
            # Progress summary
            recent_performance = self._analyze_recent_performance(recent_interactions)
            insights['progress_summary'] = recent_performance
            
            # Learning patterns
            insights['learning_patterns'] = {
                'preferred_difficulty': profile.preferred_difficulty,
                'learning_style': profile.learning_style.value,
                'optimal_study_duration': profile.study_time_preference,
                'most_active_times': self._analyze_study_times(recent_interactions),
                'question_type_preferences': self._analyze_question_type_preferences(recent_interactions)
            }
            
            # Performance trends
            insights['performance_trends'] = self._analyze_performance_trends(recent_interactions)
            
            # Study habits analysis
            insights['study_habits'] = self._analyze_study_habits(recent_interactions)
            
            # Generate recommendations
            insights['recommendations'] = await self._generate_study_recommendations(profile, recent_interactions)
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating learning insights: {e}")
            return {}

    def _analyze_recent_performance(self, interactions: List[QuestionInteraction]) -> Dict[str, Any]:
        """Analyze recent performance metrics"""
        if not interactions:
            return {}
        
        # Last 7 days performance
        week_ago = datetime.now() - timedelta(days=7)
        recent = [i for i in interactions if i.timestamp >= week_ago]
        
        if not recent:
            return {}
        
        total_questions = len(recent)
        correct_answers = sum(1 for i in recent if i.is_correct)
        accuracy = correct_answers / total_questions
        
        avg_time = sum(i.time_taken for i in recent) / total_questions
        avg_attempts = sum(i.attempts for i in recent) / total_questions
        
        return {
            'total_questions_this_week': total_questions,
            'accuracy': round(accuracy, 3),
            'average_time_per_question': round(avg_time, 1),
            'average_attempts_per_question': round(avg_attempts, 2),
            'subjects_practiced': len(set(i.subject for i in recent)),
            'improvement_areas': [i.topic for i in recent if not i.is_correct]
        }

    def _analyze_study_times(self, interactions: List[QuestionInteraction]) -> List[str]:
        """Analyze when user is most active"""
        hour_counts = defaultdict(int)
        
        for interaction in interactions:
            hour = interaction.timestamp.hour
            hour_counts[hour] += 1
        
        # Find top 3 most active hours
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        top_hours = [f"{hour:02d}:00" for hour, _ in sorted_hours[:3]]
        
        return top_hours

    def _analyze_question_type_preferences(self, interactions: List[QuestionInteraction]) -> Dict[str, float]:
        """Analyze performance by question type"""
        type_performance = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        for interaction in interactions:
            type_performance[interaction.question_type]['total'] += 1
            if interaction.is_correct:
                type_performance[interaction.question_type]['correct'] += 1
        
        preferences = {}
        for q_type, stats in type_performance.items():
            if stats['total'] >= 2:
                accuracy = stats['correct'] / stats['total']
                preferences[q_type] = round(accuracy, 3)
        
        return preferences

    def _analyze_performance_trends(self, interactions: List[QuestionInteraction]) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        if len(interactions) < 10:
            return {'trend': 'insufficient_data'}
        
        # Sort by timestamp
        sorted_interactions = sorted(interactions, key=lambda x: x.timestamp)
        
        # Split into two halves
        mid_point = len(sorted_interactions) // 2
        first_half = sorted_interactions[:mid_point]
        second_half = sorted_interactions[mid_point:]
        
        first_accuracy = sum(1 for i in first_half if i.is_correct) / len(first_half)
        second_accuracy = sum(1 for i in second_half if i.is_correct) / len(second_half)
        
        improvement = second_accuracy - first_accuracy
        
        trend = 'stable'
        if improvement > 0.1:
            trend = 'improving'
        elif improvement < -0.1:
            trend = 'declining'
        
        return {
            'trend': trend,
            'improvement_rate': round(improvement, 3),
            'early_accuracy': round(first_accuracy, 3),
            'recent_accuracy': round(second_accuracy, 3)
        }

    def _analyze_study_habits(self, interactions: List[QuestionInteraction]) -> Dict[str, Any]:
        """Analyze study habits and patterns"""
        sessions = self._group_interactions_by_session(interactions)
        
        if not sessions:
            return {}
        
        session_lengths = [len(session) for session in sessions]
        session_durations = [
            (session[-1].timestamp - session[0].timestamp).total_seconds() / 60
            for session in sessions if len(session) > 1
        ]
        
        habits = {
            'average_session_length': round(sum(session_lengths) / len(session_lengths), 1),
            'average_session_duration_minutes': round(sum(session_durations) / len(session_durations), 1) if session_durations else 0,
            'total_sessions': len(sessions),
            'study_consistency': self._calculate_study_consistency(interactions)
        }
        
        return habits

    def _calculate_study_consistency(self, interactions: List[QuestionInteraction]) -> str:
        """Calculate how consistent the user's study pattern is"""
        if len(interactions) < 7:
            return 'insufficient_data'
        
        # Group by date
        dates = defaultdict(int)
        for interaction in interactions:
            date = interaction.timestamp.date()
            dates[date] += 1
        
        # Check if user studies regularly
        total_days = len(dates)
        time_span = (max(dates.keys()) - min(dates.keys())).days + 1
        
        consistency_ratio = total_days / time_span
        
        if consistency_ratio >= 0.7:
            return 'very_consistent'
        elif consistency_ratio >= 0.5:
            return 'moderately_consistent'
        elif consistency_ratio >= 0.3:
            return 'somewhat_consistent'
        else:
            return 'inconsistent'

    async def _generate_study_recommendations(self, profile: UserProfile, interactions: List[QuestionInteraction]) -> List[str]:
        """Generate personalized study recommendations"""
        recommendations = []
        
        # Recommendations based on weak areas
        if profile.weak_areas:
            recommendations.append(f"Focus on improving in: {', '.join(profile.weak_areas[:3])}")
        
        # Recommendations based on performance level
        struggling_subjects = [
            subject for subject, level in profile.performance_levels.items()
            if level == PerformanceLevel.STRUGGLING
        ]
        
        if struggling_subjects:
            recommendations.append(f"Consider additional practice in: {', '.join(struggling_subjects)}")
        
        # Recommendations based on study habits
        recent_sessions = self._group_interactions_by_session(interactions[-50:])  # Last 50 interactions
        
        if recent_sessions:
            avg_session_length = sum(len(session) for session in recent_sessions) / len(recent_sessions)
            
            if avg_session_length < 5:
                recommendations.append("Try longer study sessions (10-15 questions) for better retention")
            elif avg_session_length > 20:
                recommendations.append("Consider shorter, more focused study sessions")
        
        # Difficulty recommendations
        recent_accuracy = sum(1 for i in interactions[-20:] if i.is_correct) / min(20, len(interactions)) if interactions else 0
        
        if recent_accuracy > 0.85:
            recommendations.append("You're doing great! Try increasing difficulty level for more challenge")
        elif recent_accuracy < 0.5:
            recommendations.append("Consider practicing easier questions to build confidence")
        
        return recommendations[:5]  # Limit to top 5 recommendations