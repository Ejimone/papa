from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
import os
import uuid
from pathlib import Path

from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_active_user
from app.core.config import settings

router = APIRouter()

# Configure upload settings
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_DOC_TYPES = {"application/pdf", "text/plain", "application/msword"}

@router.post("/image", response_model=Dict[str, Any])
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload an image file"""
    try:
        # Validate file type
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"
            )
        
        # Validate file size
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        
        # Generate unique filename
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / "images" / unique_filename
        file_path.parent.mkdir(exist_ok=True)
        
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
        
        # Return file info
        return {
            "filename": unique_filename,
            "original_filename": file.filename,
            "content_type": file.content_type,
            "size": len(contents),
            "url": f"/uploads/images/{unique_filename}",
            "uploaded_by": current_user.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/document", response_model=Dict[str, Any])
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a document file (PDF, Word, etc.)"""
    try:
        # Validate file type
        if file.content_type not in ALLOWED_DOC_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_DOC_TYPES)}"
            )
        
        # Validate file size
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        
        # Generate unique filename
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / "documents" / unique_filename
        file_path.parent.mkdir(exist_ok=True)
        
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
        
        # Return file info
        return {
            "filename": unique_filename,
            "original_filename": file.filename,
            "content_type": file.content_type,
            "size": len(contents),
            "url": f"/uploads/documents/{unique_filename}",
            "uploaded_by": current_user.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/multiple", response_model=List[Dict[str, Any]])
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload multiple files at once"""
    try:
        if len(files) > 10:  # Limit to 10 files
            raise HTTPException(status_code=400, detail="Too many files. Maximum 10 files allowed.")
        
        uploaded_files = []
        
        for file in files:
            # Determine file type and validate
            if file.content_type in ALLOWED_IMAGE_TYPES:
                file_type = "image"
                upload_subdir = "images"
            elif file.content_type in ALLOWED_DOC_TYPES:
                file_type = "document"
                upload_subdir = "documents"
            else:
                continue  # Skip invalid files
            
            # Validate file size
            contents = await file.read()
            if len(contents) > MAX_FILE_SIZE:
                continue  # Skip large files
            
            # Generate unique filename
            if not file.filename:
                continue  # Skip files without names
            file_extension = Path(file.filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = UPLOAD_DIR / upload_subdir / unique_filename
            file_path.parent.mkdir(exist_ok=True)
            
            # Save file
            with open(file_path, "wb") as buffer:
                buffer.write(contents)
            
            uploaded_files.append({
                "filename": unique_filename,
                "original_filename": file.filename,
                "content_type": file.content_type,
                "size": len(contents),
                "url": f"/uploads/{upload_subdir}/{unique_filename}",
                "type": file_type,
                "uploaded_by": current_user.id
            })
        
        return uploaded_files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/file/{filename}")
async def delete_file(
    filename: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete an uploaded file"""
    try:
        # Check both images and documents directories
        image_path = UPLOAD_DIR / "images" / filename
        doc_path = UPLOAD_DIR / "documents" / filename
        
        file_path = None
        if image_path.exists():
            file_path = image_path
        elif doc_path.exists():
            file_path = doc_path
        
        if not file_path:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete the file
        os.unlink(file_path)
        
        return {"message": "File deleted successfully", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/info/{filename}", response_model=Dict[str, Any])
async def get_file_info(
    filename: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get information about an uploaded file"""
    try:
        # Check both images and documents directories
        image_path = UPLOAD_DIR / "images" / filename
        doc_path = UPLOAD_DIR / "documents" / filename
        
        file_path = None
        file_type = None
        if image_path.exists():
            file_path = image_path
            file_type = "image"
        elif doc_path.exists():
            file_path = doc_path
            file_type = "document"
        
        if not file_path:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get file stats
        stat = file_path.stat()
        
        return {
            "filename": filename,
            "type": file_type,
            "size": stat.st_size,
            "created_at": stat.st_ctime,
            "modified_at": stat.st_mtime,
            "url": f"/uploads/{file_type}s/{filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 