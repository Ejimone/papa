class AdaptiveDifficultyEngine:
    def __init__(self):
        self.difficulty_calculator = DifficultyCalculator()
        self.performance_tracker = PerformanceTracker()
        self.confidence_estimator = ConfidenceEstimator()
    
    async def calculate_next_difficulty(self, user_id: str, subject: str, current_session: List[UserAttempt]) -> float:
        # Get user's current performance level
        current_performance = await self.performance_tracker.get_current_performance(
            user_id, subject
        )
        
        # Analyze current session performance
        session_analysis = self.analyze_session_performance(current_session)
        
        # Calculate confidence in current difficulty
        confidence_score = await self.confidence_estimator.estimate_confidence(
            current_performance, session_analysis
        )
        
        # Determine difficulty adjustment
        if confidence_score > 0.8 and session_analysis.accuracy > 0.75:
            # Increase difficulty
            new_difficulty = min(current_performance.difficulty_level + 0.2, 5.0)
        elif confidence_score < 0.4 or session_analysis.accuracy < 0.5:
            # Decrease difficulty
            new_difficulty = max(current_performance.difficulty_level - 0.3, 1.0)
        else:
            # Maintain current difficulty with slight adjustment
            new_difficulty = current_performance.difficulty_level + random.uniform(-0.1, 0.1)
        
        return new_difficulty
    
    async def select_adaptive_questions(self, user_id: str, subject: str, count: int) -> List[AdaptiveQuestion]:
        # Get target difficulty
        target_difficulty = await self.calculate_next_difficulty(user_id, subject, [])
        
        # Get user's weak areas
        user_profile = await self.get_user_profile(user_id)
        weak_areas = user_profile.knowledge_gaps.get(subject, [])
        
        # Create selection criteria
        selection_criteria = {
            'subject': subject,
            'difficulty_range': (target_difficulty - 0.5, target_difficulty + 0.5),
            'weak_areas': weak_areas,
            'exclude_recent': await self.get_recently_attempted_questions(user_id, subject),
            'priority_boost': True  # Prioritize frequently repeated questions
        }
        
        # Select questions using multiple strategies
        selected_questions = await self.multi_strategy_selection(
            selection_criteria, count
        )
        
        return selected_questions