"""
Module for specific Banco Central de Venezuela rate controller operations.
"""
import logging
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import Currency, TradeType
from app.errors import RegisterNotFoundError
from app.database.models import BCVRateSQLModel
from app.controllers.base_controller import AsyncBaseController
from app.schemas.bcv_response_schemas import (
    BCVCurrencyCreate,
    BCVCurrencyUpdate,
    BCVCurrencyResponse,
    BCVCurrencyListResponse
)

class BCVController(AsyncBaseController[BCVRateSQLModel, BCVCurrencyCreate, BCVCurrencyUpdate, BCVCurrencyResponse]):
    """Controller for managing official exchange rates from Banco Central de Venezuela."""

    def __init__(self, session: AsyncSession):
        """Initialize the BCV controller with session context.

        Args:
            session (AsyncSession): Asynchronous database session.
        """
        super().__init__(model=BCVRateSQLModel, session=session)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.create_model = BCVCurrencyCreate
        self.update_model = BCVCurrencyUpdate
        self.response_model = BCVCurrencyResponse

    @staticmethod
    def _build_list_response(rates: List[BCVRateSQLModel], total: int) -> BCVCurrencyListResponse:
        """Construct a paginated and validated currency list schema.

        Args:
            rates (List[BCVRateSQLModel]): List of database rate objects.
            total (int): Global total records matching criteria.

        Returns:
            BCVCurrencyListResponse: Structured API list payload.
        """
        return BCVCurrencyListResponse(
            currencies=[BCVCurrencyResponse.model_validate(rate.model_dump()) for rate in rates],
            count=total
        )

    async def _get_or_raise(self, rate_id: UUID) -> BCVRateSQLModel:
        """Retrieve a rate or raise exception if not found.

        Args:
            rate_id (UUID): Database identifier.

        Returns:
            BCVRateSQLModel: Database instance object.

        Raises:
            RegisterNotFoundError: If no record matches the given identity.
        """
        obj = await self.get(id=rate_id)
        if obj is None:
            raise RegisterNotFoundError(
                message="Rate record not found on database",
                details=f"ID object rate: {rate_id}"
            )
        return obj

    async def register_rate(self, rate: BCVCurrencyCreate) -> BCVCurrencyResponse:
        """Create a new BCV rate record.

        Args:
            rate (BCVCurrencyCreate): Creation schema data.

        Returns:
            BCVCurrencyResponse: Output response validation schema.
        """
        new_rate = await self.create(obj_in=rate)
        return BCVCurrencyResponse.model_validate(new_rate.model_dump())

    async def get_register_by_id(self, register_id: UUID) -> BCVCurrencyResponse:
        """Retrieve validated rate by unique identifier.

        Args:
            register_id (UUID): Database token key.

        Returns:
            BCVCurrencyResponse: Output validation model data.
        """
        register = await self._get_or_raise(register_id)
        return BCVCurrencyResponse.model_validate(register.model_dump())
    
    async def get_last_register_by_currency(self, currency: Currency, trade_type: TradeType = TradeType.SELL) -> Optional[BCVCurrencyResponse]:
        """
        Fetch the most recent rate for a specific currency and trade type.

        Args:
            currency (Currency): Target currency enumeration.
            trade_type (TradeType): Trade operation type.

        Returns:
            Optional[BCVCurrencyResponse]: The most recent rate for the specified currency and trade type, or None if not found.
        """
        where_clause = [
            BCVRateSQLModel.currency == currency,
            BCVRateSQLModel.trade_type == trade_type
        ]
        last_register = await self.get_last_register_with_conditions(where_clause=where_clause, sort_by_attribute="date")
        if last_register is None:
            return None
        return BCVCurrencyResponse.model_validate(last_register.model_dump())

    async def update_register_rate(self, register_id: UUID, rate: BCVCurrencyUpdate) -> BCVCurrencyResponse:
        """Modify fields on an existing record.

        Args:
            register_id (UUID): Target record key.
            rate (BCVCurrencyUpdate): Input field parameters.

        Returns:
            BCVCurrencyResponse: Documented updated view representation.
        """
        db_obj = await self._get_or_raise(register_id)
        updated_obj = await self.update(db_obj=db_obj, obj_in=rate)
        return BCVCurrencyResponse.model_validate(updated_obj.model_dump())

    async def delete_register_rate(self, register_id: UUID) -> BCVCurrencyResponse:
        """Remove record execution task.

        Args:
            register_id (UUID): Record identity target.

        Returns:
            BCVCurrencyResponse: Instance view of deleted dataset.
        """
        db_obj = await self._get_or_raise(register_id)
        await self.remove(id=register_id)
        return BCVCurrencyResponse.model_validate(db_obj.model_dump())

    async def get_registers_by_currency(
        self, 
        currency: Currency, 
        trade_type: TradeType = TradeType.SELL, 
        skip: int = 0, 
        limit: int = 100
    ) -> BCVCurrencyListResponse:
        """Retrieve rates matching specific currency criteria with absolute total count.

        Args:
            currency (Currency): Targeted money token type.
            trade_type (TradeType): Trading market category type.
            skip (int): Pagination offsetting margin.
            limit (int): Pagination record chunk sizing allocation.

        Returns:
            BCVCurrencyListResponse: Total database records wrapper instance.
        """
        where_clause = [
            BCVRateSQLModel.currency == currency,
            BCVRateSQLModel.trade_type == trade_type
        ]
        
        count_statement = select(func.count()).select_from(BCVRateSQLModel).where(*where_clause)
        count_result = await self.session.execute(count_statement)
        total_count = count_result.scalar_one()

        rates = await self.get_multi_with_conditions(
            where_clause=where_clause,
            skip=skip,
            limit=limit,
            sort_by_attribute="date"
        )
        return self._build_list_response(rates=rates, total=total_count)

    async def get_registers_currency_by_date_range(
        self, 
        currency: Currency, 
        trade_type: TradeType = TradeType.SELL, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None, 
        skip: int = 0, 
        limit: int = 100
    ) -> BCVCurrencyListResponse:
        """Query rate metrics inside contextual timestamp periods.

        Args:
            currency (Currency): Targeted coin entity enum element.
            trade_type (TradeType): Trading classification.
            start_date (Optional[datetime]): Chronological query origin constraint.
            end_date (Optional[datetime]): Chronological query boundary constraint.
            skip (int): Pagination offset element data.
            limit (int): Pagination limits parameters.

        Returns:
            BCVCurrencyListResponse: Chronological paginated object list data.
        """
        where_clause = [
            BCVRateSQLModel.currency == currency,
            BCVRateSQLModel.trade_type == trade_type
        ]

        if start_date:
            where_clause.append(BCVRateSQLModel.date >= start_date)
        if end_date:
            where_clause.append(BCVRateSQLModel.date <= end_date)

        count_statement = select(func.count()).select_from(BCVRateSQLModel).where(*where_clause)
        count_result = await self.session.execute(count_statement)
        total_count = count_result.scalar_one()

        rates = await self.get_multi_with_conditions(
            where_clause=where_clause,
            skip=skip,
            limit=limit,
            sort_by_attribute="date"
        )
        return self._build_list_response(rates=rates, total=total_count)