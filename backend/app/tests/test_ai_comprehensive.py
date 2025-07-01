import pytest
import asyncio
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from unittest import IsolatedAsyncioTestCase
from typing import List, Dict, Any

# Import our AI modules
from app.ai.processing.text_processor import TextProcessor, TextAnalysisResult, QuestionType, DifficultyLevel
from app.ai.processing.image_processor import ImageProcessor
from app.ai.embeddings.text_embeddings import TextEmbeddingService
from app.ai.llm.gemini_client import GeminiClient
from app.ai.vector_db.client import ChromaDBClient
from app.ai.vector_db.queries import VectorQueries, SearchResult, SemanticSearchQuery
from app.ai.personalization.user_modeling import (
    UserModelingService, UserProfile, QuestionInteraction, LearningStyle, PerformanceLevel
)


class TestTextProcessor:
    @pytest.fixture
    def text_processor(self):
        return TextProcessor(use_advanced_nlp=False)  # Use basic version to avoid dependencies
    
    @pytest.mark.asyncio
    async def test_process_text_basic(self, text_processor):
        """Test basic text processing functionality"""
        text = "What is the derivative of x^2 with respect to x?"
        
        result = await text_processor.process_text(text)
        
        assert isinstance(result, TextAnalysisResult)
        assert result.cleaned_text == text
        assert result.question_type == QuestionType.SHORT_ANSWER
        assert result.word_count > 0
        assert result.sentence_count > 0
        assert len(result.keywords) > 0
    
    def test_clean_text(self, text_processor):
        """Test text cleaning functionality"""
        dirty_text = "  What   is  2+2?   \n\n  "
        clean_text = text_processor.clean_text(dirty_text)
        
        assert clean_text == "What is 2+2?"
    
    def test_detect_question_type_multiple_choice(self, text_processor):
        """Test detection of multiple choice questions"""
        mc_text = "What is 2+2? (a) 3 (b) 4 (c) 5 (d) 6"
        question_type = text_processor.detect_question_type(mc_text)
        
        assert question_type == QuestionType.MULTIPLE_CHOICE
    
    def test_detect_question_type_true_false(self, text_processor):
        """Test detection of true/false questions"""
        tf_text = "True or False: The earth is flat."
        question_type = text_processor.detect_question_type(tf_text)
        
        assert question_type == QuestionType.TRUE_FALSE
    
    def test_extract_mathematical_expressions(self, text_processor):
        """Test extraction of mathematical expressions"""
        math_text = "Calculate $\\sum_{i=1}^{n} i$ and find x where x = 5"
        expressions = text_processor.extract_mathematical_expressions(math_text)
        
        assert len(expressions) > 0
        assert any("\\sum" in expr for expr in expressions)
    
    @pytest.mark.asyncio
    async def test_calculate_difficulty_score(self, text_processor):
        """Test difficulty score calculation"""
        easy_text = "What is 2 + 2?"
        hard_text = "Analyze the implications of quantum superposition in the context of Heisenberg's uncertainty principle and its relationship to wave function collapse."
        
        easy_score = await text_processor.calculate_difficulty_score(easy_text)
        hard_score = await text_processor.calculate_difficulty_score(hard_text)
        
        assert 0 <= easy_score <= 1
        assert 0 <= hard_score <= 1
        assert hard_score > easy_score


class TestImageProcessor:
    @pytest.fixture
    def image_processor(self):
        return ImageProcessor(use_mock=True)  # Use mock to avoid Google Cloud dependencies
    
    @pytest.mark.asyncio
    async def test_ocr_image_from_url_mock(self, image_processor):
        """Test OCR from URL using mock"""
        test_url = "https://example.com/test.jpg"
        result = await image_processor.ocr_image_from_url(test_url)
        
        assert isinstance(result, str)
        assert test_url in result
    
    @pytest.mark.asyncio
    async def test_ocr_image_from_bytes_mock(self, image_processor):
        """Test OCR from bytes using mock"""
        test_bytes = b"fake_image_data"
        result = await image_processor.ocr_image_from_bytes(test_bytes)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_extract_mathematical_content_mock(self, image_processor):
        """Test mathematical content extraction using mock"""
        test_url = "https://example.com/math.jpg"
        result = await image_processor.extract_mathematical_content(test_url)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert "type" in result[0]
        assert "content" in result[0]
        assert "confidence" in result[0]
    
    @pytest.mark.asyncio
    async def test_detect_image_properties_mock(self, image_processor):
        """Test image properties detection using mock"""
        test_url = "https://example.com/test.jpg"
        result = await image_processor.detect_image_properties(test_url)
        
        assert isinstance(result, dict)
        assert "format" in result
        assert "has_text" in result
        assert "has_mathematical_content" in result


class TestTextEmbeddingService:
    @pytest.fixture
    def embedding_service(self):
        # Mock the service since we don't have actual Google Cloud credentials
        return TextEmbeddingService()
    
    @pytest.mark.asyncio
    async def test_get_embeddings_mock(self, embedding_service):
        """Test getting embeddings (mock implementation)"""
        texts = ["Hello world", "Machine learning is awesome"]
        
        embeddings = await embedding_service.get_embeddings(texts)
        
        assert isinstance(embeddings, list)
        assert len(embeddings) == len(texts)
        assert all(isinstance(emb, list) for emb in embeddings)
        assert all(len(emb) > 0 for emb in embeddings)
    
    @pytest.mark.asyncio
    async def test_get_single_embedding_mock(self, embedding_service):
        """Test getting single embedding (mock implementation)"""
        text = "Test question about mathematics"
        
        embedding = await embedding_service.get_single_embedding(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)


class TestGeminiClient:
    @pytest.fixture
    def gemini_client(self):
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel') as mock_model:
                mock_instance = Mock()
                mock_instance.generate_content.return_value.text = "Generated explanation text"
                mock_model.return_value = mock_instance
                
                client = GeminiClient(api_key="test_key")
                return client
    
    @pytest.mark.asyncio
    async def test_generate_text(self, gemini_client):
        """Test text generation"""
        prompt = "Explain photosynthesis"
        
        result = await gemini_client.generate_text(prompt)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_generate_explanation(self, gemini_client):
        """Test explanation generation"""
        question = "What is the derivative of x^2?"
        answer = "2x"
        
        explanation = await gemini_client.generate_explanation(question, answer)
        
        assert isinstance(explanation, str)
        assert len(explanation) > 0
    
    @pytest.mark.asyncio
    async def test_generate_similar_questions(self, gemini_client):
        """Test similar question generation"""
        original_question = "What is 2 + 2?"
        
        with patch.object(gemini_client, 'generate_text', return_value="What is 3 + 3?\nWhat is 4 + 4?\nWhat is 5 + 5?"):
            variations = await gemini_client.generate_similar_questions(original_question, num_variations=3)
            
            assert isinstance(variations, list)
            assert len(variations) <= 3


class TestChromaDBClient:
    @pytest.fixture
    def chroma_client(self):
        return ChromaDBClient(in_memory=True)  # Use in-memory for testing
    
    def test_client_initialization(self, chroma_client):
        """Test ChromaDB client initialization"""
        assert chroma_client.client is not None
        assert chroma_client.questions_collection is not None
        assert chroma_client.user_learning_collection is not None
    
    def test_add_and_query_documents(self, chroma_client):
        """Test adding and querying documents"""
        # Add test documents
        embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        documents = ["Test question 1", "Test question 2"]
        metadatas = [{"subject": "math", "difficulty": 1}, {"subject": "physics", "difficulty": 2}]
        ids = ["q1", "q2"]
        
        chroma_client.add_documents(
            collection_name="questions",
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        # Query documents
        query_embeddings = [[0.1, 0.2, 0.3]]
        results = chroma_client.query_collection(
            collection_name="questions",
            query_embeddings=query_embeddings,
            n_results=2
        )
        
        assert "ids" in results
        assert len(results["ids"][0]) <= 2
    
    def test_get_document_by_id(self, chroma_client):
        """Test getting document by ID"""
        # First add a document
        embeddings = [[0.1, 0.2, 0.3]]
        documents = ["Test question"]
        metadatas = [{"subject": "math"}]
        ids = ["test_id"]
        
        chroma_client.add_documents(
            collection_name="questions",
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        # Get by ID
        result = chroma_client.get_document_by_id("questions", "test_id")
        
        assert "ids" in result
        assert "test_id" in result["ids"]


class TestVectorQueries:
    @pytest.fixture
    def vector_queries(self):
        chroma_client = ChromaDBClient(in_memory=True)
        return VectorQueries(chroma_client)
    
    @pytest.fixture
    def sample_data(self, vector_queries):
        """Setup sample data for testing"""
        # Add sample questions
        embeddings = [
            [0.1, 0.2, 0.3, 0.4, 0.5],
            [0.2, 0.3, 0.4, 0.5, 0.6],
            [0.3, 0.4, 0.5, 0.6, 0.7],
        ]
        documents = [
            "What is calculus?",
            "Explain derivatives",
            "How to integrate functions?"
        ]
        metadatas = [
            {"subject": "mathematics", "difficulty": 2, "type": "short_answer", "priority_score": 0.8},
            {"subject": "mathematics", "difficulty": 3, "type": "short_answer", "priority_score": 0.6},
            {"subject": "mathematics", "difficulty": 3, "type": "essay", "priority_score": 0.9},
        ]
        ids = ["q1", "q2", "q3"]
        
        vector_queries.client.add_documents(
            collection_name="questions",
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    @pytest.mark.asyncio
    async def test_semantic_search_questions(self, vector_queries, sample_data):
        """Test semantic search functionality"""
        query_embedding = [[0.1, 0.2, 0.3, 0.4, 0.5]]
        
        results = await vector_queries.semantic_search_questions(
            query_embedding=query_embedding,
            limit=2
        )
        
        assert isinstance(results, list)
        assert len(results) <= 2
        assert all(isinstance(result, SearchResult) for result in results)
    
    @pytest.mark.asyncio
    async def test_search_by_subject_and_difficulty(self, vector_queries, sample_data):
        """Test subject and difficulty filtering"""
        results = await vector_queries.search_by_subject_and_difficulty(
            subject="mathematics",
            difficulty_range=(2, 3),
            limit=5
        )
        
        assert isinstance(results, list)
        assert all(result.metadata.get("subject") == "mathematics" for result in results)
    
    @pytest.mark.asyncio
    async def test_search_high_priority_questions(self, vector_queries, sample_data):
        """Test high priority question search"""
        results = await vector_queries.search_high_priority_questions(
            priority_threshold=0.7,
            limit=5
        )
        
        assert isinstance(results, list)
        assert all(result.metadata.get("priority_score", 0) >= 0.7 for result in results)
    
    @pytest.mark.asyncio
    async def test_get_collection_stats(self, vector_queries, sample_data):
        """Test collection statistics"""
        stats = await vector_queries.get_collection_stats()
        
        assert isinstance(stats, dict)
        assert "total_questions" in stats
        assert "subjects" in stats
        assert "difficulty_distribution" in stats
        assert stats["total_questions"] > 0


class TestUserModelingService:
    @pytest.fixture
    def user_modeling_service(self):
        return UserModelingService()
    
    @pytest.fixture
    def sample_interactions(self):
        """Create sample user interactions for testing"""
        interactions = []
        base_time = datetime.now() - timedelta(days=30)
        
        for i in range(20):
            interaction = QuestionInteraction(
                question_id=f"q{i}",
                subject="mathematics",
                topic="algebra" if i % 2 == 0 else "calculus",
                difficulty=2 if i % 3 == 0 else 3,
                question_type="multiple_choice" if i % 2 == 0 else "short_answer",
                is_correct=i % 3 != 0,  # 2/3 correct
                time_taken=60 + (i * 10),
                attempts=1 if i % 4 != 0 else 2,
                hint_used=i % 5 == 0,
                timestamp=base_time + timedelta(days=i),
                confidence_level=0.7 + (i % 3) * 0.1
            )
            interactions.append(interaction)
        
        return interactions
    
    @pytest.mark.asyncio
    async def test_build_user_profile(self, user_modeling_service, sample_interactions):
        """Test user profile building"""
        profile = await user_modeling_service.build_user_profile(
            user_id="test_user",
            interactions=sample_interactions,
            initial_preferences={
                "academic_level": "undergraduate",
                "subjects": ["mathematics"],
                "learning_style": "mixed",
                "study_goals": ["exam_prep"]
            }
        )
        
        assert isinstance(profile, UserProfile)
        assert profile.user_id == "test_user"
        assert profile.academic_level == "undergraduate"
        assert len(profile.performance_levels) > 0
        assert profile.preferred_difficulty in [1, 2, 3, 4]
    
    @pytest.mark.asyncio
    async def test_predict_performance(self, user_modeling_service, sample_interactions):
        """Test performance prediction"""
        profile = await user_modeling_service.build_user_profile(
            user_id="test_user",
            interactions=sample_interactions
        )
        
        question_metadata = {
            "subject": "mathematics",
            "topic": "algebra",
            "difficulty": 2,
            "type": "multiple_choice"
        }
        
        prediction = await user_modeling_service.predict_performance(profile, question_metadata)
        
        assert isinstance(prediction, dict)
        assert "success_probability" in prediction
        assert "estimated_time" in prediction
        assert "difficulty_match" in prediction
        assert "confidence" in prediction
        assert 0 <= prediction["success_probability"] <= 1
    
    @pytest.mark.asyncio
    async def test_generate_learning_insights(self, user_modeling_service, sample_interactions):
        """Test learning insights generation"""
        profile = await user_modeling_service.build_user_profile(
            user_id="test_user",
            interactions=sample_interactions
        )
        
        insights = await user_modeling_service.generate_learning_insights(profile, sample_interactions)
        
        assert isinstance(insights, dict)
        assert "progress_summary" in insights
        assert "recommendations" in insights
        assert "learning_patterns" in insights
        assert "performance_trends" in insights
        assert "study_habits" in insights
    
    def test_group_interactions_by_session(self, user_modeling_service):
        """Test session grouping logic"""
        # Create interactions with time gaps
        base_time = datetime.now()
        interactions = [
            QuestionInteraction(
                question_id="q1", subject="math", topic="algebra", difficulty=2,
                question_type="mc", is_correct=True, time_taken=60, attempts=1,
                hint_used=False, timestamp=base_time
            ),
            QuestionInteraction(
                question_id="q2", subject="math", topic="algebra", difficulty=2,
                question_type="mc", is_correct=True, time_taken=60, attempts=1,
                hint_used=False, timestamp=base_time + timedelta(minutes=5)
            ),
            QuestionInteraction(
                question_id="q3", subject="math", topic="algebra", difficulty=2,
                question_type="mc", is_correct=True, time_taken=60, attempts=1,
                hint_used=False, timestamp=base_time + timedelta(hours=2)  # New session
            ),
        ]
        
        sessions = user_modeling_service._group_interactions_by_session(interactions)
        
        assert len(sessions) == 2
        assert len(sessions[0]) == 2
        assert len(sessions[1]) == 1


class TestAIIntegration:
    """Integration tests for AI components working together"""
    
    @pytest.mark.asyncio
    async def test_question_processing_pipeline(self):
        """Test the complete question processing pipeline"""
        # Initialize components
        text_processor = TextProcessor(use_advanced_nlp=False)
        image_processor = ImageProcessor(use_mock=True)
        chroma_client = ChromaDBClient(in_memory=True)
        
        # Process a question
        question_text = "What is the derivative of x^2 + 3x with respect to x?"
        
        # Text analysis
        text_analysis = await text_processor.process_text(question_text)
        assert text_analysis.question_type == QuestionType.SHORT_ANSWER
        assert len(text_analysis.mathematical_expressions) > 0
        
        # Mock embedding (in real scenario, this would come from TextEmbeddingService)
        mock_embedding = [0.1] * 768
        
        # Store in vector database
        chroma_client.add_documents(
            collection_name="questions",
            embeddings=[mock_embedding],
            documents=[question_text],
            metadatas=[{
                "subject": "mathematics",
                "difficulty": text_analysis.difficulty_score * 4 + 1,  # Scale to 1-4
                "type": text_analysis.question_type.value,
                "keywords": text_analysis.keywords[:5]
            }],
            ids=["test_question_1"]
        )
        
        # Query the database
        vector_queries = VectorQueries(chroma_client)
        results = await vector_queries.semantic_search_questions(
            query_embedding=[mock_embedding],
            limit=1
        )
        
        assert len(results) == 1
        assert results[0].content == question_text
    
    @pytest.mark.asyncio
    async def test_personalized_recommendation_pipeline(self):
        """Test personalized recommendation pipeline"""
        # Setup components
        user_modeling = UserModelingService()
        chroma_client = ChromaDBClient(in_memory=True)
        vector_queries = VectorQueries(chroma_client)
        
        # Add sample questions to database
        sample_questions = [
            {
                "id": "q1",
                "text": "What is calculus?",
                "embedding": [0.1] * 5,
                "metadata": {"subject": "mathematics", "difficulty": 1, "type": "short_answer", "topic": "calculus"}
            },
            {
                "id": "q2", 
                "text": "Solve for x: 2x + 5 = 11",
                "embedding": [0.2] * 5,
                "metadata": {"subject": "mathematics", "difficulty": 2, "type": "numerical", "topic": "algebra"}
            },
            {
                "id": "q3",
                "text": "Explain quantum mechanics",
                "embedding": [0.3] * 5,
                "metadata": {"subject": "physics", "difficulty": 4, "type": "essay", "topic": "quantum"}
            }
        ]
        
        # Add to vector database
        for q in sample_questions:
            chroma_client.add_documents(
                collection_name="questions",
                embeddings=[q["embedding"]],
                documents=[q["text"]],
                metadatas=[q["metadata"]],
                ids=[q["id"]]
            )
        
        # Create user interactions
        interactions = [
            QuestionInteraction(
                question_id="q1", subject="mathematics", topic="calculus", difficulty=1,
                question_type="short_answer", is_correct=True, time_taken=120, attempts=1,
                hint_used=False, timestamp=datetime.now() - timedelta(days=1)
            ),
            QuestionInteraction(
                question_id="q2", subject="mathematics", topic="algebra", difficulty=2,
                question_type="numerical", is_correct=False, time_taken=300, attempts=3,
                hint_used=True, timestamp=datetime.now()
            )
        ]
        
        # Build user profile
        profile = await user_modeling.build_user_profile(
            user_id="test_user",
            interactions=interactions
        )
        
        # Test recommendation logic
        assert profile.user_id == "test_user"
        assert "mathematics" in profile.performance_levels
        
        # Predict performance on new question
        prediction = await user_modeling.predict_performance(
            profile, 
            sample_questions[2]["metadata"]  # Physics question
        )
        
        assert "success_probability" in prediction
        assert 0 <= prediction["success_probability"] <= 1


class TestErrorHandling:
    """Test error handling in AI components"""
    
    @pytest.mark.asyncio
    async def test_text_processor_empty_input(self):
        """Test text processor with empty input"""
        processor = TextProcessor(use_advanced_nlp=False)
        
        result = await processor.process_text("")
        assert result.cleaned_text == ""
        assert result.word_count == 0
    
    @pytest.mark.asyncio
    async def test_image_processor_invalid_url(self):
        """Test image processor with invalid URL"""
        processor = ImageProcessor(use_mock=True)  # Mock mode should handle gracefully
        
        # Should not raise exception in mock mode
        result = await processor.ocr_image_from_url("invalid_url")
        assert isinstance(result, str)
    
    def test_chroma_client_invalid_collection(self):
        """Test ChromaDB client with invalid collection name"""
        client = ChromaDBClient(in_memory=True)
        
        with pytest.raises(ValueError):
            client.add_documents(
                collection_name="invalid_collection",
                embeddings=[[0.1, 0.2]],
                ids=["test"]
            )
    
    @pytest.mark.asyncio
    async def test_user_modeling_insufficient_data(self):
        """Test user modeling with insufficient interaction data"""
        service = UserModelingService()
        
        # Only 2 interactions, below minimum threshold
        interactions = [
            QuestionInteraction(
                question_id="q1", subject="math", topic="algebra", difficulty=2,
                question_type="mc", is_correct=True, time_taken=60, attempts=1,
                hint_used=False, timestamp=datetime.now()
            ),
            QuestionInteraction(
                question_id="q2", subject="math", topic="algebra", difficulty=2,
                question_type="mc", is_correct=False, time_taken=120, attempts=2,
                hint_used=True, timestamp=datetime.now()
            )
        ]
        
        profile = await service.build_user_profile("test_user", interactions)
        
        # Should still create profile with defaults
        assert profile.user_id == "test_user"
        assert profile.learning_style == LearningStyle.MIXED


class TestDifficultyAdapter(IsolatedAsyncioTestCase):
    """Test cases for DifficultyAdapter"""
    
    def setUp(self):
        from app.ai.personalization.difficulty_adapter import DifficultyAdapter, AdaptationStrategy
        self.difficulty_adapter = DifficultyAdapter(AdaptationStrategy.MODERATE)
    
    async def test_adapt_difficulty_increase(self):
        """Test difficulty adaptation - increase scenario"""
        from app.ai.personalization.user_modeling import UserProfile, QuestionInteraction, PerformanceLevel
        from datetime import datetime, timedelta
        
        user_profile = UserProfile(
            user_id="user_001",
            academic_level="undergraduate", 
            performance_level=PerformanceLevel.INTERMEDIATE,
            learning_style="visual",
            preferred_difficulty=2,
            strong_subjects=["physics"],
            weak_subjects=[],
            study_preferences={},
            recent_interactions=[]
        )
        
        # Create interactions showing high performance
        recent_interactions = []
        for i in range(10):
            interaction = QuestionInteraction(
                question_id=f"q_{i}",
                subject="physics",
                difficulty=2,
                is_correct=True,  # High accuracy
                time_taken=60,    # Fast completion
                attempts=1,       # First attempt
                timestamp=datetime.now() - timedelta(hours=i),
                metadata={}
            )
            recent_interactions.append(interaction)
        
        adjustment = await self.difficulty_adapter.adapt_difficulty(
            user_profile, recent_interactions, "physics"
        )
        
        if adjustment:  # Adjustment might not happen if confidence is low
            self.assertEqual(adjustment.old_difficulty, 2)
            self.assertGreater(adjustment.new_difficulty, 2)
            self.assertIsInstance(adjustment.reasoning, list)
            self.assertGreater(len(adjustment.reasoning), 0)
    
    async def test_adapt_difficulty_decrease(self):
        """Test difficulty adaptation - decrease scenario"""
        from app.ai.personalization.user_modeling import UserProfile, QuestionInteraction, PerformanceLevel
        from datetime import datetime, timedelta
        
        user_profile = UserProfile(
            user_id="user_001",
            academic_level="undergraduate",
            performance_level=PerformanceLevel.BEGINNER,
            learning_style="visual", 
            preferred_difficulty=3,
            strong_subjects=[],
            weak_subjects=["physics"],
            study_preferences={},
            recent_interactions=[]
        )
        
        # Create interactions showing poor performance
        recent_interactions = []
        for i in range(10):
            interaction = QuestionInteraction(
                question_id=f"q_{i}",
                subject="physics",
                difficulty=3,
                is_correct=False,  # Low accuracy
                time_taken=300,    # Slow completion
                attempts=3,        # Multiple attempts
                timestamp=datetime.now() - timedelta(hours=i),
                metadata={}
            )
            recent_interactions.append(interaction)
        
        adjustment = await self.difficulty_adapter.adapt_difficulty(
            user_profile, recent_interactions, "physics"
        )
        
        if adjustment:  # Adjustment might not happen if confidence is low
            self.assertEqual(adjustment.old_difficulty, 3)
            self.assertLess(adjustment.new_difficulty, 3)
    
    async def test_predict_performance_at_difficulty(self):
        """Test performance prediction at different difficulty levels"""
        from app.ai.personalization.user_modeling import UserProfile, QuestionInteraction, PerformanceLevel
        from datetime import datetime, timedelta
        
        user_profile = UserProfile(
            user_id="user_001",
            academic_level="undergraduate",
            performance_level=PerformanceLevel.INTERMEDIATE,
            learning_style="visual",
            preferred_difficulty=2,
            strong_subjects=["physics"],
            weak_subjects=[],
            study_preferences={},
            recent_interactions=[]
        )
        
        # Create diverse interactions
        recent_interactions = []
        difficulties = [1, 2, 3]
        for diff in difficulties:
            for i in range(5):
                interaction = QuestionInteraction(
                    question_id=f"q_{diff}_{i}",
                    subject="physics",
                    difficulty=diff,
                    is_correct=i < 4,  # 80% accuracy for easier, less for harder
                    time_taken=60 * diff,  # More time for harder questions
                    attempts=1,
                    timestamp=datetime.now() - timedelta(hours=i),
                    metadata={}
                )
                recent_interactions.append(interaction)
        
        prediction = await self.difficulty_adapter.predict_performance_at_difficulty(
            user_profile, 4, recent_interactions, "physics"
        )
        
        self.assertIsInstance(prediction, dict)
        self.assertIn('predicted_accuracy', prediction)
        self.assertIn('predicted_time', prediction)
        self.assertIn('confidence', prediction)
        
        # Predicted accuracy should be reasonable
        self.assertGreater(prediction['predicted_accuracy'], 0.0)
        self.assertLess(prediction['predicted_accuracy'], 1.0)


class TestLearningPathGenerator(IsolatedAsyncioTestCase):
    """Test cases for LearningPathGenerator"""
    
    def setUp(self):
        from app.ai.personalization.learning_path import LearningPathGenerator, Topic
        from app.ai.personalization.difficulty_adapter import DifficultyAdapter
        
        self.path_generator = LearningPathGenerator(DifficultyAdapter())
        
        # Create sample topics
        self.sample_topics = [
            Topic(id="topic_1", name="Introduction", subject="physics", difficulty_level=1),
            Topic(id="topic_2", name="Mechanics", subject="physics", difficulty_level=2, prerequisites=["topic_1"]),
            Topic(id="topic_3", name="Thermodynamics", subject="physics", difficulty_level=3, prerequisites=["topic_2"]),
        ]
    
    async def test_generate_personalized_path_sequential(self):
        """Test generating a sequential learning path"""
        from app.ai.personalization.user_modeling import UserProfile, PerformanceLevel
        from app.ai.personalization.learning_path import PathType, LearningObjective
        
        user_profile = UserProfile(
            user_id="user_001",
            academic_level="undergraduate",
            performance_level=PerformanceLevel.BEGINNER,
            learning_style="visual",
            preferred_difficulty=1,
            strong_subjects=[],
            weak_subjects=["physics"],
            study_preferences={"daily_minutes": 30, "session_duration": "medium"},
            recent_interactions=[]
        )
        
        path = await self.path_generator.generate_personalized_path(
            user_profile=user_profile,
            subject="physics",
            objectives=[LearningObjective.MASTERY],
            path_type=PathType.SEQUENTIAL,
            available_topics=self.sample_topics
        )
        
        self.assertIsNotNone(path)
        self.assertEqual(path.user_id, "user_001")
        self.assertEqual(path.subject, "physics")
        self.assertEqual(path.path_type, PathType.SEQUENTIAL)
        self.assertGreater(len(path.sessions), 0)
        self.assertGreater(path.total_duration, 0)
    
    async def test_generate_weakness_focused_path(self):
        """Test generating a weakness-focused learning path"""
        from app.ai.personalization.user_modeling import UserProfile, QuestionInteraction, PerformanceLevel
        from app.ai.personalization.learning_path import PathType, LearningObjective
        from datetime import datetime
        
        # Create interactions showing weakness in specific topics
        interactions = [
            QuestionInteraction(
                question_id="q1",
                subject="physics", 
                difficulty=2,
                is_correct=False,
                time_taken=180,
                attempts=2,
                timestamp=datetime.now(),
                metadata={"topic_id": "topic_2"}
            )
            for _ in range(5)
        ]
        
        user_profile = UserProfile(
            user_id="user_001",
            academic_level="undergraduate",
            performance_level=PerformanceLevel.INTERMEDIATE,
            learning_style="visual",
            preferred_difficulty=2,
            strong_subjects=[],
            weak_subjects=["physics"],
            study_preferences={"daily_minutes": 45},
            recent_interactions=interactions
        )
        
        path = await self.path_generator.generate_personalized_path(
            user_profile=user_profile,
            subject="physics",
            objectives=[LearningObjective.MASTERY],
            path_type=PathType.WEAKNESS_FOCUSED,
            available_topics=self.sample_topics
        )
        
        self.assertIsNotNone(path)
        self.assertEqual(path.path_type, PathType.WEAKNESS_FOCUSED)
        
        # Should focus on weak areas
        for session in path.sessions:
            self.assertEqual(session.session_type, "weakness_focused")
    
    async def test_update_path_progress(self):
        """Test updating learning path progress"""
        from app.ai.personalization.user_modeling import UserProfile, PerformanceLevel
        from app.ai.personalization.learning_path import PathType, LearningObjective
        from datetime import datetime
        
        user_profile = UserProfile(
            user_id="user_001",
            academic_level="undergraduate",
            performance_level=PerformanceLevel.INTERMEDIATE,
            learning_style="visual",
            preferred_difficulty=2,
            strong_subjects=[],
            weak_subjects=[],
            study_preferences={},
            recent_interactions=[]
        )
        
        path = await self.path_generator.generate_personalized_path(
            user_profile=user_profile,
            subject="physics",
            objectives=[LearningObjective.COVERAGE],
            path_type=PathType.SEQUENTIAL,
            available_topics=self.sample_topics
        )
        
        # Simulate completing first session
        session_results = {
            "accuracy": 0.8,
            "average_time": 120,
            "time_spent": 30,
            "questions_completed": 10
        }
        
        updated_path = await self.path_generator.update_path_progress(
            path, 0, session_results
        )
        
        self.assertEqual(updated_path.current_session, 1)
        self.assertGreater(updated_path.progress, 0)
        self.assertIn('session_results', updated_path.metadata)
    
    async def test_get_next_study_session(self):
        """Test getting next study session"""
        from app.ai.personalization.user_modeling import UserProfile, PerformanceLevel
        from app.ai.personalization.learning_path import PathType, LearningObjective
        
        user_profile = UserProfile(
            user_id="user_001", 
            academic_level="undergraduate",
            performance_level=PerformanceLevel.INTERMEDIATE,
            learning_style="visual",
            preferred_difficulty=2,
            strong_subjects=[],
            weak_subjects=[],
            study_preferences={},
            recent_interactions=[]
        )
        
        path = await self.path_generator.generate_personalized_path(
            user_profile=user_profile,
            subject="physics",
            objectives=[LearningObjective.COVERAGE],
            path_type=PathType.SEQUENTIAL,
            available_topics=self.sample_topics
        )
        
        next_session = await self.path_generator.get_next_study_session(path)
        
        self.assertIsNotNone(next_session)
        self.assertGreater(len(next_session.steps), 0)
        self.assertGreater(next_session.total_duration, 0)
    
    async def test_adjust_session_for_time(self):
        """Test adjusting session for limited time"""
        from app.ai.personalization.user_modeling import UserProfile, PerformanceLevel
        from app.ai.personalization.learning_path import PathType, LearningObjective
        
        user_profile = UserProfile(
            user_id="user_001",
            academic_level="undergraduate", 
            performance_level=PerformanceLevel.INTERMEDIATE,
            learning_style="visual",
            preferred_difficulty=2,
            strong_subjects=[],
            weak_subjects=[],
            study_preferences={},
            recent_interactions=[]
        )
        
        path = await self.path_generator.generate_personalized_path(
            user_profile=user_profile,
            subject="physics", 
            objectives=[LearningObjective.COVERAGE],
            path_type=PathType.SEQUENTIAL,
            available_topics=self.sample_topics
        )
        
        # Get session with time constraint
        available_time = 15  # Only 15 minutes available
        next_session = await self.path_generator.get_next_study_session(
            path, available_time
        )
        
        if next_session:
            self.assertLessEqual(next_session.total_duration, available_time)
    
    def test_get_path_analytics(self):
        """Test getting path analytics"""
        from app.ai.personalization.user_modeling import UserProfile, PerformanceLevel
        from app.ai.personalization.learning_path import LearningPath, PathType, LearningObjective, StudySession, LearningStep
        from datetime import datetime
        
        # Create a path with some completed sessions
        path = LearningPath(
            id="test_path",
            user_id="user_001", 
            subject="physics",
            path_type=PathType.SEQUENTIAL,
            objectives=[LearningObjective.MASTERY],
            sessions=[
                StudySession(
                    steps=[LearningStep("topic_1", "Topic 1", 1, 30, 5, "practice")],
                    total_duration=30,
                    session_type="sequential",
                    focus_areas=["topic_1"],
                    difficulty_range=(1, 1),
                    objectives=[LearningObjective.MASTERY]
                )
            ],
            total_duration=30,
            estimated_completion=datetime.now(),
            created_at=datetime.now(),
            progress=0.5,
            current_session=1,
            metadata={
                'session_results': {
                    '0': {
                        'completed_at': datetime.now().isoformat(),
                        'results': {'accuracy': 0.8, 'time_spent': 25}
                    }
                }
            }
        )
        
        analytics = self.path_generator.get_path_analytics(path)
        
        self.assertIsInstance(analytics, dict)
        self.assertIn('completion_rate', analytics)
        self.assertIn('average_accuracy', analytics)
        self.assertIn('total_study_time', analytics)
        self.assertIn('recommendations', analytics)
        
        self.assertEqual(analytics['completion_rate'], 0.5)
        self.assertEqual(analytics['average_accuracy'], 0.8)


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
