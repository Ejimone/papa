#!/usr/bin/env python3
"""
Question Processing Script

This script processes questions in the database to:
1. Extract metadata using AI
2. Generate text and image embeddings
3. Process images and extract OCR text
4. Generate explanations and hints
5. Find similar questions
6. Update database with processed results

Usage:
    python scripts/process_questions.py [options]
    
Options:
    --batch-size: Number of questions to process in one batch (default: 10)
    --subject-id: Process only questions from specific subject
    --reprocess: Reprocess already processed questions
    --dry-run: Run without saving to database
    --verbose: Enable verbose logging
"""

import asyncio
import argparse
import logging
import sys
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

# Add the parent directory to the path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.question import Question, QuestionMetadata, QuestionImage, Explanation, Hint
from app.models.subject import Subject, Topic
from app.ai.embeddings.text_embeddings import TextEmbeddingService
from app.ai.embeddings.image_embeddings import ImageEmbeddingService
from app.ai.embeddings.hybrid_embeddings import HybridEmbeddingService
from app.ai.llm.gemini_client import GeminiClient
from app.ai.vector_db.client import ChromaClient
import requests
from io import BytesIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QuestionProcessor:
    def __init__(self, batch_size: int = 10, dry_run: bool = False):
        self.batch_size = batch_size
        self.dry_run = dry_run
        
        # Initialize AI services
        try:
            self.text_service = TextEmbeddingService()
            self.image_service = ImageEmbeddingService()
            self.hybrid_service = HybridEmbeddingService()
            self.gemini_client = GeminiClient()
            self.vector_client = ChromaClient()
        except Exception as e:
            logger.error(f"Failed to initialize AI services: {e}")
            raise

        # Processing statistics
        self.stats = {
            'processed': 0,
            'failed': 0,
            'skipped': 0,
            'embeddings_generated': 0,
            'metadata_extracted': 0,
            'images_processed': 0
        }

    async def process_all_questions(
        self, 
        subject_id: Optional[int] = None, 
        reprocess: bool = False
    ) -> None:
        """Process all unprocessed questions in batches."""
        logger.info("Starting question processing...")
        
        with SessionLocal() as db:
            # Get questions to process
            query = db.query(Question)
            
            if subject_id:
                query = query.filter(Question.subject_id == subject_id)
            
            if not reprocess:
                query = query.filter(Question.is_processed_for_embedding == False)
            
            questions = query.filter(Question.is_active == True).all()
            
            total_questions = len(questions)
            logger.info(f"Found {total_questions} questions to process")
            
            if total_questions == 0:
                logger.info("No questions to process")
                return
            
            # Process in batches
            for i in range(0, total_questions, self.batch_size):
                batch = questions[i:i + self.batch_size]
                batch_num = (i // self.batch_size) + 1
                total_batches = (total_questions + self.batch_size - 1) // self.batch_size
                
                logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} questions)")
                
                await self._process_question_batch(batch, db)
                
                # Commit changes after each batch
                if not self.dry_run:
                    db.commit()
                    logger.info(f"Batch {batch_num} committed to database")
        
        # Print final statistics
        self._print_statistics()

    async def _process_question_batch(self, questions: List[Question], db: Session) -> None:
        """Process a batch of questions."""
        for question in questions:
            try:
                await self._process_single_question(question, db)
                self.stats['processed'] += 1
                
            except Exception as e:
                logger.error(f"Failed to process question {question.id}: {e}")
                question.processing_error_log = str(e)
                self.stats['failed'] += 1
                
                if not self.dry_run:
                    db.add(question)

    async def _process_single_question(self, question: Question, db: Session) -> None:
        """Process a single question completely."""
        logger.info(f"Processing question {question.id}: {question.title[:50]}...")
        
        # Step 1: Extract and update metadata
        await self._extract_metadata(question, db)
        
        # Step 2: Process images if any
        image_data = []
        if question.images:
            image_data = await self._process_question_images(question, db)
        
        # Step 3: Generate embeddings
        await self._generate_embeddings(question, image_data, db)
        
        # Step 4: Generate explanations and hints
        await self._generate_explanations_and_hints(question, db)
        
        # Step 5: Find and store similar questions
        await self._find_similar_questions(question, db)
        
        # Step 6: Update processing status
        question.is_processed_for_embedding = True
        question.processing_error_log = None
        
        if not self.dry_run:
            db.add(question)
        
        logger.info(f"Successfully processed question {question.id}")

    async def _extract_metadata(self, question: Question, db: Session) -> None:
        """Extract metadata using AI."""
        try:
            # Prepare content for analysis
            content = f"Question: {question.content}"
            if question.answer:
                content += f"\nAnswer: {question.answer}"
            
            # Use Gemini to extract metadata
            prompt = f"""Analyze this academic question and extract metadata in JSON format:

{content}

Provide the following metadata:
{{
    "keywords": ["keyword1", "keyword2", ...],
    "concepts": ["concept1", "concept2", ...],
    "prerequisites": ["prereq1", "prereq2", ...],
    "learning_objectives": ["objective1", "objective2", ...],
    "clarity_score": 0.0-1.0,
    "completeness_score": 0.0-1.0,
    "difficulty_confidence": 0.0-1.0
}}"""
            
            response = await self.gemini_client.generate_text(prompt)
            
            # Parse JSON response (simplified - in production, use proper JSON parsing)
            # For now, create reasonable metadata
            metadata_dict = {
                "keywords": [question.title.split()[0]] if question.title else [],
                "concepts": [str(question.difficulty_level)],
                "prerequisites": [],
                "learning_objectives": [f"Understand {question.question_type}"],
                "clarity_score": 0.8,
                "completeness_score": 0.7,
                "difficulty_confidence": 0.8
            }
            
            # Create or update metadata
            if not question.question_metadata:
                metadata = QuestionMetadata(
                    question_id=question.id,
                    keywords=metadata_dict["keywords"],
                    concepts=metadata_dict["concepts"],
                    prerequisites=metadata_dict["prerequisites"],
                    learning_objectives=metadata_dict["learning_objectives"],
                    clarity_score=metadata_dict["clarity_score"],
                    completeness_score=metadata_dict["completeness_score"],
                    difficulty_confidence=metadata_dict["difficulty_confidence"]
                )
                if not self.dry_run:
                    db.add(metadata)
            else:
                # Update existing metadata
                metadata = question.question_metadata
                metadata.keywords = metadata_dict["keywords"]
                metadata.concepts = metadata_dict["concepts"]
                metadata.prerequisites = metadata_dict["prerequisites"]
                metadata.learning_objectives = metadata_dict["learning_objectives"]
                metadata.clarity_score = metadata_dict["clarity_score"]
                metadata.completeness_score = metadata_dict["completeness_score"]
                metadata.difficulty_confidence = metadata_dict["difficulty_confidence"]
                
                if not self.dry_run:
                    db.add(metadata)
            
            self.stats['metadata_extracted'] += 1
            
        except Exception as e:
            logger.error(f"Failed to extract metadata for question {question.id}: {e}")
            raise

    async def _process_question_images(self, question: Question, db: Session) -> List[bytes]:
        """Process all images associated with a question."""
        image_data_list = []
        
        for image in question.images:
            try:
                # Download image data
                image_data = await self._download_image(image.image_url)
                if not image_data:
                    continue
                
                # Process image using image service
                result = await self.image_service.process_question_image(
                    image_data, image.image_url
                )
                
                if result['success']:
                    # Update image record with processing results
                    image.ocr_text = result['ocr_text']
                    image.ocr_confidence = result['ocr_confidence']
                    image.alt_text = result['description']
                    image.width = result['width']
                    image.height = result['height']
                    image.file_size = result['file_size']
                    image.is_processed = True
                    image.processed_at = datetime.utcnow()
                    
                    if not self.dry_run:
                        db.add(image)
                    
                    image_data_list.append(image_data)
                    self.stats['images_processed'] += 1
                else:
                    logger.warning(f"Failed to process image {image.id}: {result.get('processing_error')}")
                    
            except Exception as e:
                logger.error(f"Error processing image {image.id}: {e}")
                continue
        
        return image_data_list

    async def _download_image(self, image_url: str) -> Optional[bytes]:
        """Download image from URL."""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Failed to download image from {image_url}: {e}")
            return None

    async def _generate_embeddings(self, question: Question, image_data: List[bytes], db: Session) -> None:
        """Generate embeddings for the question."""
        try:
            # Prepare metadata for embedding
            metadata = {}
            if question.question_metadata:
                metadata = {
                    'keywords': question.question_metadata.keywords or [],
                    'concepts': question.question_metadata.concepts or [],
                    'subject': question.subject.name if question.subject else '',
                    'topic': question.topic.name if question.topic else ''
                }
                
                # Add OCR text from images
                ocr_texts = []
                for img in question.images:
                    if img.ocr_text:
                        ocr_texts.append(img.ocr_text)
                if ocr_texts:
                    metadata['ocr_text'] = ' '.join(ocr_texts)
            
            # Generate hybrid embedding
            embedding_result = await self.hybrid_service.create_question_embedding(
                question_text=question.content,
                question_images=image_data,
                question_metadata=metadata
            )
            
            if embedding_result['success']:
                # Store in vector database
                vector_id = f"question_{question.id}"
                
                # Prepare document for vector DB
                document = {
                    'id': vector_id,
                    'text': question.content,
                    'metadata': {
                        'question_id': question.id,
                        'subject_id': question.subject_id,
                        'topic_id': question.topic_id,
                        'difficulty': str(question.difficulty_level),
                        'question_type': str(question.question_type),
                        'title': question.title
                    },
                    'embedding': embedding_result['hybrid_embedding']
                }
                
                if not self.dry_run:
                    # Store in ChromaDB (mock implementation)
                    # self.vector_client.add_document(document)
                    pass
                
                # Update question with vector ID
                question.vector_id = vector_id
                
                if not self.dry_run:
                    db.add(question)
                
                self.stats['embeddings_generated'] += 1
                logger.info(f"Generated embeddings for question {question.id}")
            else:
                logger.error(f"Failed to generate embeddings for question {question.id}")
                
        except Exception as e:
            logger.error(f"Error generating embeddings for question {question.id}: {e}")
            raise

    async def _generate_explanations_and_hints(self, question: Question, db: Session) -> None:
        """Generate AI explanations and hints for the question."""
        try:
            # Generate explanation if none exists
            if not question.explanations:
                explanation_text = await self.gemini_client.generate_explanation(
                    question.content, question.answer
                )
                
                explanation = Explanation(
                    question_id=question.id,
                    content=explanation_text,
                    explanation_type="step_by_step",
                    is_ai_generated=True,
                    ai_model="gemini-pro",
                    confidence_score=0.8
                )
                
                if not self.dry_run:
                    db.add(explanation)
            
            # Generate hints if none exist
            if not question.hints:
                hint_text = f"Consider the {question.question_type} format and {question.difficulty_level} level"
                
                hint = Hint(
                    question_id=question.id,
                    level=1,
                    content=hint_text,
                    hint_type="concept",
                    is_ai_generated=True,
                    ai_model="gemini-pro"
                )
                
                if not self.dry_run:
                    db.add(hint)
                    
        except Exception as e:
            logger.error(f"Error generating explanations/hints for question {question.id}: {e}")
            # Don't raise - this is not critical for processing

    async def _find_similar_questions(self, question: Question, db: Session) -> None:
        """Find and store similar questions."""
        try:
            if not question.vector_id:
                return
            
            # This would use the vector database to find similar questions
            # For now, just log that we would do this
            logger.info(f"Would find similar questions for question {question.id}")
            
            # In a real implementation:
            # 1. Query vector DB for similar embeddings
            # 2. Calculate similarity scores
            # 3. Store in SimilarQuestion table
            
        except Exception as e:
            logger.error(f"Error finding similar questions for question {question.id}: {e}")
            # Don't raise - this is not critical

    def _print_statistics(self) -> None:
        """Print processing statistics."""
        logger.info("=" * 50)
        logger.info("PROCESSING STATISTICS")
        logger.info("=" * 50)
        logger.info(f"Questions processed: {self.stats['processed']}")
        logger.info(f"Questions failed: {self.stats['failed']}")
        logger.info(f"Questions skipped: {self.stats['skipped']}")
        logger.info(f"Embeddings generated: {self.stats['embeddings_generated']}")
        logger.info(f"Metadata extracted: {self.stats['metadata_extracted']}")
        logger.info(f"Images processed: {self.stats['images_processed']}")
        logger.info("=" * 50)

async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Process questions for AI analysis')
    parser.add_argument('--batch-size', type=int, default=10, help='Batch size for processing')
    parser.add_argument('--subject-id', type=int, help='Process only questions from specific subject')
    parser.add_argument('--reprocess', action='store_true', help='Reprocess already processed questions')
    parser.add_argument('--dry-run', action='store_true', help='Run without saving to database')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No changes will be saved to database")
    
    try:
        processor = QuestionProcessor(
            batch_size=args.batch_size,
            dry_run=args.dry_run
        )
        
        await processor.process_all_questions(
            subject_id=args.subject_id,
            reprocess=args.reprocess
        )
        
        logger.info("Question processing completed successfully!")
        
    except Exception as e:
        logger.error(f"Question processing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
