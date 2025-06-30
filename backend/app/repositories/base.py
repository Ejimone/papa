from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete
from app.models.base import Base # Using our custom Base with id, created_at, updated_at

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        Base class that can be extend by other action repositories.

        :param model: SQLAlchemy model class
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        statement = select(self.model).where(self.model.id == id)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        statement = select(self.model).offset(skip).limit(limit)
        result = await db.execute(statement)
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        if isinstance(obj_in, dict):
            obj_in_data = obj_in
        else:
            obj_in_data = obj_in.model_dump()

        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.flush() # Use flush to get ID before commit if needed, commit is handled by get_db dependency
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[ModelType]:
        obj = await self.get(db, id=id)
        if obj:
            await db.delete(obj)
            await db.flush()
        return obj # Return the deleted object or None if not found

    async def get_by_attribute(
        self, db: AsyncSession, *, attribute: str, value: Any
    ) -> Optional[ModelType]:
        """
        Get a single object by a specific attribute and its value.
        """
        statement = select(self.model).where(getattr(self.model, attribute) == value)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def get_multi_by_attribute(
        self, db: AsyncSession, *, attribute: str, value: Any, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple objects by a specific attribute and its value.
        """
        statement = select(self.model).where(getattr(self.model, attribute) == value).offset(skip).limit(limit)
        result = await db.execute(statement)
        return result.scalars().all()
