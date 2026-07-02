"""Module for specific Binance P2P rate controller operations."""

import logging
from uuid import UUID
from datetime import datetime
from typing import List, Optional, Any
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import TradeType, FiatCurrency, BinanceAsset
from app.errors import RegisterNotFoundError
from app.database.models import BinanceRateSQLModel
from app.controllers.base_controller import AsyncBaseController
from app.schemas.binance_response_schemas import (
    BinanceCurrencyCreate,
    BinanceCurrencyUpdate,
    BinanceCurrencyResponse,
    BinanceCurrencyListResponse,
)

class BinanceController(
    AsyncBaseController[
        BinanceRateSQLModel,
        BinanceCurrencyCreate,
        BinanceCurrencyUpdate,
        BinanceCurrencyResponse,
    ]
):
    """Controller for managing P2P market rate statistics from Binance."""

    def __init__(self, session: AsyncSession):
        """Initialize the Binance controller with an asynchronous session.

        Args:
            session (AsyncSession): Asynchronous database session context.
        """
        super().__init__(model=BinanceRateSQLModel, session=session)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.create_model = BinanceCurrencyCreate
        self.update_model = BinanceCurrencyUpdate
        self.response_model = BinanceCurrencyResponse

    @staticmethod
    def _build_list_response(
        rates: List[BinanceRateSQLModel], total: int
    ) -> BinanceCurrencyListResponse:
        """Construct a paginated and validated Binance rate list response.

        Args:
            rates (List[BinanceRateSQLModel]): List of database records.
            total (int): Global count matching the filtered parameters.

        Returns:
            BinanceCurrencyListResponse: Validated response payload API model.
        """
        return BinanceCurrencyListResponse(
            currencies=[BinanceCurrencyResponse.model_validate(rate.model_dump()) for rate in rates],
            count=total,
        )

    async def _get_or_raise(self, rate_id: UUID) -> BinanceRateSQLModel:
        """Fetch a specific Binance rate record or raise an exception.

        Args:
            rate_id (UUID): Database primary key identifier.

        Returns:
            BinanceRateSQLModel: The persistent model instance.

        Raises:
            RegisterNotFoundError: If the ID does not map to any record.
        """
        obj = await self.get(id=rate_id)
        if obj is None:
            raise RegisterNotFoundError(
                message="Binance rate record not found on database",
                details=f"ID object rate: {rate_id}",
            )
        return obj

    async def register_rate(self, rate: BinanceCurrencyCreate) -> BinanceCurrencyResponse:
        """Persist a new calculated Binance P2P rate metric record.

        Args:
            rate (BinanceCurrencyCreate): Insertion validation constraints data.

        Returns:
            BinanceCurrencyResponse: Validated output serialization model.
        """
        new_rate = await self.create(obj_in=rate)
        return BinanceCurrencyResponse.model_validate(new_rate.model_dump())

    async def get_register_by_id(self, register_id: UUID) -> BinanceCurrencyResponse:
        """Look up a validated historical record entity snapshot.

        Args:
            register_id (UUID): Database key index.

        Returns:
            BinanceCurrencyResponse: Output instance visualization model.
        """
        register = await self._get_or_raise(register_id)
        return BinanceCurrencyResponse.model_validate(register.model_dump())
    
    async def get_last_register_by_pair(
        self, 
        asset: BinanceAsset, 
        fiat: FiatCurrency, 
        trade_type: TradeType = TradeType.BUY
    ) -> Optional[BinanceCurrencyResponse]:
        """
        Retrieve the most recent record for a specific asset-fiat-trade_type combination.

        Args:
            asset (BinanceAsset): Cryptocurrency token target (e.g., USDT).
            fiat (FiatCurrency): Local fiat currency token target (e.g., VES).
            trade_type (TradeType): Order book context perspective.
        Returns:
            Optional[BinanceCurrencyResponse]: The latest record if found, else None.
        """
        where_clause = [
            BinanceRateSQLModel.asset == asset,
            BinanceRateSQLModel.fiat == fiat,
            BinanceRateSQLModel.trade_type == trade_type,
        ]

        last_register = await self.get_last_register_with_conditions(
            where_clause=where_clause, sort_by_attribute="date"
        )
        if last_register is None:
            return None
        return BinanceCurrencyResponse.model_validate(last_register.model_dump())

    async def update_register_rate(
        self, register_id: UUID, rate: BinanceCurrencyUpdate
    ) -> BinanceCurrencyResponse:
        """Modify tracking variables of an existing market record.

        Args:
            register_id (UUID): Target entity primary key token.
            rate (BinanceCurrencyUpdate): Schema of values to update.

        Returns:
            BinanceCurrencyResponse: Serialized data object outcome.
        """
        db_obj = await self._get_or_raise(register_id)
        updated_obj = await self.update(db_obj=db_obj, obj_in=rate)
        return BinanceCurrencyResponse.model_validate(updated_obj.model_dump())

    async def delete_register_rate(self, register_id: UUID) -> BinanceCurrencyResponse:
        """Erase a tracking data row inside a session execution block.

        Args:
            register_id (UUID): Unique target identifier.

        Returns:
            BinanceCurrencyResponse: Copy snapshot representation of dropped element.
        """
        db_obj = await self._get_or_raise(register_id)
        await self.remove(id=register_id)
        return BinanceCurrencyResponse.model_validate(db_obj.model_dump())

    async def get_registers_by_pair(
        self,
        asset: BinanceAsset,
        fiat: FiatCurrency,
        trade_type: TradeType = TradeType.BUY,
        skip: int = 0,
        limit: int = 100,
    ) -> BinanceCurrencyListResponse:
        """Fetch tracking records based on asset, local fiat and trade perspective.

        Args:
            asset (BinanceAsset): Cryptocurrency token target (e.g., USDT).
            fiat (FiatCurrency): Target fiat token target (e.g., VES).
            trade_type (TradeType): P2P operation perspective.
            skip (int): Pagination offset value.
            limit (int): Size of slice records chunk.

        Returns:
            BinanceCurrencyListResponse: Paginated results along with true total count.
        """
        where_clause = [
            BinanceRateSQLModel.asset == asset,
            BinanceRateSQLModel.fiat == fiat,
            BinanceRateSQLModel.trade_type == trade_type,
        ]

        count_statement = (
            select(func.count()).select_from(BinanceRateSQLModel).where(*where_clause)
        )
        count_result = await self.session.execute(count_statement)
        total_count = count_result.scalar_one()

        rates = await self.get_multi_with_conditions(
            where_clause=where_clause,
            skip=skip,
            limit=limit,
            sort_by_attribute="date",
        )
        return self._build_list_response(rates=rates, total=total_count)

    async def get_registers_by_date_range(
        self,
        asset: BinanceAsset,
        fiat: FiatCurrency,
        trade_type: TradeType = TradeType.BUY,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> BinanceCurrencyListResponse:
        """Query metrics bounded inside historical chronological timestamps.

        Args:
            asset (BinanceAsset): Cryptocurrency token target (e.g., USDT).
            fiat (FiatCurrency): Local fiat currency token target (e.g., VES).
            trade_type (TradeType): Order book context perspective.
            start_date (Optional[datetime]): From point parameter filter.
            end_date (Optional[datetime]): Until point parameter filter.
            skip (int): Pagination offset value.
            limit (int): Limit parameters allocation.

        Returns:
            BinanceCurrencyListResponse: Ordered records context wrapper payload.
        """
        where_clause = [
            BinanceRateSQLModel.asset == asset,
            BinanceRateSQLModel.fiat == fiat,
            BinanceRateSQLModel.trade_type == trade_type,
        ]

        if start_date:
            where_clause.append(BinanceRateSQLModel.date >= start_date)
        if end_date:
            where_clause.append(BinanceRateSQLModel.date <= end_date)

        count_statement = (
            select(func.count()).select_from(BinanceRateSQLModel).where(*where_clause)
        )
        count_result = await self.session.execute(count_statement)
        total_count = count_result.scalar_one()

        rates = await self.get_multi_with_conditions(
            where_clause=where_clause,
            skip=skip,
            limit=limit,
            sort_by_attribute="date",
        )
        return self._build_list_response(rates=rates, total=total_count)