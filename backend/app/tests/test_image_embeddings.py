import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from io import BytesIO
from PIL import Image
import numpy as np

from app.ai.embeddings.image_embeddings import ImageEmbeddingService

class TestImageEmbeddingService:
    """Test suite for ImageEmbeddingService."""
    
    @pytest.fixture
    def service(self):
        """Create a test service instance."""
        with patch('google.generativeai.configure'):
            return ImageEmbeddingService()
    
    @pytest.fixture
    def sample_image_data(self):
        """Create sample image data for testing."""
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
    
    def test_init_success(self):
        """Test successful initialization."""
        with patch('google.generativeai.configure'), \
             patch('app.core.config.settings') as mock_settings:
            mock_settings.GEMINI_API_KEY = "test_api_key"
            
            service = ImageEmbeddingService()
            assert service.api_key == "test_api_key"
            assert service.vision_model_name == "gemini-pro-vision"
            assert service.embedding_model_name == "text-embedding-004"
    
    def test_init_no_api_key(self):
        """Test initialization without API key raises error."""
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.GEMINI_API_KEY = None
            
            with pytest.raises(ValueError, match="Gemini API key is not configured"):
                ImageEmbeddingService()
    
    def test_prepare_image_success(self, service, sample_image_data):
        """Test successful image preparation."""
        image = service._prepare_image(sample_image_data)
        assert isinstance(image, Image.Image)
        assert image.mode == 'RGB'
        assert image.size == (100, 100)
    
    def test_prepare_image_invalid_data(self, service):
        """Test image preparation with invalid data."""
        invalid_data = b"not an image"
        
        with pytest.raises(ValueError, match="Invalid image data"):
            service._prepare_image(invalid_data)
    
    @pytest.mark.asyncio
    async def test_extract_text_from_image_success(self, service, sample_image_data):
        """Test successful text extraction from image."""
        mock_response = Mock()
        mock_response.text = """TEXT: Sample extracted text
DESCRIPTION: A red square image
CONFIDENCE: 0.9"""
        
        with patch.object(service, 'vision_model') as mock_model:
            mock_model.generate_content.return_value = mock_response
            
            result = await service.extract_text_from_image(sample_image_data)
            
            assert result['success'] is True
            assert result['text'] == "Sample extracted text"
            assert result['description'] == "A red square image"
            assert result['confidence'] == 0.9
    
    @pytest.mark.asyncio
    async def test_extract_text_from_image_error(self, service, sample_image_data):
        """Test text extraction with error."""
        with patch.object(service, 'vision_model') as mock_model:
            mock_model.generate_content.side_effect = Exception("API Error")
            
            result = await service.extract_text_from_image(sample_image_data)
            
            assert result['success'] is False
            assert result['error'] == "API Error"
            assert result['text'] == ""
            assert result['confidence'] == 0.0
    
    @pytest.mark.asyncio
    async def test_analyze_image_content_success(self, service, sample_image_data):
        """Test successful image content analysis."""
        mock_response = Mock()
        mock_response.text = """CONTENT_TYPE: diagram
SUBJECT_AREA: mathematics
COMPLEXITY: basic
VISUAL_ELEMENTS: geometric shapes
EDUCATIONAL_VALUE: teaches basic geometry"""
        
        with patch.object(service, 'vision_model') as mock_model:
            mock_model.generate_content.return_value = mock_response
            
            result = await service.analyze_image_content(sample_image_data)
            
            assert result['success'] is True
            analysis = result['analysis']
            assert analysis['content_type'] == "diagram"
            assert analysis['subject_area'] == "mathematics"
            assert analysis['complexity'] == "basic"
    
    @pytest.mark.asyncio
    async def test_generate_image_description_embedding_success(self, service, sample_image_data):
        """Test successful embedding generation from image description."""
        mock_response = Mock()
        mock_response.text = "This is a red square image showing geometric concepts"
        
        with patch.object(service, 'vision_model') as mock_model:
            mock_model.generate_content.return_value = mock_response
            
            embedding = await service.generate_image_description_embedding(sample_image_data)
            
            assert isinstance(embedding, list)
            assert len(embedding) == 768
            assert all(isinstance(x, float) for x in embedding)
            
            # Check that embedding is normalized (magnitude should be close to 1)
            magnitude = sum(x*x for x in embedding) ** 0.5
            assert 0.9 <= magnitude <= 1.1
    
    @pytest.mark.asyncio
    async def test_generate_image_description_embedding_error(self, service, sample_image_data):
        """Test embedding generation with error."""
        with patch.object(service, 'vision_model') as mock_model:
            mock_model.generate_content.side_effect = Exception("API Error")
            
            embedding = await service.generate_image_description_embedding(sample_image_data)
            
            assert isinstance(embedding, list)
            assert len(embedding) == 768
            assert all(x == 0.0 for x in embedding)
    
    @pytest.mark.asyncio
    async def test_process_question_image_success(self, service, sample_image_data):
        """Test complete question image processing."""
        # Mock all the async methods
        with patch.object(service, 'extract_text_from_image') as mock_extract, \
             patch.object(service, 'analyze_image_content') as mock_analyze, \
             patch.object(service, 'generate_image_description_embedding') as mock_embed:
            
            mock_extract.return_value = {
                'text': 'Sample text',
                'description': 'Sample description',
                'confidence': 0.8
            }
            
            mock_analyze.return_value = {
                'analysis': {'content_type': 'diagram'}
            }
            
            mock_embed.return_value = [0.1] * 768
            
            result = await service.process_question_image(sample_image_data, "http://example.com/image.png")
            
            assert result['success'] is True
            assert result['ocr_text'] == 'Sample text'
            assert result['ocr_confidence'] == 0.8
            assert result['description'] == 'Sample description'
            assert result['content_analysis'] == {'content_type': 'diagram'}
            assert len(result['embedding']) == 768
            assert result['width'] == 100
            assert result['height'] == 100
            assert result['file_size'] == len(sample_image_data)
    
    @pytest.mark.asyncio
    async def test_process_question_image_error(self, service):
        """Test question image processing with error."""
        invalid_data = b"invalid"
        
        result = await service.process_question_image(invalid_data, "http://example.com/image.png")
        
        assert result['success'] is False
        assert result['processing_error'] is not None
        assert result['ocr_text'] == ""
        assert result['ocr_confidence'] == 0.0
    
    def test_calculate_image_similarity_success(self, service):
        """Test successful similarity calculation."""
        embedding1 = [1.0, 0.0, 0.0]
        embedding2 = [0.0, 1.0, 0.0]
        
        similarity = service.calculate_image_similarity(embedding1, embedding2)
        
        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0
        assert similarity == 0.0  # Orthogonal vectors
    
    def test_calculate_image_similarity_identical(self, service):
        """Test similarity calculation with identical embeddings."""
        embedding = [1.0, 0.0, 0.0]
        
        similarity = service.calculate_image_similarity(embedding, embedding)
        
        assert similarity == 1.0
    
    def test_calculate_image_similarity_different_lengths(self, service):
        """Test similarity calculation with different length embeddings."""
        embedding1 = [1.0, 0.0]
        embedding2 = [0.0, 1.0, 0.0]
        
        similarity = service.calculate_image_similarity(embedding1, embedding2)
        
        assert similarity == 0.0
    
    def test_calculate_image_similarity_zero_vectors(self, service):
        """Test similarity calculation with zero vectors."""
        embedding1 = [0.0, 0.0, 0.0]
        embedding2 = [1.0, 0.0, 0.0]
        
        similarity = service.calculate_image_similarity(embedding1, embedding2)
        
        assert similarity == 0.0
    
    def test_calculate_image_similarity_error(self, service):
        """Test similarity calculation with error."""
        # This should trigger an exception in the calculation
        embedding1 = None
        embedding2 = [1.0, 0.0, 0.0]
        
        similarity = service.calculate_image_similarity(embedding1, embedding2)
        
        assert similarity == 0.0

class TestImageEmbeddingServiceIntegration:
    """Integration tests for ImageEmbeddingService."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_real_api_call(self):
        """Test with real API call (requires valid API key)."""
        # Skip if no API key available
        try:
            service = ImageEmbeddingService()
        except ValueError:
            pytest.skip("No API key available for integration test")
        
        # Create a simple test image
        img = Image.new('RGB', (50, 50), color='blue')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        image_data = img_bytes.getvalue()
        
        # This would make real API calls - only run in integration environment
        # result = await service.extract_text_from_image(image_data)
        # assert 'success' in result
        
        # For now, just test that the service can be initialized
        assert service is not None

class TestImageEmbeddingServiceSingleton:
    """Test the singleton instance."""
    
    def test_singleton_import(self):
        """Test that the singleton can be imported."""
        from app.ai.embeddings.image_embeddings import image_embedding_service
        
        assert image_embedding_service is not None

if __name__ == "__main__":
    pytest.main([__file__]) 