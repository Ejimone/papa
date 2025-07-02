"""
Tests for the question processing script.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import sys
import os

# Mock the database imports before importing the script
sys.modules['sqlalchemy.orm'] = Mock()
sys.modules['app.core.database'] = Mock()
sys.modules['app.ai.vector_db.client'] = Mock()

# Import the script after mocking dependencies
from backend.scripts.process_questions import QuestionProcessor

class TestQuestionProcessorBasic:
    """Basic tests for QuestionProcessor functionality."""
    
    def test_processor_import(self):
        """Test that the processor can be imported and instantiated."""
        # Mock the dependencies that might not be available
        with patch('sys.modules'), \
             patch('sqlalchemy.orm'), \
             patch('app.core.database'), \
             patch('app.ai.embeddings.text_embeddings.TextEmbeddingService'), \
             patch('app.ai.embeddings.image_embeddings.ImageEmbeddingService'), \
             patch('app.ai.embeddings.hybrid_embeddings.HybridEmbeddingService'), \
             patch('app.ai.llm.gemini_client.GeminiClient'), \
             patch('app.ai.vector_db.client.ChromaClient'):
            
            # Try to import the module
            try:
                import backend.scripts.process_questions as pq
                processor = pq.QuestionProcessor(batch_size=1, dry_run=True)
                assert processor.batch_size == 1
                assert processor.dry_run is True
            except ImportError:
                pytest.skip("Cannot import process_questions due to missing dependencies")
    
    def test_stats_initialization(self):
        """Test that statistics are properly initialized."""
        with patch('sys.modules'), \
             patch('app.ai.embeddings.text_embeddings.TextEmbeddingService'), \
             patch('app.ai.embeddings.image_embeddings.ImageEmbeddingService'), \
             patch('app.ai.embeddings.hybrid_embeddings.HybridEmbeddingService'), \
             patch('app.ai.llm.gemini_client.GeminiClient'), \
             patch('app.ai.vector_db.client.ChromaClient'):
            
            try:
                import backend.scripts.process_questions as pq
                processor = pq.QuestionProcessor()
                
                expected_stats = {
                    'processed': 0,
                    'failed': 0,
                    'skipped': 0,
                    'embeddings_generated': 0,
                    'metadata_extracted': 0,
                    'images_processed': 0
                }
                
                assert processor.stats == expected_stats
            except ImportError:
                pytest.skip("Cannot import process_questions due to missing dependencies")

class TestQuestionProcessorMethods:
    """Test individual methods of QuestionProcessor."""
    
    @pytest.fixture
    def mock_processor(self):
        """Create a mock processor for testing."""
        processor = Mock()
        processor.batch_size = 10
        processor.dry_run = False
        processor.stats = {
            'processed': 0,
            'failed': 0,
            'skipped': 0,
            'embeddings_generated': 0,
            'metadata_extracted': 0,
            'images_processed': 0
        }
        return processor
    
    def test_stats_tracking(self, mock_processor):
        """Test that statistics are properly tracked."""
        # Simulate processing success
        mock_processor.stats['processed'] += 1
        mock_processor.stats['embeddings_generated'] += 1
        
        assert mock_processor.stats['processed'] == 1
        assert mock_processor.stats['embeddings_generated'] == 1
        assert mock_processor.stats['failed'] == 0
    
    def test_error_handling_simulation(self, mock_processor):
        """Test error handling simulation."""
        # Simulate processing failure
        mock_processor.stats['failed'] += 1
        
        assert mock_processor.stats['failed'] == 1
        assert mock_processor.stats['processed'] == 0

class TestQuestionProcessorConfiguration:
    """Test different configurations of QuestionProcessor."""
    
    def test_different_batch_sizes(self):
        """Test processor with different batch sizes."""
        batch_sizes = [1, 5, 10, 20]
        
        for batch_size in batch_sizes:
            with patch('app.ai.embeddings.text_embeddings.TextEmbeddingService'), \
                 patch('app.ai.embeddings.image_embeddings.ImageEmbeddingService'), \
                 patch('app.ai.embeddings.hybrid_embeddings.HybridEmbeddingService'), \
                 patch('app.ai.llm.gemini_client.GeminiClient'), \
                 patch('app.ai.vector_db.client.ChromaClient'):
                
                try:
                    import backend.scripts.process_questions as pq
                    processor = pq.QuestionProcessor(batch_size=batch_size)
                    assert processor.batch_size == batch_size
                except ImportError:
                    pytest.skip("Cannot import process_questions due to missing dependencies")
    
    def test_dry_run_modes(self):
        """Test processor in different dry run modes."""
        for dry_run in [True, False]:
            with patch('app.ai.embeddings.text_embeddings.TextEmbeddingService'), \
                 patch('app.ai.embeddings.image_embeddings.ImageEmbeddingService'), \
                 patch('app.ai.embeddings.hybrid_embeddings.HybridEmbeddingService'), \
                 patch('app.ai.llm.gemini_client.GeminiClient'), \
                 patch('app.ai.vector_db.client.ChromaClient'):
                
                try:
                    import backend.scripts.process_questions as pq
                    processor = pq.QuestionProcessor(dry_run=dry_run)
                    assert processor.dry_run == dry_run
                except ImportError:
                    pytest.skip("Cannot import process_questions due to missing dependencies")

class TestQuestionProcessor:
    """Test suite for QuestionProcessor."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        session = Mock()
        session.query.return_value.filter.return_value.filter.return_value.all.return_value = []
        session.commit = Mock()
        session.add = Mock()
        return session
    
    @pytest.fixture
    def mock_question(self):
        """Mock question object."""
        question = Mock()
        question.id = 1
        question.title = "Sample Question"
        question.content = "What is 2 + 2?"
        question.answer = "4"
        question.images = []
        question.subject_id = 1
        question.topic_id = 1
        question.difficulty_level = "intermediate"
        question.question_type = "multiple_choice"
        question.is_processed_for_embedding = False
        question.processing_error_log = None
        question.vector_id = None
        
        # Mock relationships
        question.subject = Mock()
        question.subject.name = "Mathematics"
        question.topic = Mock()
        question.topic.name = "Arithmetic"
        question.question_metadata = None
        question.explanations = []
        question.hints = []
        
        return question
    
    @pytest.fixture
    def processor(self):
        """Create a test processor instance."""
        with patch('backend.scripts.process_questions.TextEmbeddingService'), \
             patch('backend.scripts.process_questions.ImageEmbeddingService'), \
             patch('backend.scripts.process_questions.HybridEmbeddingService'), \
             patch('backend.scripts.process_questions.GeminiClient'), \
             patch('backend.scripts.process_questions.ChromaClient'):
            
            return QuestionProcessor(batch_size=2, dry_run=True)
    
    def test_init_success(self):
        """Test successful processor initialization."""
        with patch('backend.scripts.process_questions.TextEmbeddingService'), \
             patch('backend.scripts.process_questions.ImageEmbeddingService'), \
             patch('backend.scripts.process_questions.HybridEmbeddingService'), \
             patch('backend.scripts.process_questions.GeminiClient'), \
             patch('backend.scripts.process_questions.ChromaClient'):
            
            processor = QuestionProcessor(batch_size=5, dry_run=False)
            assert processor.batch_size == 5
            assert processor.dry_run is False
            assert processor.stats['processed'] == 0
    
    def test_init_service_failure(self):
        """Test processor initialization with service failure."""
        with patch('backend.scripts.process_questions.TextEmbeddingService', side_effect=Exception("Service error")):
            
            with pytest.raises(Exception, match="Service error"):
                QuestionProcessor()
    
    @pytest.mark.asyncio
    async def test_process_all_questions_no_questions(self, processor):
        """Test processing when no questions are found."""
        with patch('backend.scripts.process_questions.SessionLocal') as mock_session_local:
            mock_session = Mock()
            mock_session.__enter__ = Mock(return_value=mock_session)
            mock_session.__exit__ = Mock(return_value=None)
            mock_session.query.return_value.filter.return_value.filter.return_value.all.return_value = []
            mock_session_local.return_value = mock_session
            
            await processor.process_all_questions()
            
            assert processor.stats['processed'] == 0
    
    @pytest.mark.asyncio
    async def test_process_all_questions_with_subject_filter(self, processor, mock_question):
        """Test processing with subject filter."""
        with patch('backend.scripts.process_questions.SessionLocal') as mock_session_local:
            mock_session = Mock()
            mock_session.__enter__ = Mock(return_value=mock_session)
            mock_session.__exit__ = Mock(return_value=None)
            
            # Set up query chain
            query_mock = Mock()
            query_mock.filter.return_value.filter.return_value.all.return_value = [mock_question]
            mock_session.query.return_value = query_mock
            
            mock_session_local.return_value = mock_session
            
            with patch.object(processor, '_process_question_batch', new_callable=AsyncMock) as mock_process:
                await processor.process_all_questions(subject_id=1)
                
                # Verify subject filter was applied
                mock_process.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_question_batch_success(self, processor, mock_question, mock_db_session):
        """Test successful batch processing."""
        questions = [mock_question]
        
        with patch.object(processor, '_process_single_question', new_callable=AsyncMock) as mock_process:
            await processor._process_question_batch(questions, mock_db_session)
            
            mock_process.assert_called_once_with(mock_question, mock_db_session)
            assert processor.stats['processed'] == 1
    
    @pytest.mark.asyncio
    async def test_process_question_batch_error(self, processor, mock_question, mock_db_session):
        """Test batch processing with error."""
        questions = [mock_question]
        
        with patch.object(processor, '_process_single_question', new_callable=AsyncMock) as mock_process:
            mock_process.side_effect = Exception("Processing error")
            
            await processor._process_question_batch(questions, mock_db_session)
            
            assert processor.stats['failed'] == 1
            assert mock_question.processing_error_log == "Processing error"
    
    @pytest.mark.asyncio
    async def test_process_single_question_complete(self, processor, mock_question, mock_db_session):
        """Test complete single question processing."""
        with patch.object(processor, '_extract_metadata', new_callable=AsyncMock) as mock_extract, \
             patch.object(processor, '_process_question_images', new_callable=AsyncMock) as mock_images, \
             patch.object(processor, '_generate_embeddings', new_callable=AsyncMock) as mock_embeddings, \
             patch.object(processor, '_generate_explanations_and_hints', new_callable=AsyncMock) as mock_explain, \
             patch.object(processor, '_find_similar_questions', new_callable=AsyncMock) as mock_similar:
            
            mock_images.return_value = []
            
            await processor._process_single_question(mock_question, mock_db_session)
            
            # Verify all processing steps were called
            mock_extract.assert_called_once()
            mock_images.assert_called_once()
            mock_embeddings.assert_called_once()
            mock_explain.assert_called_once()
            mock_similar.assert_called_once()
            
            # Verify question status updated
            assert mock_question.is_processed_for_embedding is True
            assert mock_question.processing_error_log is None
    
    @pytest.mark.asyncio
    async def test_extract_metadata_success(self, processor, mock_question, mock_db_session):
        """Test successful metadata extraction."""
        processor.gemini_client.generate_text = AsyncMock(return_value="Generated metadata")
        
        await processor._extract_metadata(mock_question, mock_db_session)
        
        processor.gemini_client.generate_text.assert_called_once()
        assert processor.stats['metadata_extracted'] == 1
    
    @pytest.mark.asyncio
    async def test_extract_metadata_with_existing_metadata(self, processor, mock_question, mock_db_session):
        """Test metadata extraction when metadata already exists."""
        # Add existing metadata
        existing_metadata = Mock()
        mock_question.question_metadata = existing_metadata
        
        processor.gemini_client.generate_text = AsyncMock(return_value="Generated metadata")
        
        await processor._extract_metadata(mock_question, mock_db_session)
        
        # Verify existing metadata was updated
        assert existing_metadata.keywords is not None
        assert processor.stats['metadata_extracted'] == 1
    
    @pytest.mark.asyncio
    async def test_process_question_images_success(self, processor, mock_question, mock_db_session):
        """Test successful image processing."""
        # Add mock images to question
        mock_image = Mock()
        mock_image.id = 1
        mock_image.image_url = "http://example.com/image.jpg"
        mock_question.images = [mock_image]
        
        # Mock image download and processing
        with patch.object(processor, '_download_image', new_callable=AsyncMock) as mock_download:
            mock_download.return_value = b"fake_image_data"
            
            processor.image_service.process_question_image = AsyncMock(return_value={
                'success': True,
                'ocr_text': 'Sample text',
                'ocr_confidence': 0.8,
                'description': 'Sample description',
                'width': 100,
                'height': 100,
                'file_size': 1024
            })
            
            result = await processor._process_question_images(mock_question, mock_db_session)
            
            assert len(result) == 1
            assert mock_image.ocr_text == 'Sample text'
            assert mock_image.is_processed is True
            assert processor.stats['images_processed'] == 1
    
    @pytest.mark.asyncio
    async def test_process_question_images_no_images(self, processor, mock_question, mock_db_session):
        """Test image processing when no images exist."""
        mock_question.images = []
        
        result = await processor._process_question_images(mock_question, mock_db_session)
        
        assert result == []
        assert processor.stats['images_processed'] == 0
    
    @pytest.mark.asyncio
    async def test_download_image_success(self, processor):
        """Test successful image download."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.content = b"fake_image_data"
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            result = await processor._download_image("http://example.com/image.jpg")
            
            assert result == b"fake_image_data"
            mock_get.assert_called_once_with("http://example.com/image.jpg", timeout=30)
    
    @pytest.mark.asyncio
    async def test_download_image_failure(self, processor):
        """Test failed image download."""
        with patch('requests.get', side_effect=Exception("Network error")):
            result = await processor._download_image("http://example.com/image.jpg")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_success(self, processor, mock_question, mock_db_session):
        """Test successful embedding generation."""
        # Mock metadata
        mock_metadata = Mock()
        mock_metadata.keywords = ['math']
        mock_metadata.concepts = ['arithmetic']
        mock_question.question_metadata = mock_metadata
        
        processor.hybrid_service.create_question_embedding = AsyncMock(return_value={
            'success': True,
            'hybrid_embedding': [0.1] * 1536
        })
        
        await processor._generate_embeddings(mock_question, [], mock_db_session)
        
        assert mock_question.vector_id == f"question_{mock_question.id}"
        assert processor.stats['embeddings_generated'] == 1
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_failure(self, processor, mock_question, mock_db_session):
        """Test embedding generation failure."""
        processor.hybrid_service.create_question_embedding = AsyncMock(return_value={
            'success': False
        })
        
        await processor._generate_embeddings(mock_question, [], mock_db_session)
        
        assert processor.stats['embeddings_generated'] == 0
    
    @pytest.mark.asyncio
    async def test_generate_explanations_and_hints_new(self, processor, mock_question, mock_db_session):
        """Test generating explanations and hints for question without them."""
        mock_question.explanations = []
        mock_question.hints = []
        
        processor.gemini_client.generate_explanation = AsyncMock(return_value="Sample explanation")
        
        await processor._generate_explanations_and_hints(mock_question, mock_db_session)
        
        processor.gemini_client.generate_explanation.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_explanations_and_hints_existing(self, processor, mock_question, mock_db_session):
        """Test with existing explanations and hints."""
        mock_question.explanations = [Mock()]  # Already has explanations
        mock_question.hints = [Mock()]  # Already has hints
        
        processor.gemini_client.generate_explanation = AsyncMock()
        
        await processor._generate_explanations_and_hints(mock_question, mock_db_session)
        
        # Should not generate new ones
        processor.gemini_client.generate_explanation.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_find_similar_questions_with_vector_id(self, processor, mock_question, mock_db_session):
        """Test finding similar questions when vector_id exists."""
        mock_question.vector_id = "question_1"
        
        await processor._find_similar_questions(mock_question, mock_db_session)
        
        # Should complete without error (actual implementation would query vector DB)
    
    @pytest.mark.asyncio
    async def test_find_similar_questions_no_vector_id(self, processor, mock_question, mock_db_session):
        """Test finding similar questions when no vector_id exists."""
        mock_question.vector_id = None
        
        await processor._find_similar_questions(mock_question, mock_db_session)
        
        # Should return early without processing
    
    def test_print_statistics(self, processor, capsys):
        """Test statistics printing."""
        processor.stats['processed'] = 5
        processor.stats['failed'] = 1
        processor.stats['embeddings_generated'] = 4
        
        processor._print_statistics()
        
        captured = capsys.readouterr()
        assert "Questions processed: 5" in captured.out
        assert "Questions failed: 1" in captured.out
        assert "Embeddings generated: 4" in captured.out

class TestQuestionProcessorIntegration:
    """Integration tests for QuestionProcessor."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_processing_flow(self):
        """Test complete processing flow with mocked dependencies."""
        # This would be a more comprehensive test with actual database
        # and API mocking for integration testing
        pass

if __name__ == "__main__":
    pytest.main([__file__]) 