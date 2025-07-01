from typing import List, Dict, Any, Optional, Tuple
import asyncio
import logging
from datetime import datetime, timedelta

from .user_modeling import UserProfile, QuestionInteraction, RecommendationScore
from ..vector_db.queries import VectorQueries, SearchResult
from ..embeddings.text_embeddings import TextEmbeddingService

class RecommendationEngine:
    def __init__(
        self,
        vector_queries: VectorQueries,
        embedding_service: TextEmbeddingService
    ):
        self.vector_queries = vector_queries
        self.embedding_service = embedding_service
        self.logger = logging.getLogger(__name__)
        
        # Recommendation weights
        self.weights = {
            'semantic_similarity': 0.3,
            'difficulty_match': 0.25,
            'subject_performance': 0.2,
            'learning_style_match': 0.15,
            'priority_boost': 0.1
        }

    async def generate_personalized_recommendations(
        self,
        user_profile: UserProfile,
        query_text: Optional[str] = None,
        subject_filter: Optional[str] = None,
        limit: int = 10,
        diversity_factor: float = 0.3
    ) -> List[RecommendationScore]:
        """
        Generate personalized question recommendations for a user
        """
        try:
            recommendations = []
            
            # Get base recommendations from different strategies
            if query_text:
                semantic_recs = await self._get_semantic_recommendations(
                    query_text, user_profile, subject_filter, limit * 2
                )
                recommendations.extend(semantic_recs)
            
            # Get weakness-based recommendations
            weakness_recs = await self._get_weakness_based_recommendations(
                user_profile, subject_filter, limit
            )
            recommendations.extend(weakness_recs)
            
            # Get adaptive difficulty recommendations
            adaptive_recs = await self._get_adaptive_difficulty_recommendations(
                user_profile, subject_filter, limit
            )
            recommendations.extend(adaptive_recs)
            
            # Get high-priority recommendations
            priority_recs = await self._get_priority_based_recommendations(
                user_profile, subject_filter, limit // 2
            )
            recommendations.extend(priority_recs)
            
            # Combine and rank recommendations
            final_recommendations = await self._combine_and_rank_recommendations(
                recommendations, user_profile, diversity_factor
            )
            
            return final_recommendations[:limit]
            
        except Exception as e:
            self.logger.error(f"Error generating personalized recommendations: {e}")
            return []

    async def _get_semantic_recommendations(
        self,
        query_text: str,
        user_profile: UserProfile,
        subject_filter: Optional[str],
        limit: int
    ) -> List[RecommendationScore]:
        """Get recommendations based on semantic similarity to query"""
        try:
            # Generate embedding for query
            query_embedding = await self.embedding_service.get_single_embedding(query_text)
            
            # Prepare filters
            filters = {}
            if subject_filter:
                filters['subject'] = subject_filter
            elif user_profile.subjects:
                filters['subject'] = {'$in': user_profile.subjects}
            
            # Search for similar questions
            search_results = await self.vector_queries.semantic_search_questions(
                query_embedding=[query_embedding],
                filters=filters,
                limit=limit,
                score_threshold=0.3
            )
            
            recommendations = []
            for result in search_results:
                score = RecommendationScore(
                    question_id=result.id,
                    score=result.score * self.weights['semantic_similarity'],
                    reasons=[f"Semantically similar to your query (similarity: {result.score:.2f})"],
                    metadata=result.metadata
                )
                recommendations.append(score)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error in semantic recommendations: {e}")
            return []

    async def _get_weakness_based_recommendations(
        self,
        user_profile: UserProfile,
        subject_filter: Optional[str],
        limit: int
    ) -> List[RecommendationScore]:
        """Get recommendations targeting user's weak areas"""
        try:
            recommendations = []
            
            # Focus on weak topics
            for weak_topic in user_profile.weak_areas[:3]:  # Top 3 weak areas
                # Create search query for this topic
                topic_query = f"questions about {weak_topic}"
                topic_embedding = await self.embedding_service.get_single_embedding(topic_query)
                
                filters = {'topic': weak_topic}
                if subject_filter:
                    filters['subject'] = subject_filter
                
                # Get questions slightly easier than user's preferred difficulty
                target_difficulty = max(1, user_profile.preferred_difficulty - 1)
                filters['difficulty'] = {'$lte': target_difficulty + 1, '$gte': target_difficulty - 1}
                
                search_results = await self.vector_queries.semantic_search_questions(
                    query_embedding=[topic_embedding],
                    filters=filters,
                    limit=limit // len(user_profile.weak_areas[:3]) + 1
                )
                
                for result in search_results:
                    score = RecommendationScore(
                        question_id=result.id,
                        score=0.8 * self.weights['subject_performance'],  # High weight for weakness
                        reasons=[f"Targets your weak area: {weak_topic}"],
                        metadata=result.metadata
                    )
                    recommendations.append(score)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error in weakness-based recommendations: {e}")
            return []

    async def _get_adaptive_difficulty_recommendations(
        self,
        user_profile: UserProfile,
        subject_filter: Optional[str],
        limit: int
    ) -> List[RecommendationScore]:
        """Get recommendations with adaptive difficulty"""
        try:
            recommendations = []
            
            # Get questions at user's preferred difficulty and adjacent levels
            difficulty_levels = [
                user_profile.preferred_difficulty,
                max(1, user_profile.preferred_difficulty - 1),
                min(4, user_profile.preferred_difficulty + 1)
            ]
            
            for difficulty in difficulty_levels:
                filters = {'difficulty': difficulty}
                if subject_filter:
                    filters['subject'] = subject_filter
                elif user_profile.subjects:
                    filters['subject'] = {'$in': user_profile.subjects}
                
                search_results = await self.vector_queries.search_by_subject_and_difficulty(
                    subject=subject_filter or user_profile.subjects[0] if user_profile.subjects else "mathematics",
                    difficulty_range=(difficulty, difficulty),
                    limit=limit // len(difficulty_levels) + 1
                )
                
                for result in search_results:
                    # Calculate difficulty match score
                    difficulty_diff = abs(difficulty - user_profile.preferred_difficulty)
                    difficulty_match = max(0, 1 - (difficulty_diff * 0.3))
                    
                    score = RecommendationScore(
                        question_id=result.id,
                        score=difficulty_match * self.weights['difficulty_match'],
                        reasons=[f"Matches your skill level (difficulty {difficulty})"],
                        metadata=result.metadata
                    )
                    recommendations.append(score)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error in adaptive difficulty recommendations: {e}")
            return []

    async def _get_priority_based_recommendations(
        self,
        user_profile: UserProfile,
        subject_filter: Optional[str],
        limit: int
    ) -> List[RecommendationScore]:
        """Get recommendations based on question priority/importance"""
        try:
            search_results = await self.vector_queries.search_high_priority_questions(
                subject=subject_filter,
                priority_threshold=0.7,
                limit=limit
            )
            
            recommendations = []
            for result in search_results:
                priority_score = result.metadata.get('priority_score', 0.0)
                score = RecommendationScore(
                    question_id=result.id,
                    score=priority_score * self.weights['priority_boost'],
                    reasons=[f"High priority question (frequently appears in exams)"],
                    metadata=result.metadata
                )
                recommendations.append(score)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error in priority-based recommendations: {e}")
            return []

    async def _combine_and_rank_recommendations(
        self,
        recommendations: List[RecommendationScore],
        user_profile: UserProfile,
        diversity_factor: float
    ) -> List[RecommendationScore]:
        """Combine recommendations from different sources and rank them"""
        try:
            # Group by question ID and combine scores
            combined_recs = {}
            
            for rec in recommendations:
                if rec.question_id in combined_recs:
                    # Combine scores and reasons
                    existing = combined_recs[rec.question_id]
                    existing.score += rec.score
                    existing.reasons.extend(rec.reasons)
                else:
                    combined_recs[rec.question_id] = rec
            
            # Apply additional scoring factors
            final_recs = []
            for rec in combined_recs.values():
                # Apply learning style bonus
                learning_style_bonus = self._calculate_learning_style_bonus(
                    rec.metadata.get('type', ''), user_profile.learning_style
                )
                rec.score += learning_style_bonus * self.weights['learning_style_match']
                
                # Apply recency penalty for recently attempted questions
                # (This would require tracking recent attempts - placeholder for now)
                
                final_recs.append(rec)
            
            # Sort by score and apply diversity
            final_recs.sort(key=lambda x: x.score, reverse=True)
            
            if diversity_factor > 0:
                final_recs = self._apply_diversity_filter(final_recs, diversity_factor)
            
            return final_recs
            
        except Exception as e:
            self.logger.error(f"Error combining recommendations: {e}")
            return list(combined_recs.values()) if 'combined_recs' in locals() else []

    def _calculate_learning_style_bonus(self, question_type: str, learning_style) -> float:
        """Calculate bonus score based on learning style match"""
        from .user_modeling import LearningStyle
        
        style_matches = {
            LearningStyle.VISUAL: {
                'diagram': 0.3, 'chart': 0.3, 'image_based': 0.3, 'multiple_choice': 0.2
            },
            LearningStyle.READING_WRITING: {
                'essay': 0.3, 'short_answer': 0.2, 'fill_in_blank': 0.2
            },
            LearningStyle.KINESTHETIC: {
                'numerical': 0.3, 'calculation': 0.3, 'practical': 0.3
            },
            LearningStyle.AUDITORY: {
                'listening': 0.3, 'pronunciation': 0.3
            },
            LearningStyle.MIXED: {}  # No specific bonus
        }
        
        matches = style_matches.get(learning_style, {})
        return matches.get(question_type, 0.0)

    def _apply_diversity_filter(
        self, 
        recommendations: List[RecommendationScore], 
        diversity_factor: float
    ) -> List[RecommendationScore]:
        """Apply diversity to avoid too many similar questions"""
        if not recommendations:
            return recommendations
        
        diverse_recs = [recommendations[0]]  # Always include top recommendation
        
        for rec in recommendations[1:]:
            # Check diversity against already selected recommendations
            is_diverse = True
            
            for selected in diverse_recs:
                # Simple diversity check based on subject and topic
                if (rec.metadata.get('subject') == selected.metadata.get('subject') and
                    rec.metadata.get('topic') == selected.metadata.get('topic')):
                    
                    # Apply diversity penalty
                    similarity_penalty = 1 - diversity_factor
                    if rec.score * similarity_penalty < selected.score * 0.8:
                        is_diverse = False
                        break
            
            if is_diverse:
                diverse_recs.append(rec)
        
        return diverse_recs

    async def get_similar_questions_for_practice(
        self,
        question_id: str,
        user_profile: UserProfile,
        limit: int = 5
    ) -> List[RecommendationScore]:
        """Get similar questions for additional practice"""
        try:
            similar_results = await self.vector_queries.find_similar_questions(
                question_id=question_id,
                similarity_threshold=0.6,
                limit=limit,
                exclude_same_subject=False
            )
            
            recommendations = []
            for result in similar_results:
                # Calculate relevance score based on user profile
                relevance_score = self._calculate_relevance_score(result, user_profile)
                
                score = RecommendationScore(
                    question_id=result.id,
                    score=relevance_score,
                    reasons=[f"Similar to your current question (similarity: {result.score:.2f})"],
                    metadata=result.metadata
                )
                recommendations.append(score)
            
            return sorted(recommendations, key=lambda x: x.score, reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error getting similar questions: {e}")
            return []

    def _calculate_relevance_score(self, result: SearchResult, user_profile: UserProfile) -> float:
        """Calculate how relevant a question is to the user"""
        base_score = result.score
        
        # Subject relevance
        subject = result.metadata.get('subject', '')
        if subject in user_profile.subjects:
            base_score *= 1.2
        
        # Difficulty appropriateness
        difficulty = result.metadata.get('difficulty', 2)
        difficulty_diff = abs(difficulty - user_profile.preferred_difficulty)
        if difficulty_diff == 0:
            base_score *= 1.1
        elif difficulty_diff > 2:
            base_score *= 0.8
        
        # Topic relevance (weak areas get boost)
        topic = result.metadata.get('topic', '')
        if topic in user_profile.weak_areas:
            base_score *= 1.3
        elif topic in user_profile.strong_areas:
            base_score *= 0.9  # Slight penalty for already strong areas
        
        return min(base_score, 1.0)

    async def generate_study_path(
        self,
        user_profile: UserProfile,
        subject: str,
        target_sessions: int = 5,
        questions_per_session: int = 10
    ) -> List[List[RecommendationScore]]:
        """Generate a progressive study path"""
        try:
            study_path = []
            
            # Start with current difficulty, gradually increase
            current_difficulty = max(1, user_profile.preferred_difficulty - 1)
            target_difficulty = min(4, user_profile.preferred_difficulty + 1)
            
            difficulty_progression = []
            for i in range(target_sessions):
                # Gradual difficulty increase
                progress_ratio = i / (target_sessions - 1) if target_sessions > 1 else 0
                session_difficulty = int(current_difficulty + 
                                      (target_difficulty - current_difficulty) * progress_ratio)
                difficulty_progression.append(session_difficulty)
            
            # Generate sessions
            for session_idx, difficulty in enumerate(difficulty_progression):
                session_recs = await self._generate_session_recommendations(
                    user_profile, subject, difficulty, questions_per_session, session_idx
                )
                study_path.append(session_recs)
            
            return study_path
            
        except Exception as e:
            self.logger.error(f"Error generating study path: {e}")
            return []

    async def _generate_session_recommendations(
        self,
        user_profile: UserProfile,
        subject: str,
        difficulty: int,
        question_count: int,
        session_index: int
    ) -> List[RecommendationScore]:
        """Generate recommendations for a single study session"""
        try:
            recommendations = []
            
            # Mix of question types for variety
            if session_index == 0:
                # First session: focus on weak areas
                weak_area_count = min(len(user_profile.weak_areas), question_count // 2)
                for i, weak_topic in enumerate(user_profile.weak_areas[:weak_area_count]):
                    topic_recs = await self._get_topic_specific_questions(
                        subject, weak_topic, difficulty, 2
                    )
                    recommendations.extend(topic_recs)
            
            # Fill remaining slots with general recommendations
            remaining_count = question_count - len(recommendations)
            if remaining_count > 0:
                general_recs = await self.vector_queries.search_by_subject_and_difficulty(
                    subject=subject,
                    difficulty_range=(difficulty, difficulty),
                    limit=remaining_count
                )
                
                for result in general_recs:
                    score = RecommendationScore(
                        question_id=result.id,
                        score=0.7,  # Base score for general recommendations
                        reasons=[f"Level {difficulty} {subject} practice"],
                        metadata=result.metadata
                    )
                    recommendations.append(score)
            
            return recommendations[:question_count]
            
        except Exception as e:
            self.logger.error(f"Error generating session recommendations: {e}")
            return []

    async def _get_topic_specific_questions(
        self,
        subject: str,
        topic: str,
        difficulty: int,
        limit: int
    ) -> List[RecommendationScore]:
        """Get questions for a specific topic"""
        try:
            # Create search query for topic
            topic_query = f"{subject} {topic} questions"
            topic_embedding = await self.embedding_service.get_single_embedding(topic_query)
            
            filters = {
                'subject': subject,
                'topic': topic,
                'difficulty': {'$lte': difficulty + 1, '$gte': max(1, difficulty - 1)}
            }
            
            search_results = await self.vector_queries.semantic_search_questions(
                query_embedding=[topic_embedding],
                filters=filters,
                limit=limit
            )
            
            recommendations = []
            for result in search_results:
                score = RecommendationScore(
                    question_id=result.id,
                    score=0.8,  # High score for targeted practice
                    reasons=[f"Targeted practice for {topic}"],
                    metadata=result.metadata
                )
                recommendations.append(score)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting topic-specific questions: {e}")
            return []