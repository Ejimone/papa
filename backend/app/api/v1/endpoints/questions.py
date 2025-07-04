from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import json
from pathlib import Path

from app.core.database import get_db
from app.models.user import User
from app.schemas.question import (
    QuestionCreate, QuestionRead, QuestionUpdate, QuestionFilter, QuestionSearch,
    QuestionMetadataCreate, QuestionMetadataRead, QuestionMetadataUpdate,
    ExplanationCreate, ExplanationRead, HintCreate, HintRead,
    QuestionPublic, QuestionResponse, QuestionBulkCreate, QuestionSearchResponse
)
from app.api.deps import get_current_user, get_current_active_user
from app.services.question_service import QuestionService

router = APIRouter()

@router.get("/", response_model=List[QuestionRead])
async def get_questions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    subject_id: Optional[int] = Query(None, description="Filter by subject ID"),
    topic_id: Optional[int] = Query(None, description="Filter by topic ID"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty level"),
    question_type: Optional[str] = Query(None, description="Filter by question type"),
    verified_only: bool = Query(False, description="Show only verified questions"),
    db: AsyncSession = Depends(get_db)
):
    """Get questions with optional filtering"""
    try:
        service = QuestionService(db)
        
        # Build filters
        filters = QuestionFilter(
            subject_ids=[subject_id] if subject_id else None,
            topic_ids=[topic_id] if topic_id else None,
            difficulty_levels=[difficulty] if difficulty else None,
            question_types=[question_type] if question_type else None,
            is_verified=verified_only if verified_only else None
        )
        
        questions = await service.get_filtered(filters, skip, limit)
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=QuestionSearchResponse)
async def search_questions(
    q: str = Query(..., description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    subject_ids: Optional[List[int]] = Query(None, description="Filter by subject IDs"),
    difficulty_levels: Optional[List[str]] = Query(None, description="Filter by difficulty levels"),
    verified_only: bool = Query(False, description="Show only verified questions"),
    db: AsyncSession = Depends(get_db)
):
    """Search questions with text search and filters"""
    try:
        service = QuestionService(db)
        
        # Build search parameters
        filters = QuestionFilter(
            subject_ids=subject_ids,
            difficulty_levels=difficulty_levels,
            is_verified=verified_only if verified_only else None
        )
        
        search_params = QuestionSearch(
            query=q,
            filters=filters,
            offset=skip,
            limit=limit
        )
        
        result = await service.search_questions(search_params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    include_details: bool = Query(True, description="Include metadata, images, explanations, hints"),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific question by ID"""
    try:
        service = QuestionService(db)
        
        if include_details:
            question = await service.get_with_details(question_id)
        else:
            question = await service.get(question_id)
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        return question
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{question_id}/public", response_model=QuestionPublic)
async def get_question_public(
    question_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get question in public format (without answer for practice mode)"""
    try:
        service = QuestionService(db)
        question = await service.get_with_details(question_id)
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Convert to public format (without answer)
        return QuestionPublic(
            id=question.id,
            title=question.title,
            content=question.content,
            question_type=question.question_type,
            difficulty_level=question.difficulty_level,
            points=question.points,
            subject_id=question.subject_id,
            topic_id=question.topic_id,
            images=question.images or [],
            hints=question.hints or [],
            created_at=question.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=QuestionRead)
async def create_question(
    question_data: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new question"""
    try:
        service = QuestionService(db)
        question = await service.create(question_data)
        return question
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk", response_model=Dict[str, Any])
async def create_questions_bulk(
    questions_data: QuestionBulkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create multiple questions in bulk"""
    try:
        service = QuestionService(db)
        created_questions = []
        failed_questions = []
        
        for question_data in questions_data.questions:
            try:
                question = await service.create(question_data)
                created_questions.append(question)
            except Exception as e:
                failed_questions.append({
                    "question_data": question_data.dict(),
                    "error": str(e)
                })
        
        return {
            "created_count": len(created_questions),
            "failed_count": len(failed_questions),
            "created_questions": created_questions,
            "failed_questions": failed_questions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{question_id}", response_model=QuestionRead)
async def update_question(
    question_id: int,
    question_data: QuestionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a question"""
    try:
        service = QuestionService(db)
        question = await service.update(question_id, question_data)
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        return question
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{question_id}")
async def delete_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a question"""
    try:
        service = QuestionService(db)
        success = await service.delete(question_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Question not found")
        
        return {"message": "Question deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subject/{subject_id}", response_model=List[QuestionRead])
async def get_questions_by_subject(
    subject_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get questions by subject"""
    try:
        service = QuestionService(db)
        questions = await service.get_by_subject(subject_id, skip, limit)
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/topic/{topic_id}", response_model=List[QuestionRead])
async def get_questions_by_topic(
    topic_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get questions by topic"""
    try:
        service = QuestionService(db)
        questions = await service.get_by_topic(topic_id, skip, limit)
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/random", response_model=List[QuestionPublic])
async def get_random_questions(
    count: int = Query(10, ge=1, le=50, description="Number of random questions"),
    subject_ids: Optional[List[int]] = Query(None, description="Filter by subject IDs"),
    difficulty_levels: Optional[List[str]] = Query(None, description="Filter by difficulty levels"),
    question_types: Optional[List[str]] = Query(None, description="Filter by question types"),
    db: AsyncSession = Depends(get_db)
):
    """Get random questions for practice"""
    try:
        service = QuestionService(db)
        
        filters = None
        if subject_ids or difficulty_levels or question_types:
            filters = QuestionFilter(
                subject_ids=subject_ids,
                difficulty_levels=difficulty_levels,
                question_types=question_types
            )
        
        questions = await service.get_random_questions(count, filters)
        
        # Convert to public format
        public_questions = []
        for question in questions:
            public_questions.append(QuestionPublic(
                id=question.id,
                title=question.title,
                content=question.content,
                question_type=question.question_type,
                difficulty_level=question.difficulty_level,
                points=question.points,
                subject_id=question.subject_id,
                topic_id=question.topic_id,
                images=question.images or [],
                hints=question.hints or [],
                created_at=question.created_at
            ))
        
        return public_questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{question_id}/similar", response_model=List[QuestionRead])
async def get_similar_questions(
    question_id: int,
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Get similar questions"""
    try:
        service = QuestionService(db)
        questions = await service.get_similar_questions(question_id, limit)
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Question metadata endpoints
@router.post("/{question_id}/metadata", response_model=QuestionMetadataRead)
async def add_question_metadata(
    question_id: int,
    metadata_data: QuestionMetadataCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add metadata to a question"""
    try:
        service = QuestionService(db)
        metadata = await service.add_metadata(question_id, metadata_data)
        return metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Explanation endpoints
@router.post("/{question_id}/explanations", response_model=ExplanationRead)
async def add_explanation(
    question_id: int,
    explanation_data: ExplanationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add an explanation to a question"""
    try:
        service = QuestionService(db)
        explanation = await service.add_explanation(question_id, explanation_data)
        return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Hint endpoints
@router.post("/{question_id}/hints", response_model=HintRead)
async def add_hint(
    question_id: int,
    hint_data: HintCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a hint to a question"""
    try:
        service = QuestionService(db)
        hint = await service.add_hint(question_id, hint_data)
        return hint
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=Dict[str, Any])
async def get_question_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get question statistics"""
    try:
        service = QuestionService(db)
        stats = await service.get_question_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# File Upload endpoints for Questions
@router.post("/upload", response_model=Dict[str, Any])
async def create_question_with_files(
    # Text fields
    title: str = Form(..., description="Question title"),
    content: str = Form(..., description="Question content/text"),
    answer: Optional[str] = Form(None, description="Correct answer"),
    options: Optional[str] = Form(None, description="JSON string of options for multiple choice"),
    question_type: str = Form("multiple_choice", description="Question type"),
    difficulty_level: str = Form("intermediate", description="Difficulty level"),
    subject_id: int = Form(..., description="Subject ID"),
    topic_id: Optional[int] = Form(None, description="Topic ID"),
    source: Optional[str] = Form(None, description="Source of the question"),
    tags: Optional[str] = Form(None, description="Comma-separated tags"),
    
    # File uploads
    images: List[UploadFile] = File(default=[], description="Question images"),
    documents: List[UploadFile] = File(default=[], description="Supporting documents"),
    
    # Dependencies
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a question with file uploads (images and documents)"""
    try:
        # Process options if provided
        question_options = None
        if options:
            try:
                question_options = json.loads(options)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON format for options")
        
        # Process tags
        question_tags = []
        if tags:
            question_tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Create question data
        question_data = QuestionCreate(
            title=title,
            content=content,
            answer=answer,
            options=question_options,
            question_type=question_type,
            difficulty_level=difficulty_level,
            subject_id=subject_id,
            topic_id=topic_id,
            metadata=QuestionMetadataCreate(
                source=source,
                tags=question_tags
            ) if source or question_tags else None
        )
        
        # Create the question first
        service = QuestionService(db)
        question = await service.create(question_data)
        
        # Handle file uploads
        uploaded_files = {
            "images": [],
            "documents": []
        }
        
        # Upload directory configuration
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Process images
        for image_file in images:
            if image_file.filename:
                try:
                    # Validate image file
                    if not image_file.content_type.startswith('image/'):
                        continue
                    
                    # Generate unique filename
                    file_extension = Path(image_file.filename).suffix
                    unique_filename = f"{uuid.uuid4()}{file_extension}"
                    
                    # Create question-specific directory
                    question_dir = upload_dir / "questions" / str(question.id)
                    question_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Save image file
                    image_path = question_dir / unique_filename
                    contents = await image_file.read()
                    
                    with open(image_path, "wb") as buffer:
                        buffer.write(contents)
                    
                    # Store image info
                    image_info = {
                        "filename": unique_filename,
                        "original_filename": image_file.filename,
                        "content_type": image_file.content_type,
                        "size": len(contents),
                        "path": str(image_path),
                        "url": f"/uploads/questions/{question.id}/{unique_filename}"
                    }
                    uploaded_files["images"].append(image_info)
                    
                    # Add background task for AI processing
                    background_tasks.add_task(
                        process_question_image,
                        question.id,
                        image_path,
                        image_info
                    )
                    
                except Exception as e:
                    # Log error but continue with other files
                    print(f"Error processing image {image_file.filename}: {e}")
        
        # Process documents
        for doc_file in documents:
            if doc_file.filename:
                try:
                    # Validate document file
                    allowed_types = [
                        'application/pdf',
                        'text/plain',
                        'application/msword',
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    ]
                    if doc_file.content_type not in allowed_types:
                        continue
                    
                    # Generate unique filename
                    file_extension = Path(doc_file.filename).suffix
                    unique_filename = f"{uuid.uuid4()}{file_extension}"
                    
                    # Create question-specific directory
                    question_dir = upload_dir / "questions" / str(question.id)
                    question_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Save document file
                    doc_path = question_dir / unique_filename
                    contents = await doc_file.read()
                    
                    with open(doc_path, "wb") as buffer:
                        buffer.write(contents)
                    
                    # Store document info
                    doc_info = {
                        "filename": unique_filename,
                        "original_filename": doc_file.filename,
                        "content_type": doc_file.content_type,
                        "size": len(contents),
                        "path": str(doc_path),
                        "url": f"/uploads/questions/{question.id}/{unique_filename}"
                    }
                    uploaded_files["documents"].append(doc_info)
                    
                    # Add background task for document processing
                    background_tasks.add_task(
                        process_question_document,
                        question.id,
                        doc_path,
                        doc_info
                    )
                    
                except Exception as e:
                    # Log error but continue with other files
                    print(f"Error processing document {doc_file.filename}: {e}")
        
        return {
            "question": question,
            "uploaded_files": uploaded_files,
            "message": "Question created successfully. Files are being processed in the background."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-batch", response_model=Dict[str, Any])
async def upload_questions_batch(
    files: List[UploadFile] = File(..., description="PDF or image files containing questions"),
    subject_id: int = Form(..., description="Subject ID for all questions"),
    auto_process: bool = Form(True, description="Automatically process files with AI"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload multiple files to extract questions in batch"""
    try:
        # Validate file count
        if len(files) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 files allowed per batch")
        
        uploaded_files = []
        processing_tasks = []
        
        # Upload directory configuration
        upload_dir = Path("uploads") / "batch_processing"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        for file in files:
            if not file.filename:
                continue
                
            try:
                # Validate file type
                allowed_types = [
                    'application/pdf',
                    'image/jpeg',
                    'image/png',
                    'image/gif',
                    'image/webp'
                ]
                if file.content_type not in allowed_types:
                    continue
                
                # Generate unique filename
                file_extension = Path(file.filename).suffix
                unique_filename = f"{uuid.uuid4()}{file_extension}"
                
                # Save file
                file_path = upload_dir / unique_filename
                contents = await file.read()
                
                with open(file_path, "wb") as buffer:
                    buffer.write(contents)
                
                file_info = {
                    "filename": unique_filename,
                    "original_filename": file.filename,
                    "content_type": file.content_type,
                    "size": len(contents),
                    "path": str(file_path),
                    "status": "uploaded"
                }
                uploaded_files.append(file_info)
                
                # Add to processing queue if auto_process is enabled
                if auto_process:
                    task_id = str(uuid.uuid4())
                    processing_tasks.append({
                        "task_id": task_id,
                        "file": file_info,
                        "subject_id": subject_id
                    })
                    
                    background_tasks.add_task(
                        process_file_for_questions,
                        task_id,
                        file_path,
                        subject_id,
                        current_user.id
                    )
                
            except Exception as e:
                print(f"Error processing file {file.filename}: {e}")
        
        return {
            "uploaded_count": len(uploaded_files),
            "files": uploaded_files,
            "processing_tasks": processing_tasks,
            "message": f"Uploaded {len(uploaded_files)} files successfully. " + 
                      (f"{len(processing_tasks)} files queued for processing." if auto_process else "")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Background task functions
async def process_question_image(question_id: int, image_path: Path, image_info: Dict):
    """Background task to process question images with AI"""
    try:
        print(f"Processing image for question {question_id}: {image_info['original_filename']}")
        
        # Import AI services
        from app.ai.processing.image_processor import ImageProcessor
        from app.ai.embeddings.image_embeddings import ImageEmbeddingService
        from app.core.database import async_session
        
        # Process image with OCR
        image_processor = ImageProcessor()
        extracted_text = await image_processor.extract_text_from_image(str(image_path))
        
        # Generate embeddings
        embedding_service = ImageEmbeddingService()
        embeddings = await embedding_service.create_image_embedding(str(image_path))
        
        # Store results in database
        async with async_session() as db:
            # TODO: Update QuestionImage model with extracted text and embeddings
            pass
        
        print(f"Successfully processed image for question {question_id}")
        
    except Exception as e:
        print(f"Error processing image for question {question_id}: {e}")

async def process_question_document(question_id: int, doc_path: Path, doc_info: Dict):
    """Background task to process question documents"""
    try:
        print(f"Processing document for question {question_id}: {doc_info['original_filename']}")
        
        # Import AI services
        from app.ai.processing.pdf_processor import PDFProcessor
        from app.ai.processing.text_processor import TextProcessor
        from app.ai.embeddings.text_embeddings import TextEmbeddingService
        from app.core.database import async_session
        
        # Extract text from document
        if doc_info['content_type'] == 'application/pdf':
            pdf_processor = PDFProcessor()
            with open(doc_path, 'rb') as f:
                pdf_bytes = f.read()
            extracted_text, entities = await pdf_processor.process_pdf_from_bytes(pdf_bytes)
        else:
            # Handle text files
            with open(doc_path, 'r', encoding='utf-8') as f:
                extracted_text = f.read()
            entities = []
        
        # Process text with AI
        text_processor = TextProcessor()
        analysis_result = await text_processor.analyze_text(extracted_text)
        
        # Generate embeddings
        embedding_service = TextEmbeddingService()
        embeddings = await embedding_service.create_text_embedding(extracted_text)
        
        # Store processed content in database
        async with async_session() as db:
            # TODO: Update question with extracted content and embeddings
            pass
        
        print(f"Successfully processed document for question {question_id}")
        
    except Exception as e:
        print(f"Error processing document for question {question_id}: {e}")

async def process_file_for_questions(task_id: str, file_path: Path, subject_id: int, user_id: int):
    """Background task to extract questions from uploaded files"""
    try:
        print(f"Processing file for question extraction: {file_path}")
        
        # Import AI services
        from app.ai.llm.gemini_client import GeminiClient
        from app.ai.processing.pdf_processor import PDFProcessor
        from app.ai.processing.image_processor import ImageProcessor
        from app.services.question_service import QuestionService
        from app.core.database import async_session
        
        # Extract text from file
        extracted_text = ""
        file_suffix = file_path.suffix.lower()
        
        if file_suffix == '.pdf':
            pdf_processor = PDFProcessor()
            with open(file_path, 'rb') as f:
                pdf_bytes = f.read()
            extracted_text, _ = await pdf_processor.process_pdf_from_bytes(pdf_bytes)
        elif file_suffix in ['.jpg', '.jpeg', '.png', '.gif']:
            image_processor = ImageProcessor()
            extracted_text = await image_processor.extract_text_from_image(str(file_path))
        else:
            # Handle text files
            with open(file_path, 'r', encoding='utf-8') as f:
                extracted_text = f.read()
        
        # Use AI to extract questions from text
        gemini_client = GeminiClient()
        questions_data = await gemini_client.extract_questions_from_text(
            extracted_text, 
            subject_id=subject_id
        )
        
        # Create questions in database
        async with async_session() as db:
            question_service = QuestionService(db)
            
            for question_data in questions_data:
                try:
                    # Add user and subject context
                    question_data['created_by'] = user_id
                    question_data['subject_id'] = subject_id
                    
                    # Create question
                    await question_service.create_from_dict(question_data)
                    
                except Exception as e:
                    print(f"Error creating question: {e}")
                    continue
        
        print(f"Successfully extracted {len(questions_data)} questions from file")
        
    except Exception as e:
        print(f"Error processing file {file_path} for questions: {e}")
