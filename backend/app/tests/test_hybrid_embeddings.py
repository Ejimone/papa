import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any

from app.ai.embeddings.hybrid_embeddings import HybridEmbeddingService

class TestHybridEmbeddingService:
    """Test suite for HybridEmbeddingService."""
    
    @pytest.fixture
    def mock_text_service(self):
        """Mock text embedding service."""
        mock_service = Mock()
        mock_service.get_single_embedding = AsyncMock(return_value=[0.1] * 768)
        return mock_service
    
    @pytest.fixture
    def mock_image_service(self):
        """Mock image embedding service."""
        mock_service = Mock()
        mock_service.generate_image_description_embedding = AsyncMock(return_value=[0.2] * 768)
        return mock_service
    
    @pytest.fixture
    def service(self, mock_text_service, mock_image_service):
        """Create a test service instance."""
        return HybridEmbeddingService(
            text_service=mock_text_service,
            image_service=mock_image_service,
            fusion_method="concatenation"
        )
    
    @pytest.fixture
    def sample_metadata(self):
        """Create sample metadata for testing."""
        return {
            'keywords': ['math', 'algebra'],
            'concepts': ['linear equations', 'variables'],
            'subject': 'Mathematics',
            'topic': 'Algebra',
            'ocr_text': 'x + y = 5'
        }
    
    def test_init_default(self):
        """Test default initialization."""
        with patch('app.ai.embeddings.hybrid_embeddings.TextEmbeddingService'), \
             patch('app.ai.embeddings.hybrid_embeddings.ImageEmbeddingService'):
            
            service = HybridEmbeddingService()
            assert service.fusion_method == "concatenation"
            assert service.text_weight == 0.7
            assert service.image_weight == 0.3
            assert service.text_dim == 768
            assert service.image_dim == 768
            assert service.hybrid_dim == 1536  # concatenation doubles the dimension
    
    def test_init_weighted_average(self):
        """Test initialization with weighted average fusion."""
        with patch('app.ai.embeddings.hybrid_embeddings.TextEmbeddingService'), \
             patch('app.ai.embeddings.hybrid_embeddings.ImageEmbeddingService'):
            
            service = HybridEmbeddingService(fusion_method="weighted_average")
            assert service.fusion_method == "weighted_average"
            assert service.hybrid_dim == 768  # same as max of text/image dims
    
    @pytest.mark.asyncio
    async def test_create_question_embedding_text_only(self, service, sample_metadata):
        """Test creating embedding for text-only question."""
        result = await service.create_question_embedding(
            question_text="What is 2 + 2?",
            question_images=None,
            question_metadata=sample_metadata
        )
        
        assert result['success'] is True
        assert len(result['hybrid_embedding']) == 1536  # concatenation
        assert len(result['text_embedding']) == 768
        assert len(result['image_embedding']) == 768
        assert result['fusion_method'] == "concatenation"
        assert result['text_weight'] == 0.7
        assert result['image_weight'] == 0.3
    
    @pytest.mark.asyncio
    async def test_create_question_embedding_with_images(self, service, sample_metadata):
        """Test creating embedding for question with images."""
        image_data = [b"fake_image_data_1", b"fake_image_data_2"]
        
        result = await service.create_question_embedding(
            question_text="Analyze this diagram",
            question_images=image_data,
            question_metadata=sample_metadata
        )
        
        assert result['success'] is True
        assert len(result['hybrid_embedding']) == 1536
        
        # Verify image service was called for each image
        assert service.image_service.generate_image_description_embedding.call_count == 2
    
    @pytest.mark.asyncio
    async def test_create_question_embedding_error(self, service):
        """Test embedding creation with error."""
        service.text_service.get_single_embedding.side_effect = Exception("API Error")
        
        result = await service.create_question_embedding(
            question_text="What is 2 + 2?",
            question_images=None,
            question_metadata=None
        )
        
        assert result['success'] is False
        assert 'error' in result
        assert all(x == 0.0 for x in result['hybrid_embedding'])
    
    def test_prepare_text_for_embedding_complete(self, service, sample_metadata):
        """Test text preparation with complete metadata."""
        text = service._prepare_text_for_embedding("What is x?", sample_metadata)
        
        expected_components = [
            "What is x?",
            "Keywords: math algebra",
            "Concepts: linear equations variables", 
            "Subject: Mathematics",
            "Topic: Algebra",
            "Image text: x + y = 5"
        ]
        
        for component in expected_components:
            assert component in text
    
    def test_prepare_text_for_embedding_no_metadata(self, service):
        """Test text preparation without metadata."""
        text = service._prepare_text_for_embedding("What is x?", None)
        assert text == "What is x?"
    
    def test_concatenation_fusion(self, service):
        """Test concatenation fusion method."""
        text_embedding = [0.1, 0.2, 0.3]
        image_embedding = [0.4, 0.5, 0.6]
        
        result = service._concatenation_fusion(text_embedding, image_embedding)
        
        assert result == [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    
    def test_calculate_hybrid_similarity_cosine(self, service):
        """Test hybrid similarity calculation with cosine method."""
        embedding1 = [1.0, 0.0, 0.0]
        embedding2 = [0.0, 1.0, 0.0]
        
        similarity = service.calculate_hybrid_similarity(
            embedding1, embedding2, similarity_type="cosine"
        )
        
        assert similarity == 0.0
    
    @pytest.mark.asyncio
    async def test_find_similar_questions_success(self, service):
        """Test finding similar questions."""
        query_embedding = [1.0, 0.0, 0.0]
        candidate_embeddings = [
            (1, [0.9, 0.1, 0.0]),  # High similarity
            (2, [0.0, 1.0, 0.0]),  # Low similarity
            (3, [0.8, 0.2, 0.0]),  # Medium similarity
        ]
        
        results = await service.find_similar_questions(
            query_embedding, candidate_embeddings, top_k=2, threshold=0.5
        )
        
        assert len(results) <= 2
        # All results should meet threshold
        for question_id, similarity in results:
            assert similarity >= 0.5
    
    def test_get_embedding_info(self, service):
        """Test getting embedding configuration info."""
        info = service.get_embedding_info()
        
        expected_keys = [
            'fusion_method', 'text_weight', 'image_weight',
            'text_dim', 'image_dim', 'hybrid_dim',
            'supported_fusion_methods', 'supported_similarity_types'
        ]
        
        for key in expected_keys:
            assert key in info
        
        assert info['fusion_method'] == "concatenation"
        assert info['text_weight'] == 0.7
        assert info['image_weight'] == 0.3
        assert info['hybrid_dim'] == 1536

if __name__ == "__main__":
    pytest.main([__file__]) 