from typing import TypeVar, Generic, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base service class with common CRUD operations"""
    
    def __init__(self, model: ModelType, db: AsyncSession):
        self.model = model
        self.db = db
    
    async def get(self, id: int) -> Optional[ModelType]:
        """Get a single record by ID"""
        try:
            result = await self.db.execute(select(self.model).where(self.model.id == id))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} with id {id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """Get multiple records with optional filtering and pagination"""
        try:
            query = select(self.model)
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key) and value is not None:
                        query = query.where(getattr(self.model, key) == value)
            
            # Apply ordering
            if order_by and hasattr(self.model, order_by):
                query = query.order_by(getattr(self.model, order_by))
            else:
                query = query.order_by(self.model.id)
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting multiple {self.model.__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record"""
        try:
            if hasattr(obj_in, 'dict'):
                obj_data = obj_in.dict()
            else:
                obj_data = obj_in
            
            db_obj = self.model(**obj_data)
            self.db.add(db_obj)
            await self.db.commit()
            await self.db.refresh(db_obj)
            return db_obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def update(self, id: int, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        """Update an existing record"""
        try:
            db_obj = await self.get(id)
            if not db_obj:
                return None
            
            if hasattr(obj_in, 'dict'):
                update_data = obj_in.dict(exclude_unset=True)
            else:
                update_data = obj_in
            
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            await self.db.commit()
            await self.db.refresh(db_obj)
            return db_obj
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating {self.model.__name__} with id {id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def delete(self, id: int) -> bool:
        """Delete a record by ID"""
        try:
            db_obj = await self.get(id)
            if not db_obj:
                return False
            
            await self.db.delete(db_obj)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting {self.model.__name__} with id {id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filtering"""
        try:
            query = select(func.count(self.model.id))
            
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key) and value is not None:
                        query = query.where(getattr(self.model, key) == value)
            
            result = await self.db.execute(query)
            return result.scalar()
        except Exception as e:
            logger.error(f"Error counting {self.model.__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error")
    
    async def exists(self, id: int) -> bool:
        """Check if a record exists by ID"""
        try:
            result = await self.db.execute(
                select(func.count(self.model.id)).where(self.model.id == id)
            )
            return result.scalar() > 0
        except Exception as e:
            logger.error(f"Error checking existence of {self.model.__name__} with id {id}: {str(e)}")
            return False
