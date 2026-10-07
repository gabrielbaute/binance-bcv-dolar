"""
Abstract base controller for operations common to other controllers.
"""
from uuid import UUID
from pydantic import BaseModel
from sqlmodel import func, select, SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List, Optional, Tuple, Type, Union

from app.errors import RegisterNotFoundError, DatabaseOperationError

class AsyncBaseController[
    ModelType: SQLModel,
    CreateSchemaType: BaseModel,
    UpdateSchemaType: BaseModel,
    ResponseSchemaType: BaseModel,
]:
    """
    It provides a basic implementation for interacting with the database.
    """
    def __init__(self, model: Type[ModelType], database_session: AsyncSession):
        """
        Initialize the controller with a specific SQL model.

        Args:
            model (Type[ModelType]): The associated SQLModel.
            session (AsyncSession): Database session.
        """
        self.model = model
        self.database_session = database_session

    def _validate_uuid(self, uuid_str: Union[str, UUID]) -> UUID:
        """
        Helper para validar que una ID sea en efecto de tipo UUID.

        Args:
            uuid_str (Union[str, UUID]): ID en string o UUID.

        Returns:
            UUID: ID en formato UUID.
        """
        if isinstance(uuid_str, str):
            return UUID(uuid_str)
        else:
            return uuid_str

    async def _get_or_raise(self, db_obj_id: UUID) -> ModelType:
        """
        Obtiene un registro del ModelType específico o genere una excepción.

        Args:
            db_obj_id (UUID): Identificador de clave primaria de la base de datos.

        Returns:
            ModelType: El modelo de datos de persistencia de evento.

        Raises:
            RegisterNotFoundError: Si el ID no se corresponde con ningún registro.
        """
        event_id = self._validate_uuid(db_obj_id)
        obj = await self.get(id=db_obj_id)
        if obj is None:
            raise RegisterNotFoundError(
                message="Register not found.",
                details={"detail": f"Register ID: {event_id}",}
            )
        return obj

    async def _commit_or_rollback(self) -> None:
        """
        Try committing the session, and if it fails, roll back.

        Raises:
            Exception: If the commit operation fails after a rollback attempt.
        """
        try:
            await self.database_session.commit()
        except Exception:
            await self.database_session.rollback()
            raise

    async def _update_or_rollback(self, db_obj: ModelType) -> bool:
        """
        Intenta realizar un commit con el objetivo explícito de actualizar un objeto de la base de datos.

        Args:
            db_obj (ModelType): El objeto actual en la base de datos.

        Returns:
            bool: True si la edición del campo fue exitosa.

        Raises:
            Exception: Si ocurre un error durante el commit, se lanza una excepción con el error correspondiente
            y se realiza un rollback de la sesión.
        """
        try:
            self.database_session.add(db_obj)
            await self.database_session.commit()
            return True
        except Exception:
            await self.database_session.rollback()
            raise

    async def get(self, id: UUID) -> Optional[ModelType]:
        """
        Retrieve a record by its ID.

        Args:
            id (UUID): UUID of the database object.

        Returns:
            Optional[ModelType]: The object found or None.
        """
        statement = select(self.model).where(self.model.id == id) # type: ignore
        result = await self.database_session.execute(statement)
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
        result = await self.database_session.execute(statement)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by_attribute: str = "registered_at"
    ) -> Tuple[List[ModelType], int]:
        """
        Devuelve una lista de registros de la base de datos con paginación y el conteo total.

        Args:
            skip (int): Registros a omitir para la paginación.
            limit (int): Número máximo de registros a devolver.
            sort_by_attribute (str): Nombre del atributo por el cual ordenar los registros en orden descendente.

        Returns:
            Tuple[List[ModelType], int]: Tupla con la lista de objetos obtenidos y el total de registros en la tabla.

        Raises:
            DatabaseOperationError: Si ocurre un error al consultar la base de datos.
        """
        return await self.get_multi_with_conditions(
            where_clause=[],
            skip=skip,
            limit=limit,
            sort_by_attribute=sort_by_attribute
        )

    async def get_multi_with_conditions(
        self,
        where_clause: List[Any],
        skip: int = 0,
        limit: int = 100,
        sort_by_attribute: str = "date"
    ) -> Tuple[List[ModelType], int]:
        """
        Devuelve una lista de registros que cumplen con las condiciones y el conteo total de registros que coinciden.

        Args:
            where_clause (List[Any]): Lista de expresiones condicionales de SQLModel para filtrar los registros.
            skip (int): Número de registros a omitir para la paginación.
            limit (int): Número máximo de registros a devolver.
            sort_by_attribute (str): Nombre del atributo por el cual ordenar los registros en orden descendente.

        Returns:
            Tuple[List[ModelType], int]: Tupla que contiene la lista de objetos paginados y el conteo total sin paginar.

        Raises:
            DatabaseOperationError: Si ocurre un error al consultar la base de datos.
        """
        try:
            # 1. Consulta para el conteo total sin la paginación (offset/limit)
            count_statement = select(func.count()).select_from(self.model)
            if where_clause:
                count_statement = count_statement.where(*where_clause)

            count_result = await self.database_session.execute(count_statement)
            total_count: int = count_result.scalar_one()

            # 2. Consulta para obtener los registros paginados y ordenados
            order_column = getattr(self.model, sort_by_attribute)
            statement = select(self.model)
            if where_clause:
                statement = statement.where(*where_clause)

            statement = statement.order_by(order_column.desc()).offset(skip).limit(limit)

            result = await self.database_session.execute(statement)
            items: List[ModelType] = list(result.scalars().all())

            return items, total_count
        except Exception as e:
            raise DatabaseOperationError(
                message="Error al realizar la consulta con condiciones en la base de datos.",
                details={"error": str(e)}
            ) from e

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

        self.database_session.add(db_obj)
        await self._commit_or_rollback()
        await self.database_session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """
        Actualiza un registro existente.

        Args:
            db_obj (ModelType): El objeto actual en la base de datos.
            obj_in (UpdateSchemaType | dict[str, Any]): Contenedor de los nuevos datos.

        Returns:
            ModelType: El objeto actualizado en la base de datos.
        """
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        self.database_session.add(db_obj)
        await self._commit_or_rollback()
        await self.database_session.refresh(db_obj)
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
            await self.database_session.delete(obj)
            await self._commit_or_rollback()
        return obj
