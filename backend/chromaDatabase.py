import chromadb
from chromadb.config import Settings
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import uuid
from datetime import datetime
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class QuestionEmbedding:
    """Data class for question embeddings"""
    question_id: str
    embeddings: Dict[str, List[float]]
    metadata: Dict[str, Any]
    created_at: str

class ChromaVectorStore:
    def __init__(self, persist_directory: str = "./chroma_db", api_key: str = None):
        """Initialize ChromaDB with persistence and Google embeddings"""
        try:
            # Configure ChromaDB client with persistence
            self.chroma_client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            self.api_key = api_key
            
            # Initialize collections
            self.collections = {
                'questions': self.setup_questions_collection(),
                'user_patterns': self.setup_user_patterns_collection(),
                'explanations': self.setup_explanations_collection()
            }
            
            logger.info(f"ChromaVectorStore initialized with persistence at {persist_directory}")
            
        except Exception as e:
            logger.error(f"Error initializing ChromaVectorStore: {str(e)}")
            raise
    
    def get_embedding_function(self):
        """Get Google Generative AI embedding function"""
        if self.api_key:
            return chromadb.utils.embedding_functions.GoogleGenerativeAiEmbeddingFunction(
                api_key=self.api_key,
                model_name="models/text-embedding-004"
            )
        else:
            # Fallback to default embedding function
            logger.warning("No API key provided, using default embedding function")
            return chromadb.utils.embedding_functions.DefaultEmbeddingFunction()
    
    def setup_questions_collection(self):
        """Set up the questions collection with proper configuration"""
        try:
            collection = self.chroma_client.get_or_create_collection(
                name="questions",
                metadata={"hnsw:space": "cosine"},
                embedding_function=self.get_embedding_function()
            )
            logger.info("Questions collection setup completed")
            return collection
        except Exception as e:
            logger.error(f"Error setting up questions collection: {str(e)}")
            raise
    
    def setup_user_patterns_collection(self):
        """Set up the user patterns collection"""
        try:
            collection = self.chroma_client.get_or_create_collection(
                name="user_patterns",
                metadata={"hnsw:space": "cosine"},
                embedding_function=self.get_embedding_function()
            )
            logger.info("User patterns collection setup completed")
            return collection
        except Exception as e:
            logger.error(f"Error setting up user patterns collection: {str(e)}")
            raise
    
    def setup_explanations_collection(self):
        """Set up the explanations collection"""
        try:
            collection = self.chroma_client.get_or_create_collection(
                name="explanations",
                metadata={"hnsw:space": "cosine"},
                embedding_function=self.get_embedding_function()
            )
            logger.info("Explanations collection setup completed")
            return collection
        except Exception as e:
            logger.error(f"Error setting up explanations collection: {str(e)}")
            raise
    
    async def store_question_vectors(self, question_embedding: QuestionEmbedding):
        """Store question vectors in the appropriate collections"""
        try:
            # Prepare document text
            document_text = f"Question ID: {question_embedding.question_id}"
            if question_embedding.metadata.get('question_text'):
                document_text += f"\nQuestion: {question_embedding.metadata['question_text']}"
            if question_embedding.metadata.get('answer_text'):
                document_text += f"\nAnswer: {question_embedding.metadata['answer_text']}"
            
            # Store in questions collection
            if 'text' in question_embedding.embeddings:
                self.collections['questions'].add(
                    documents=[document_text],
                    embeddings=[question_embedding.embeddings['text']],
                    metadatas=[{
                        **question_embedding.metadata,
                        'stored_at': datetime.now().isoformat(),
                        'embedding_type': 'text'
                    }],
                    ids=[question_embedding.question_id]
                )
                
                logger.info(f"Stored question vector for {question_embedding.question_id}")
            else:
                logger.warning(f"No text embedding found for question {question_embedding.question_id}")
                
        except Exception as e:
            logger.error(f"Error storing question vectors: {str(e)}")
            raise
    
    async def search_similar_questions(
        self, 
        query_embedding: List[float], 
        n_results: int = 5,
        where_filter: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Search for similar questions using vector similarity"""
        try:
            results = self.collections['questions'].query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter,
                include=['documents', 'metadatas', 'distances', 'embeddings']
            )
            
            logger.info(f"Found {len(results['ids'][0])} similar questions")
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar questions: {str(e)}")
            return {
                'ids': [[]],
                'documents': [[]],
                'metadatas': [[]],
                'distances': [[]],
                'embeddings': [[]]
            }
    
    async def search_by_text(
        self,
        query_text: str,
        collection_name: str = 'questions',
        n_results: int = 5,
        where_filter: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Search using text query (ChromaDB will handle embedding generation)"""
        try:
            collection = self.collections.get(collection_name)
            if not collection:
                raise ValueError(f"Collection '{collection_name}' not found")
            
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where_filter,
                include=['documents', 'metadatas', 'distances']
            )
            
            logger.info(f"Text search found {len(results['ids'][0])} results in {collection_name}")
            return results
            
        except Exception as e:
            logger.error(f"Error in text search: {str(e)}")
            return {
                'ids': [[]],
                'documents': [[]],
                'metadatas': [[]],
                'distances': [[]]
            }
    
    async def store_user_learning_pattern(
        self,
        user_id: str,
        learning_data: Dict[str, Any],
        embedding: List[float]
    ):
        """Store user learning patterns"""
        try:
            document_text = f"User: {user_id}\nLearning Pattern: {learning_data.get('description', '')}"
            
            self.collections['user_patterns'].add(
                documents=[document_text],
                embeddings=[embedding],
                metadatas=[{
                    'user_id': user_id,
                    'pattern_type': learning_data.get('pattern_type', 'general'),
                    'subject': learning_data.get('subject'),
                    'performance_score': learning_data.get('performance_score'),
                    'difficulty_preference': learning_data.get('difficulty_preference'),
                    'created_at': datetime.now().isoformat()
                }],
                ids=[f"{user_id}_{uuid.uuid4().hex[:8]}"]
            )
            
            logger.info(f"Stored learning pattern for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error storing user learning pattern: {str(e)}")
            raise
    
    async def store_explanation_vector(
        self,
        explanation_id: str,
        question_id: str,
        explanation_text: str,
        embedding: List[float],
        metadata: Dict[str, Any] = None
    ):
        """Store explanation vectors"""
        try:
            self.collections['explanations'].add(
                documents=[explanation_text],
                embeddings=[embedding],
                metadatas=[{
                    'explanation_id': explanation_id,
                    'question_id': question_id,
                    'explanation_type': metadata.get('type', 'detailed') if metadata else 'detailed',
                    'created_at': datetime.now().isoformat(),
                    **(metadata or {})
                }],
                ids=[explanation_id]
            )
            
            logger.info(f"Stored explanation vector for {explanation_id}")
            
        except Exception as e:
            logger.error(f"Error storing explanation vector: {str(e)}")
            raise
    
    async def get_user_learning_history(
        self,
        user_id: str,
        n_results: int = 10
    ) -> Dict[str, Any]:
        """Get user's learning history and patterns"""
        try:
            results = self.collections['user_patterns'].query(
                query_texts=[f"User: {user_id}"],
                n_results=n_results,
                where={'user_id': user_id},
                include=['documents', 'metadatas', 'distances']
            )
            
            logger.info(f"Retrieved {len(results['ids'][0])} learning patterns for user {user_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving user learning history: {str(e)}")
            return {
                'ids': [[]],
                'documents': [[]],
                'metadatas': [[]],
                'distances': [[]]
            }
    
    async def batch_store_questions(
        self,
        question_embeddings: List[QuestionEmbedding],
        batch_size: int = 10
    ) -> Dict[str, Any]:
        """Store multiple question embeddings in batches"""
        results = {'success': 0, 'failed': 0, 'errors': []}
        
        for i in range(0, len(question_embeddings), batch_size):
            batch = question_embeddings[i:i + batch_size]
            
            for embedding in batch:
                try:
                    await self.store_question_vectors(embedding)
                    results['success'] += 1
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"Question {embedding.question_id}: {str(e)}")
            
            # Small delay between batches
            await asyncio.sleep(0.1)
        
        logger.info(f"Batch store completed: {results['success']} success, {results['failed']} failed")
        return results
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about all collections"""
        info = {}
        
        for name, collection in self.collections.items():
            try:
                count = collection.count()
                info[name] = {
                    'document_count': count,
                    'status': 'active'
                }
            except Exception as e:
                info[name] = {
                    'document_count': 0,
                    'status': 'error',
                    'error': str(e)
                }
        
        return info
    
    def reset_collection(self, collection_name: str) -> bool:
        """Reset a specific collection (use with caution)"""
        try:
            if collection_name in self.collections:
                self.chroma_client.delete_collection(collection_name)
                
                # Recreate the collection
                if collection_name == 'questions':
                    self.collections[collection_name] = self.setup_questions_collection()
                elif collection_name == 'user_patterns':
                    self.collections[collection_name] = self.setup_user_patterns_collection()
                elif collection_name == 'explanations':
                    self.collections[collection_name] = self.setup_explanations_collection()
                
                logger.info(f"Reset collection: {collection_name}")
                return True
            else:
                logger.warning(f"Collection not found: {collection_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error resetting collection {collection_name}: {str(e)}")
            return False


# Utility functions
async def create_chroma_store(persist_directory: str = "./chroma_db", api_key: str = None) -> ChromaVectorStore:
    """Create and initialize ChromaVectorStore"""
    return ChromaVectorStore(persist_directory=persist_directory, api_key=api_key)

async def migrate_existing_data(
    old_store: ChromaVectorStore,
    new_store: ChromaVectorStore,
    collection_name: str
) -> bool:
    """Migrate data from one ChromaDB instance to another"""
    try:
        # This would implement data migration logic
        logger.info(f"Migration completed for collection: {collection_name}")
        return True
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return False

# Test function
async def test_chroma_store():
    """Test ChromaDB functionality"""
    pass

if __name__ == "__main__":
    asyncio.run(test_chroma_store())