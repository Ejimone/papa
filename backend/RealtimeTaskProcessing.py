class AITaskProcessor:
    def __init__(self):
        self.celery_app = Celery('ai_tasks')
        self.task_queue = TaskQueue()
        self.result_cache = ResultCache()
    
    @celery_task(bind=True, retry_backoff=True, max_retries=3)
    async def process_question_content(self, question_data: dict):
        """Background task for processing uploaded questions"""
        try:
            # Process content through AI pipeline
            processed_content = await self.content_processor.process_content(
                question_data
            )
            
            # Generate embeddings
            embeddings = await self.embedding_pipeline.generate_embeddings(
                processed_content
            )
            
            # Store in vector database
            await self.vector_store.store_question_vectors(embeddings)
            
            # Update question metadata in PostgreSQL
            await self.update_question_metadata(
                question_data['question_id'],
                processed_content.ai_metadata
            )
            
            return {
                'status': 'success',
                'question_id': question_data['question_id'],
                'processing_time': time.time() - self.request.started_at
            }
            
        except Exception as exc:
            # Log error and retry
            logger.error(f"Question processing failed: {exc}")
            raise self.retry(exc=exc, countdown=60)
    
    @celery_task(bind=True)
    async def generate_ai_explanation(self, question_id: str, user_id: str):
        """Generate AI explanation for a question"""
        try:
            # Get question details
            question = await self.get_question_details(question_id)
            
            # Get user context for personalization
            user_context = await self.get_user_context(user_id)
            
            # Generate explanation using Gemini
            explanation = await self.gemini_service.generate_explanation(
                question=question,
                context=user_context
            )
            
            # Store explanation
            await self.store_explanation(question_id, explanation)
            
            # Cache for quick retrieval
            await self.result_cache.set(
                f"explanation:{question_id}:{user_id}",
                explanation,
                ttl=3600  # 1 hour cache
            )
            
            return explanation
            
        except Exception as exc:
            logger.error(f"Explanation generation failed: {exc}")
            raise



class RealtimeRecommendationEngine:
    def __init__(self):
        self.vector_store = ChromaVectorStore()
        self.user_modeler = UserModelingEngine()
        self.content_ranker = ContentRanker()
        self.cache = RecommendationCache()
    
    async def get_realtime_recommendations(self, user_id: str, context: dict) -> List[Recommendation]:
        # Check cache first
        cache_key = f"recommendations:{user_id}:{hash(str(context))}"
        cached_recommendations = await self.cache.get(cache_key)
        
        if cached_recommendations:
            return cached_recommendations
        
        # Get user's current state
        user_profile = await self.user_modeler.get_user_profile(user_id)
        current_session = await self.get_current_session_data(user_id)
        
        # Generate recommendations based on multiple signals
        recommendations = []
        
        # 1. Knowledge gap filling
        gap_based_recs = await self.generate_gap_based_recommendations(
            user_profile.knowledge_gaps, context
        )
        recommendations.extend(gap_based_recs)
        
        # 2. Similar questions to recently attempted
        if current_session.recent_questions:
            similar_recs = await self.generate_similar_question_recommendations(
                current_session.recent_questions, user_profile
            )
            recommendations.extend(similar_recs)
        
        # 3. Trending and priority questions
        trending_recs = await self.generate_trending_recommendations(
            user_profile, context
        )
        recommendations.extend(trending_recs)
        
        # 4. Spaced repetition candidates
        spaced_recs = await self.generate_spaced_repetition_recommendations(
            user_id, context
        )
        recommendations.extend(spaced_recs)
        
        # Rank and filter recommendations
        final_recommendations = await self.content_ranker.rank_recommendations(
            recommendations, user_profile, context
        )
        
        # Cache recommendations
        await self.cache.set(
            cache_key, 
            final_recommendations[:10], 
            ttl=300  # 5 minutes cache
        )
        
        return final_recommendations[:10]
    
    async def update_recommendations_realtime(self, user_id: str, user_action: UserAction):
        """Update recommendations based on real-time user actions"""
        # Invalidate relevant caches
        await self.cache.invalidate_pattern(f"recommendations:{user_id}:*")
        
        # Update user model incrementally
        await self.user_modeler.increment_user_model(user_id, user_action)
        
        # Trigger background recommendation refresh
        await self.trigger_background_refresh(user_id)