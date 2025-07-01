from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
from .client import ChromaDBClient, QUESTIONS_COLLECTION_NAME, USER_LEARNING_COLLECTION_NAME

@dataclass
class SearchResult:
    id: str
    content: str
    metadata: Dict[str, Any]
    score: float
    distance: float

@dataclass
class SemanticSearchQuery:
    query_text: str
    query_embedding: List[float]
    filters: Optional[Dict[str, Any]] = None
    limit: int = 10
    score_threshold: float = 0.0

class VectorQueries:
    def __init__(self, chroma_client: ChromaDBClient):
        self.client = chroma_client
        self.logger = logging.getLogger(__name__)

    async def semantic_search_questions(
        self,
        query_embedding: List[List[float]],
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        include_metadata: bool = True,
        score_threshold: float = 0.0
    ) -> List[SearchResult]:
        """
        Perform semantic search on questions collection
        """
        try:
            include_list = ["documents", "distances"]
            if include_metadata:
                include_list.append("metadatas")

            results = self.client.query_collection(
                collection_name=QUESTIONS_COLLECTION_NAME,
                query_embeddings=query_embedding,
                n_results=limit,
                where=filters,
                include=include_list
            )

            search_results = []
            if results and results.get('ids'):
                for i in range(len(results['ids'][0])):
                    # Calculate similarity score from distance
                    distance = results['distances'][0][i]
                    score = 1 - distance  # Convert distance to similarity score

                    if score >= score_threshold:
                        search_result = SearchResult(
                            id=results['ids'][0][i],
                            content=results['documents'][0][i] if 'documents' in results else "",
                            metadata=results['metadatas'][0][i] if 'metadatas' in results else {},
                            score=score,
                            distance=distance
                        )
                        search_results.append(search_result)

            return sorted(search_results, key=lambda x: x.score, reverse=True)

        except Exception as e:
            self.logger.error(f"Error in semantic search: {e}")
            raise

    async def find_similar_questions(
        self,
        question_id: str,
        similarity_threshold: float = 0.7,
        limit: int = 5,
        exclude_same_subject: bool = False
    ) -> List[SearchResult]:
        """
        Find questions similar to a given question
        """
        try:
            # First, get the question's embedding
            question_data = self.client.get_document_by_id(
                collection_name=QUESTIONS_COLLECTION_NAME,
                doc_id=question_id,
                include=["metadatas", "documents"]
            )

            if not question_data or not question_data.get('ids'):
                raise ValueError(f"Question with ID {question_id} not found")

            # Get the embedding for this question
            question_vector = self.client.questions_collection.get(
                ids=[question_id],
                include=["embeddings"]
            )

            if not question_vector or not question_vector.get('embeddings'):
                raise ValueError(f"No embedding found for question {question_id}")

            # Prepare filters
            filters = {}
            if exclude_same_subject and question_data['metadatas'][0].get('subject'):
                filters = {"subject": {"$ne": question_data['metadatas'][0]['subject']}}

            # Perform similarity search
            similar_results = await self.semantic_search_questions(
                query_embedding=question_vector['embeddings'],
                filters=filters,
                limit=limit + 1,  # +1 to account for the original question
                score_threshold=similarity_threshold
            )

            # Filter out the original question
            filtered_results = [
                result for result in similar_results 
                if result.id != question_id
            ]

            return filtered_results[:limit]

        except Exception as e:
            self.logger.error(f"Error finding similar questions: {e}")
            raise

    async def search_by_subject_and_difficulty(
        self,
        subject: str,
        difficulty_range: Tuple[int, int] = (1, 4),
        question_type: Optional[str] = None,
        limit: int = 20
    ) -> List[SearchResult]:
        """
        Search questions by subject and difficulty level
        """
        try:
            filters = {
                "subject": subject,
                "difficulty": {"$gte": difficulty_range[0], "$lte": difficulty_range[1]}
            }

            if question_type:
                filters["type"] = question_type

            # Since this is not a semantic search, we'll use a dummy embedding
            # and rely on metadata filtering
            dummy_embedding = [[0.0] * 768]  # Assuming 768-dimensional embeddings

            results = self.client.query_collection(
                collection_name=QUESTIONS_COLLECTION_NAME,
                query_embeddings=dummy_embedding,
                n_results=limit,
                where=filters,
                include=["metadatas", "documents", "distances"]
            )

            search_results = []
            if results and results.get('ids'):
                for i in range(len(results['ids'][0])):
                    search_result = SearchResult(
                        id=results['ids'][0][i],
                        content=results['documents'][0][i] if 'documents' in results else "",
                        metadata=results['metadatas'][0][i] if 'metadatas' in results else {},
                        score=1.0,  # All results have equal score for filter-based search
                        distance=0.0
                    )
                    search_results.append(search_result)

            return search_results

        except Exception as e:
            self.logger.error(f"Error in subject/difficulty search: {e}")
            raise

    async def search_high_priority_questions(
        self,
        subject: Optional[str] = None,
        priority_threshold: float = 0.7,
        limit: int = 10
    ) -> List[SearchResult]:
        """
        Search for high-priority (frequently repeated) questions
        """
        try:
            filters = {"priority_score": {"$gte": priority_threshold}}
            
            if subject:
                filters["subject"] = subject

            # Use dummy embedding for metadata-based search
            dummy_embedding = [[0.0] * 768]

            results = self.client.query_collection(
                collection_name=QUESTIONS_COLLECTION_NAME,
                query_embeddings=dummy_embedding,
                n_results=limit,
                where=filters,
                include=["metadatas", "documents", "distances"]
            )

            search_results = []
            if results and results.get('ids'):
                for i in range(len(results['ids'][0])):
                    metadata = results['metadatas'][0][i] if 'metadatas' in results else {}
                    search_result = SearchResult(
                        id=results['ids'][0][i],
                        content=results['documents'][0][i] if 'documents' in results else "",
                        metadata=metadata,
                        score=metadata.get('priority_score', 0.0),
                        distance=0.0
                    )
                    search_results.append(search_result)

            # Sort by priority score
            return sorted(search_results, key=lambda x: x.score, reverse=True)

        except Exception as e:
            self.logger.error(f"Error searching high-priority questions: {e}")
            raise

    async def search_recent_questions(
        self,
        days_back: int = 30,
        subject: Optional[str] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """
        Search for recently added questions
        """
        try:
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days_back)
            cutoff_year = cutoff_date.year

            filters = {"year": {"$gte": cutoff_year}}
            
            if subject:
                filters["subject"] = subject

            # Use dummy embedding for metadata-based search
            dummy_embedding = [[0.0] * 768]

            results = self.client.query_collection(
                collection_name=QUESTIONS_COLLECTION_NAME,
                query_embeddings=dummy_embedding,
                n_results=limit,
                where=filters,
                include=["metadatas", "documents", "distances"]
            )

            search_results = []
            if results and results.get('ids'):
                for i in range(len(results['ids'][0])):
                    search_result = SearchResult(
                        id=results['ids'][0][i],
                        content=results['documents'][0][i] if 'documents' in results else "",
                        metadata=results['metadatas'][0][i] if 'metadatas' in results else {},
                        score=1.0,
                        distance=0.0
                    )
                    search_results.append(search_result)

            return search_results

        except Exception as e:
            self.logger.error(f"Error searching recent questions: {e}")
            raise

    async def hybrid_search(
        self,
        query_embedding: List[List[float]],
        filters: Optional[Dict[str, Any]] = None,
        boost_recent: bool = True,
        boost_high_priority: bool = True,
        limit: int = 10
    ) -> List[SearchResult]:
        """
        Perform hybrid search combining semantic similarity with metadata-based boosting
        """
        try:
            # Perform semantic search
            semantic_results = await self.semantic_search_questions(
                query_embedding=query_embedding,
                filters=filters,
                limit=limit * 2,  # Get more results for reranking
                score_threshold=0.3
            )

            # Apply boosting
            boosted_results = []
            for result in semantic_results:
                boosted_score = result.score
                
                # Boost high-priority questions
                if boost_high_priority:
                    priority_score = result.metadata.get('priority_score', 0.0)
                    if priority_score > 0.7:
                        boosted_score *= 1.2
                    elif priority_score > 0.5:
                        boosted_score *= 1.1
                
                # Boost recent questions
                if boost_recent:
                    year = result.metadata.get('year', 2020)
                    current_year = datetime.now().year
                    if year >= current_year - 1:
                        boosted_score *= 1.15
                    elif year >= current_year - 2:
                        boosted_score *= 1.05
                
                # Create new result with boosted score
                boosted_result = SearchResult(
                    id=result.id,
                    content=result.content,
                    metadata=result.metadata,
                    score=min(boosted_score, 1.0),  # Cap at 1.0
                    distance=result.distance
                )
                boosted_results.append(boosted_result)

            # Sort by boosted score and return top results
            return sorted(boosted_results, key=lambda x: x.score, reverse=True)[:limit]

        except Exception as e:
            self.logger.error(f"Error in hybrid search: {e}")
            raise

    async def get_question_by_id(self, question_id: str) -> Optional[SearchResult]:
        """
        Get a specific question by its ID
        """
        try:
            result = self.client.get_document_by_id(
                collection_name=QUESTIONS_COLLECTION_NAME,
                doc_id=question_id,
                include=["metadatas", "documents"]
            )

            if result and result.get('ids'):
                return SearchResult(
                    id=result['ids'][0],
                    content=result['documents'][0] if 'documents' in result else "",
                    metadata=result['metadatas'][0] if 'metadatas' in result else {},
                    score=1.0,
                    distance=0.0
                )
            
            return None

        except Exception as e:
            self.logger.error(f"Error getting question by ID: {e}")
            raise

    async def batch_similarity_search(
        self,
        query_embeddings: List[List[float]],
        limit_per_query: int = 5
    ) -> List[List[SearchResult]]:
        """
        Perform similarity search for multiple queries at once
        """
        try:
            results = []
            for embedding in query_embeddings:
                query_results = await self.semantic_search_questions(
                    query_embedding=[embedding],
                    limit=limit_per_query
                )
                results.append(query_results)
            
            return results

        except Exception as e:
            self.logger.error(f"Error in batch similarity search: {e}")
            raise

    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the questions collection
        """
        try:
            total_questions = self.client.count(QUESTIONS_COLLECTION_NAME)
            
            # Get sample data to analyze distribution
            sample_results = self.client.query_collection(
                collection_name=QUESTIONS_COLLECTION_NAME,
                query_embeddings=[[0.0] * 768],
                n_results=min(1000, total_questions),
                include=["metadatas"]
            )

            stats = {
                "total_questions": total_questions,
                "subjects": {},
                "difficulty_distribution": {1: 0, 2: 0, 3: 0, 4: 0},
                "question_types": {},
                "average_priority_score": 0.0
            }

            if sample_results and sample_results.get('metadatas'):
                priority_scores = []
                
                for metadata in sample_results['metadatas'][0]:
                    # Subject distribution
                    subject = metadata.get('subject', 'unknown')
                    stats['subjects'][subject] = stats['subjects'].get(subject, 0) + 1
                    
                    # Difficulty distribution
                    difficulty = metadata.get('difficulty', 1)
                    if difficulty in stats['difficulty_distribution']:
                        stats['difficulty_distribution'][difficulty] += 1
                    
                    # Question type distribution
                    q_type = metadata.get('type', 'unknown')
                    stats['question_types'][q_type] = stats['question_types'].get(q_type, 0) + 1
                    
                    # Priority scores
                    priority = metadata.get('priority_score', 0.0)
                    priority_scores.append(priority)
                
                # Calculate average priority score
                if priority_scores:
                    stats['average_priority_score'] = sum(priority_scores) / len(priority_scores)

            return stats

        except Exception as e:
            self.logger.error(f"Error getting collection stats: {e}")
            raise

    async def update_question_metadata(
        self,
        question_id: str,
        metadata_updates: Dict[str, Any]
    ) -> bool:
        """
        Update metadata for a specific question
        """
        try:
            # Get current metadata
            current_data = self.client.get_document_by_id(
                collection_name=QUESTIONS_COLLECTION_NAME,
                doc_id=question_id,
                include=["metadatas"]
            )

            if not current_data or not current_data.get('metadatas'):
                return False

            # Merge with updates
            current_metadata = current_data['metadatas'][0]
            updated_metadata = {**current_metadata, **metadata_updates}

            # Update in database
            self.client.update_document(
                collection_name=QUESTIONS_COLLECTION_NAME,
                doc_id=question_id,
                metadata=updated_metadata
            )

            return True

        except Exception as e:
            self.logger.error(f"Error updating question metadata: {e}")
            return False

    async def delete_question(self, question_id: str) -> bool:
        """
        Delete a question from the vector database
        """
        try:
            self.client.delete_documents(
                collection_name=QUESTIONS_COLLECTION_NAME,
                ids=[question_id]
            )
            return True

        except Exception as e:
            self.logger.error(f"Error deleting question: {e}")
            return False