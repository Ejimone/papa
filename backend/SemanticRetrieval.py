from typing import List

class SemanticRetrieval:
    def __init__(self, vector_store: ChromaVectorStore):
        self.vector_store = vector_store
        self.reranker = CrossEncoderReranker()
    
    async def find_similar_questions(self, question_id: str, filters: dict = None, top_k: int = 5) -> List[SimilarQuestion]:
        # Get the original question's embeddings
        original_embeddings = await self.vector_store.get_question_embeddings(question_id)
        
        # Search for similar questions using different embedding types
        similar_questions = []
        
        for embedding_type, embedding_vector in original_embeddings.items():
            results = await self.vector_store.vector_search(
                embedding_vector=embedding_vector,
                collection_name=f"questions_{embedding_type}",
                filters=filters,
                top_k=top_k * 2  # Get more candidates for reranking
            )
            similar_questions.extend(results)
        
        # Remove duplicates and original question
        unique_questions = self.deduplicate_results(similar_questions, question_id)
        
        # Rerank using cross-encoder for better relevance
        reranked_questions = await self.reranker.rerank(
            query_question_id=question_id,
            candidate_questions=unique_questions
        )
        
        return reranked_questions[:top_k]
    
    async def personalized_search(self, user_id: str, query: str, context: dict) -> List[SearchResult]:
        # Get user's learning patterns
        user_patterns = await self.get_user_learning_patterns(user_id)
        
        # Adjust search based on user's performance and preferences
        personalized_filters = self.create_personalized_filters(user_patterns, context)
        
        # Perform semantic search with personalization
        base_results = await self.vector_store.semantic_search(
            query=query,
            filters=personalized_filters,
            top_k=20
        )
        
        # Apply personalization scoring
        personalized_results = await self.apply_personalization_scoring(
            base_results, user_patterns
        )
        
        return personalized_results[:10]