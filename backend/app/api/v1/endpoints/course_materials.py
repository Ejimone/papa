from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import os
from pathlib import Path
import asyncio

from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_user, get_current_active_user
from app.core.config import settings

router = APIRouter()

# Configure upload settings for course materials
COURSE_MATERIALS_DIR = Path("uploads") / "course_materials"
COURSE_MATERIALS_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB for course materials
ALLOWED_COURSE_MATERIAL_TYPES = {
    "application/pdf",
    "text/plain",
    "application/msword", 
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/markdown",
    "text/html"
}

@router.post("/upload", response_model=Dict[str, Any])
async def upload_course_materials(
    # Required fields
    subject_id: int = Form(..., description="Subject ID for the course materials"),
    title: str = Form(..., description="Title/name for the course material"),
    
    # Optional fields
    topic_id: Optional[int] = Form(None, description="Specific topic ID"),
    description: Optional[str] = Form(None, description="Description of the materials"),
    material_type: str = Form("lecture_notes", description="Type of material"),
    tags: Optional[str] = Form(None, description="Comma-separated tags"),
    
    # File uploads
    files: List[UploadFile] = File(..., description="Course material files"),
    
    # Options
    enable_rag: bool = Form(True, description="Enable for RAG/search functionality"),
    auto_extract_questions: bool = Form(False, description="Automatically extract questions"),
    
    # Dependencies
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload course materials for RAG functionality"""
    try:
        # Validate file count and size
        if len(files) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 files allowed per upload")
        
        # Process tags
        material_tags = []
        if tags:
            material_tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Create course material directory
        material_id = str(uuid.uuid4())
        material_dir = COURSE_MATERIALS_DIR / material_id
        material_dir.mkdir(parents=True, exist_ok=True)
        
        uploaded_files = []
        processing_tasks = []
        
        for file in files:
            if not file.filename:
                continue
                
            try:
                # Validate file type
                if file.content_type not in ALLOWED_COURSE_MATERIAL_TYPES:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Invalid file type: {file.content_type}. Allowed types: {', '.join(ALLOWED_COURSE_MATERIAL_TYPES)}"
                    )
                
                # Validate file size
                contents = await file.read()
                if len(contents) > MAX_FILE_SIZE:
                    raise HTTPException(status_code=400, detail=f"File {file.filename} is too large. Maximum size: 50MB")
                
                # Generate unique filename
                file_extension = Path(file.filename).suffix
                unique_filename = f"{uuid.uuid4()}{file_extension}"
                file_path = material_dir / unique_filename
                
                # Save file
                with open(file_path, "wb") as buffer:
                    buffer.write(contents)
                
                file_info = {
                    "filename": unique_filename,
                    "original_filename": file.filename,
                    "content_type": file.content_type,
                    "size": len(contents),
                    "path": str(file_path),
                    "url": f"/uploads/course_materials/{material_id}/{unique_filename}"
                }
                uploaded_files.append(file_info)
                
                # Add processing tasks
                if enable_rag:
                    task_id = str(uuid.uuid4())
                    processing_tasks.append({
                        "task_id": task_id,
                        "type": "rag_processing",
                        "file": file_info
                    })
                    
                    background_tasks.add_task(
                        process_for_rag,
                        task_id,
                        file_path,
                        {
                            "material_id": material_id,
                            "subject_id": subject_id,
                            "topic_id": topic_id,
                            "title": title,
                            "description": description,
                            "tags": material_tags,
                            "uploaded_by": current_user.id
                        }
                    )
                
                if auto_extract_questions:
                    task_id = str(uuid.uuid4())
                    processing_tasks.append({
                        "task_id": task_id,
                        "type": "question_extraction",
                        "file": file_info
                    })
                    
                    background_tasks.add_task(
                        extract_questions_from_material,
                        task_id,
                        file_path,
                        subject_id,
                        current_user.id
                    )
                
            except Exception as e:
                # Log error but continue with other files
                print(f"Error processing file {file.filename}: {e}")
                continue
        
        # TODO: Store course material metadata in database
        material_record = {
            "id": material_id,
            "title": title,
            "description": description,
            "material_type": material_type,
            "subject_id": subject_id,
            "topic_id": topic_id,
            "tags": material_tags,
            "uploaded_by": current_user.id,
            "files": uploaded_files,
            "enable_rag": enable_rag,
            "auto_extract_questions": auto_extract_questions
        }
        
        return {
            "material_id": material_id,
            "material": material_record,
            "uploaded_files": uploaded_files,
            "processing_tasks": processing_tasks,
            "message": f"Uploaded {len(uploaded_files)} files successfully. " +
                      (f"{len(processing_tasks)} processing tasks queued." if processing_tasks else "")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/materials", response_model=List[Dict[str, Any]])
async def get_course_materials(
    subject_id: Optional[int] = None,
    topic_id: Optional[int] = None,
    material_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get course materials with optional filtering"""
    try:
        # TODO: Implement database query for course materials
        # For now, return empty list as placeholder
        return []
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/materials/{material_id}", response_model=Dict[str, Any])
async def get_course_material(
    material_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific course material by ID"""
    try:
        # TODO: Implement database query for specific material
        material_dir = COURSE_MATERIALS_DIR / material_id
        if not material_dir.exists():
            raise HTTPException(status_code=404, detail="Course material not found")
        
        # Return basic info for now
        return {
            "id": material_id,
            "status": "exists",
            "path": str(material_dir)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/materials/{material_id}/query", response_model=Dict[str, Any])
async def query_course_material(
    material_id: str,
    query: str = Form(..., description="Query to search in the course material"),
    max_results: int = Form(5, description="Maximum number of results to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Query course materials using RAG"""
    try:
        # TODO: Implement RAG query functionality
        # This would search through processed course materials
        
        return {
            "query": query,
            "material_id": material_id,
            "results": [],
            "message": "RAG functionality not yet implemented"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/materials/{material_id}")
async def delete_course_material(
    material_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete course material and associated files"""
    try:
        material_dir = COURSE_MATERIALS_DIR / material_id
        if not material_dir.exists():
            raise HTTPException(status_code=404, detail="Course material not found")
        
        # Delete files
        import shutil
        shutil.rmtree(material_dir)
        
        # TODO: Delete from database
        
        return {"message": "Course material deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=List[Dict[str, Any]])
async def query_course_materials(
    query: str,
    subject_id: Optional[int] = None,
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Query course materials using RAG"""
    try:
        # Import AI services
        from app.ai.embeddings.text_embeddings import TextEmbeddingService
        from app.ai.vector_db.client import ChromaClient
        
        # Generate query embedding
        embedding_service = TextEmbeddingService()
        query_embedding = await embedding_service.create_text_embedding(query)
        
        # Query vector database
        chroma_client = ChromaClient()
        results = await chroma_client.query_similar(
            collection_name="course_materials",
            query_embedding=query_embedding,
            n_results=limit,
            metadata_filter={"subject_id": subject_id} if subject_id else None
        )
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Background processing functions
async def process_for_rag(task_id: str, file_path: Path, metadata: Dict[str, Any]):
    """Background task to process course materials for RAG functionality"""
    try:
        print(f"Processing file for RAG: {file_path}")
        
        # Import AI services
        from app.ai.processing.pdf_processor import PDFProcessor
        from app.ai.processing.text_processor import TextProcessor
        from app.ai.embeddings.text_embeddings import TextEmbeddingService
        from app.ai.vector_db.client import ChromaClient
        from app.core.database import async_session
        
        # Extract text from file
        extracted_text = ""
        file_suffix = file_path.suffix.lower()
        
        if file_suffix == '.pdf':
            pdf_processor = PDFProcessor()
            with open(file_path, 'rb') as f:
                pdf_bytes = f.read()
            extracted_text, entities = await pdf_processor.process_pdf_from_bytes(pdf_bytes)
        elif file_suffix in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                extracted_text = f.read()
        elif file_suffix in ['.doc', '.docx']:
            # TODO: Implement Word document processing
            print(f"Word document processing not implemented for {file_path}")
            return
        else:
            print(f"Unsupported file type: {file_suffix}")
            return
        
        # Process text into chunks for RAG
        text_processor = TextProcessor()
        chunks = await text_processor.chunk_text_for_rag(extracted_text)
        
        # Generate embeddings for each chunk
        embedding_service = TextEmbeddingService()
        
        # Store in vector database
        chroma_client = ChromaClient()
        
        for i, chunk in enumerate(chunks):
            # Create embedding
            embedding = await embedding_service.create_text_embedding(chunk.text)
            
            # Prepare metadata for vector store
            vector_metadata = {
                "material_id": metadata["material_id"],
                "subject_id": metadata["subject_id"],
                "topic_id": metadata.get("topic_id"),
                "title": metadata["title"],
                "chunk_index": i,
                "chunk_type": chunk.chunk_type,
                "file_path": str(file_path),
                "uploaded_by": metadata["uploaded_by"],
                "tags": ",".join(metadata.get("tags", [])),
            }
            
            # Store in vector database
            await chroma_client.add_document(
                collection_name="course_materials",
                document_id=f"{metadata['material_id']}_{i}",
                embedding=embedding,
                metadata=vector_metadata,
                text=chunk.text
            )
        
        print(f"Successfully processed {len(chunks)} chunks for RAG from {file_path}")
        
        # TODO: Store course material record in database
        async with async_session() as db:
            # Create CourseMaterial record
            pass
        
    except Exception as e:
        print(f"Error processing file for RAG: {e}")

async def extract_questions_from_material(task_id: str, file_path: Path, subject_id: int, user_id: int):
    """Background task to extract questions from course materials"""
    try:
        print(f"Extracting questions from course material: {file_path}")
        
        # Import AI services
        from app.ai.llm.gemini_client import GeminiClient
        from app.ai.processing.pdf_processor import PDFProcessor
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
        elif file_suffix in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                extracted_text = f.read()
        else:
            print(f"Unsupported file type for question extraction: {file_suffix}")
            return
        
        # Use AI to extract questions from text
        gemini_client = GeminiClient()
        questions_data = await gemini_client.extract_questions_from_text(
            extracted_text, 
            subject_id=subject_id
        )
        
        # Create questions in database
        async with async_session() as db:
            question_service = QuestionService(db)
            
            created_questions = []
            for question_data in questions_data:
                try:
                    # Add user and subject context
                    question_data['created_by'] = user_id
                    question_data['subject_id'] = subject_id
                    
                    # Create question
                    question = await question_service.create_from_dict(question_data)
                    created_questions.append(question)
                    
                except Exception as e:
                    print(f"Error creating question: {e}")
                    continue
        
        print(f"Successfully extracted {len(created_questions)} questions from course material")
        
    except Exception as e:
        print(f"Error extracting questions from course material: {e}")
