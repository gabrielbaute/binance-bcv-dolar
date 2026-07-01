"""
Abstract base controller for operations common to other controllers.
"""
from uuid import UUID
from sqlmodel import select, SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Generic, Type, TypeVar, List, Optional, Any

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")
ResponseSchemaType = TypeVar("ResponseSchemaType")

class AsyncBaseController(Generic[ModelType, CreateSchemaType, UpdateSchemaType, ResponseSchemaType]):
    """
    It provides a basic implementation for interacting with the database.
    """
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """
        Initialize the controller with a specific SQL model.

        Args:
            model (Type[ModelType]): The associated SQLModel.
            session (AsyncSession): Database session.
        """
        self.model = model
        self.session = session

    async def _commit_or_rollback(self) -> None:
        """
        Try committing the session, and if it fails, roll back.

        Raises:
            Exception: If the commit operation fails after a rollback attempt.
        """
        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

    async def get(self, id: UUID) -> Optional[ModelType]:
        """
        Retrieve a record by its ID.

        Args:
            id (UUID): UUID of the database object.

        Returns:
            Optional[ModelType]: The object found or None.
        """
        statement = select(self.model).where(self.model.id == id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_last_register_with_conditions(
        self, 
        where_clause: List[Any],
        sort_by_attribute: str = "date"
    ) -> Optional[ModelType]:
        """
        Retrieve the last register that matches the given conditions.

        Args:
            where_clause (List[Any]): List of SQL Alchemy conditional expressions.

        Returns:
            Optional[ModelType]: The object found or None.
        """
        order_column = getattr(self.model, sort_by_attribute)
        statement = select(self.model).where(*where_clause).order_by(order_column.desc()).limit(1)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_multi(
        self, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Retrieves multiple records with pagination.

        Args:
            skip (int): Records to skip.
            limit (int): Maximum number of records to return.

        Returns:
            List[ModelType]: List of objects.
        """
        statement = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_multi_with_conditions(
        self, 
        where_clause: List[Any], 
        skip: int = 0, 
        limit: int = 100,
        sort_by_attribute: str = "date"
    ) -> List[ModelType]:
        """
        Returns a list of records that meet given conditions with chronological sort.

        Args:
            where_clause (List[Any]): List of SQL Alchemy conditional expressions.
            skip (int): Records to skip for pagination.
            limit (int): Maximum number of records to return.
            sort_by_attribute (str): Attribute name used for descending order.

        Returns:
            List[ModelType]: List of objects meeting the criteria.
        """
        order_column = getattr(self.model, sort_by_attribute)
        statement = (
            select(self.model)
            .where(*where_clause)
            .order_by(order_column.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record from a creation scheme.

        Args:
            obj_in (CreateSchemaType): Valid input data from CreateSchema.

        Returns:
            ModelType: The object created and persisted.
        """
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)

        self.session.add(db_obj)
        await self._commit_or_rollback()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(
        self, 
        db_obj: ModelType, 
        obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """
        Update an existing record.

        Args:
            db_obj (ModelType): The current object in the DB.
            obj_in (UpdateSchemaType | dict[str, Any]): New data wrapper.

        Returns:
            ModelType: The updated object.
        """
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        self.session.add(db_obj)
        await self._commit_or_rollback()
        await self.session.refresh(db_obj)
        return db_obj

    async def remove(self, id: UUID) -> Optional[ModelType]:
        """
        Deletes a record from the database.

        Args:
            id (UUID): Registration ID.

        Returns:
            Optional[ModelType]: The deleted object if found, otherwise None.
        """
        obj = await self.get(id)
        if obj:
            await self.session.delete(obj)
            await self._commit_or_rollback()
        return obj