"""Binance P2P module."""
import logging
from datetime import datetime
from statistics import median, mean
from typing import List, Optional, Dict
from httpx import AsyncClient, HTTPError
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import BinanceController
from app.enums import TradeType, BinanceAsset, FiatCurrency
from app.errors import (
    BinanceConnectionError,
    BinanceRequestError,
    DatabaseSessionError,
    DatabaseOperationError,
    RegisterNotFoundError
)
from app.schemas import (
    BinanceRequest,
    BinanceRealTimeResponse,
    BinanceCurrencyCreate,
    BinanceCurrencyResponse,
    BinanceCurrencyListResponse,
)

class BinanceService:
    """
    Binance P2P Client
    """
    def __init__(self, databasesession: Optional[AsyncSession] = None):
        self.url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        self.database_session = databasesession
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    def controller(self) -> BinanceController:
        """
        Get the BinanceController instance dynamically.

        Returns:
            BinanceController: The initialized controller instance.

        Raises:
            DatabaseSessionError: If execution context lacks an active database session.
        """
        if not self.database_session:
            self.logger.error("Database session is not provided.")
            raise DatabaseSessionError(
                message="Database session is required to initialize the controller.",
                details={"error": "No database session provided."}
            )
        return BinanceController(session=self.database_session)

    def _build_request(
        self,
        fiat: FiatCurrency,
        page: Optional[int],
        rows: Optional[int],
        trade_type: Optional[TradeType],
        asset: Optional[BinanceAsset]
    ) -> BinanceRequest:
        """
        Build the body request for Binance P2P.

        Args:
            fiat (FiatCurrency): Fiat currency.
            page (Optional[int]): Page number.
            rows (Optional[int]): Number of rows per page.
            trade_type (Optional[TradeType]): Trade type.
            asset (Optional[BinanceAsset]): Asset (USDT, BTC, etc).

        Returns:
            BinanceRequest: BinanceRequest object.

        Raises:
            BinanceRequestError: If rows parameter exceeds maximum limit of 20.
        """
        if rows and rows > 20:
            raise BinanceRequestError(
                message="Rows parameter exceeds maximum limit of 20.",
                details={"rows": rows}
            )

        return BinanceRequest(
            fiat=fiat.value,
            page=page,
            rows=rows,
            tradeType=trade_type.value if trade_type else None,
            asset=asset.value if asset else None
        )

    async def _do_request(self, req: BinanceRequest) -> dict:
        """
        Execute asynchronous HTTP POST request to Binance P2P API using AsyncClient.

        Args:
            req (BinanceRequest): BinanceRequest object.

        Returns:
            dict: Response JSON data parsed into a dictionary.

        Raises:
            BinanceConnectionError: If there was an error connecting to
            or parsing Binance P2P response.
        """
        body = req.model_dump()
        try:
            self.logger.debug("Request Binance P2P")
            async with AsyncClient(timeout=15.0) as client:
                res = await client.post(
                    self.url,
                    json=body,
                    headers={"Content-Type": "application/json"}
                )
                res.raise_for_status()
                self.logger.debug("Response Binance P2P")
                return res.json()
        except HTTPError as e:
            self.logger.error(f"Error at Binance P2P request: {e}")
            raise BinanceConnectionError(
                message="Error connecting to the Binance P2P API.",
                details={"error": str(e)}
            )
        except ValueError as e:
            self.logger.error(f"Error parsing Binance P2P response: {e}")
            raise BinanceConnectionError(
                message="Error parsing Binance P2P response.",
                details={"error": str(e)}
            )

    def _colect_prices(self, data: dict, fiat: FiatCurrency) -> Optional[List[float]]:
        """
        Collect prices from Binance P2P response.

        Args:
            data (dict): Response data.
            fiat (FiatCurrency): Fiat currency for logging purposes.

        Returns:
            Optional[List[float]]: List of prices or None if failed.
        """
        if data.get("code") == "000000" and isinstance(data.get("data"), list) and len(data["data"]) > 0:
            precios = [float(adv["adv"]["price"]) for adv in data["data"]]
            self.logger.info(f"Getting prices: {len(precios)} for {fiat.value}")
            return precios

        self.logger.error(f"Binance response error: {data}")
        return None

    def _calculate_med(self, prices: Optional[List[float]]) -> Dict[str, Optional[float]]:
        """
        Calculate the median and average price.

        Args:
            prices (Optional[List[float]]): List of prices.

        Returns:
            Dict[str, Optional[float]]: Median and average price.
        """
        if not prices:
            self.logger.warning("Empty price list received from Binance")
            return {"median_price": None, "average_price": None}
        try:
            return {
                "median_price": median(prices),
                "average_price": mean(prices)
            }
        except Exception as e:
            self.logger.error(f"Error calculating median price: {e}")
            return {"median_price": None, "average_price": None}

    async def get_real_time_pair(
        self,
        fiat: FiatCurrency = FiatCurrency.VES,
        asset: BinanceAsset = BinanceAsset.USDT,
        trade_type: TradeType = TradeType.BUY,
        rows: int = 20
    ) -> Optional[BinanceRealTimeResponse]:
        """
        Get real-time pair metrics asynchronously from Binance P2P.

        Args:
            fiat (FiatCurrency, optional): Fiat currency. Defaults to FiatCurrency.VES.
            asset (BinanceAsset, optional): Asset (USDT, BTC, etc). Defaults to BinanceAsset.USDT.
            trade_type (TradeType, optional): Trade type. Defaults to TradeType.BUY.
            rows (int, optional): Number of rows per page. Defaults to 20, max 20.

        Returns:
            Optional[BinanceRealTimeResponse]: Real-time pair data or None if unavailable.
        """
        body = self._build_request(fiat=fiat, page=1, rows=rows, trade_type=trade_type, asset=asset)
        data = await self._do_request(body)
        if not data:
            self.logger.warning("No data received from Binance")
            return None

        precios = self._colect_prices(data, fiat=fiat)
        medians = self._calculate_med(precios)

        return BinanceRealTimeResponse(
            fiat=fiat,
            asset=asset,
            trade_type=trade_type,
            prices=precios or [],
            average_price=medians.get("average_price"),
            median_price=medians.get("median_price")
        )

    async def get_real_time_usdt_ves_pair(self) -> Optional[BinanceRealTimeResponse]:
        """
        Get the USDT/VES pair asynchronously.

        Returns:
            Optional[BinanceRealTimeResponse]: USDT/VES pair data for BUY trade type.
        """
        return await self.get_real_time_pair(
            fiat=FiatCurrency.VES,
            asset=BinanceAsset.USDT,
            trade_type=TradeType.BUY,
            rows=20
        )

    # Database Operations
    async def save_binance_currency(
        self,
        currency: FiatCurrency,
        asset: BinanceAsset,
        trade_type: TradeType
    ) -> BinanceCurrencyResponse:
        """
        Fetch current real-time P2P rate statistics and persist them to the database.

        Args:
            currency (FiatCurrency): Target fiat currency (e.g., VES).
            asset (BinanceAsset): Digital asset or stablecoin (e.g., USDT).
            trade_type (TradeType): Order book perspective (BUY or SELL).

        Returns:
            BinanceCurrencyResponse: Validated representation of saved database record.

        Raises:
            DatabaseSessionError: If execution context lacks an active database session.
            BinanceRequestError: If no pricing data could be fetched from Binance API.
            DatabaseOperationError: If an unexpected error occurs during database write.
        """
        pair = await self.get_real_time_pair(
            fiat=currency,
            asset=asset,
            trade_type=trade_type,
            rows=20
        )

        if not pair:
            self.logger.error("No data received from Binance for saving.")
            raise BinanceRequestError(
                message="No data received from Binance for saving.",
                details={
                    "currency": currency.value,
                    "asset": asset.value,
                    "trade_type": trade_type.value
                }
            )

        data_pair = BinanceCurrencyCreate(
            fiat=pair.fiat,
            asset=pair.asset,
            trade_type=pair.trade_type,
            average_price=pair.average_price,
            median_price=pair.median_price
        )

        try:
            saved_pair = await self.controller.register_rate(data_pair)
            return saved_pair
        except DatabaseSessionError:
            raise
        except Exception as e:
            self.logger.error(f"Error occurred while saving currency rate: {e}")
            raise DatabaseOperationError(
                message="Error occurred while saving currency rate.",
                details={"currency": currency.value, "asset": asset.value, "trade_type": trade_type.value}
            )

    async def get_last_saved_binance_fiat(
        self,
        fiat: FiatCurrency,
        asset: BinanceAsset,
        trade_type: TradeType
    ) -> BinanceCurrencyResponse:
        """
        Retrieve latest recorded exchange rate statistics for a specific trading pair.

        Args:
            fiat (FiatCurrency): Target fiat currency.
            asset (BinanceAsset): Target digital asset.
            trade_type (TradeType): Order book perspective.

        Returns:
            BinanceCurrencyResponse: Most recent database entry matching criteria.

        Raises:
            DatabaseSessionError: If execution context lacks an active database session.
            RegisterNotFoundError: If no record matches specified trading pair attributes.
            DatabaseOperationError: If an unexpected database exception occurs.
        """
        try:
            last_saved_pair = await self.controller.get_last_register_by_pair(
                fiat=fiat,
                asset=asset,
                trade_type=trade_type
            )

            if not last_saved_pair:
                self.logger.warning("No saved currency rate found in the database.")
                raise RegisterNotFoundError(
                    message="No saved currency rate found in the database.",
                    details={
                        "fiat": fiat.value,
                        "asset": asset.value,
                        "trade_type": trade_type.value
                    }
                )

            return last_saved_pair
        except (RegisterNotFoundError, DatabaseSessionError):
            raise
        except Exception as e:
            self.logger.error(f"Error occurred while retrieving last saved currency rate: {e}")
            raise DatabaseOperationError(
                message="Unexpected error occurred while retrieving the last saved currency rate.",
                details={"fiat": fiat.value, "asset": asset.value, "trade_type": trade_type.value, "error": str(e)}
            )

    async def get_all_saved_binance_pair(
        self,
        fiat: FiatCurrency,
        asset: BinanceAsset,
        trade_type: TradeType,
        skip: int = 0,
        limit: int = 100
    ) -> BinanceCurrencyListResponse:
        """
        Fetch a paginated collection of historical records for a specific trading pair.

        Args:
            fiat (FiatCurrency): Target fiat currency filter.
            asset (BinanceAsset): Target digital asset filter.
            trade_type (TradeType): Operational perspective filter.
            skip (int): Records offset for pagination. Defaults to 0.
            limit (int): Maximum chunk size of records. Defaults to 100.

        Returns:
            BinanceCurrencyListResponse: Aggregated dataset container along with counters.

        Raises:
            DatabaseSessionError: If execution context lacks an active database session.
            RegisterNotFoundError: If requested query filter resolves to an empty dataset.
            DatabaseOperationError: If an unexpected exception occurs during query.
        """
        try:
            all_saved_pairs = await self.controller.get_registers_by_pair(
                asset=asset,
                fiat=fiat,
                trade_type=trade_type,
                skip=skip,
                limit=limit
            )

            if all_saved_pairs.count == 0:
                self.logger.warning("No saved currency rates found in the database.")
                raise RegisterNotFoundError(
                    message="No saved currency rates found in the database.",
                    details={
                        "fiat": fiat.value,
                        "asset": asset.value,
                        "trade_type": trade_type.value
                    }
                )

            return all_saved_pairs
        except (RegisterNotFoundError, DatabaseSessionError):
            raise
        except Exception as e:
            self.logger.error(f"Error occurred while retrieving all saved currency rates: {e}")
            raise DatabaseOperationError(
                message="Unexpected error occurred while retrieving all saved currency rates.",
                details={
                    "fiat": fiat.value,
                    "asset": asset.value,
                    "trade_type": trade_type.value,
                    "error": str(e)
                }
            )

    async def get_binance_pair_by_time_range(
        self,
        fiat: FiatCurrency,
        asset: BinanceAsset,
        trade_type: TradeType,
        start_time: datetime,
        end_time: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> BinanceCurrencyListResponse:
        """
        Query historical trading pair metrics bounded inside specific time boundaries.

        Args:
            fiat (FiatCurrency): Target fiat currency filter.
            asset (BinanceAsset): Target digital asset filter.
            trade_type (TradeType): Operational perspective filter.
            start_time (datetime): Lower bound constraint.
            end_time (datetime): Upper bound constraint.
            skip (int): Offset records window marker. Defaults to 0.
            limit (int): Partition size constraint. Defaults to 100.

        Returns:
            BinanceCurrencyListResponse: Ordered records container payload.

        Raises:
            DatabaseSessionError: If execution context lacks an active database session.
            RegisterNotFoundError: If no dataset elements fall into range boundaries.
            DatabaseOperationError: If an unexpected anomaly happens during execution.
        """
        try:
            rates = await self.controller.get_registers_by_date_range(
                asset=asset,
                fiat=fiat,
                trade_type=trade_type,
                start_date=start_time,
                end_date=end_time,
                skip=skip,
                limit=limit
            )

            if rates.count == 0:
                self.logger.warning("No saved currency rates found in the specified time range.")
                raise RegisterNotFoundError(
                    message="No saved currency rates found in the specified time range.",
                    details={
                        "fiat": fiat.value,
                        "asset": asset.value,
                        "trade_type": trade_type.value,
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat()
                    }
                )
            return rates
        except (RegisterNotFoundError, DatabaseSessionError):
            raise
        except Exception as e:
            self.logger.error(f"Error occurred while retrieving currency rates by time range: {e}")
            raise DatabaseOperationError(
                message="Unexpected error occurred while retrieving currency rates by time range.",
                details={
                    "fiat": fiat.value,
                    "asset": asset.value,
                    "trade_type": trade_type.value,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "error": str(e)
                }
            )
