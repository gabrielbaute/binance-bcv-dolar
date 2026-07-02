"""Binance P2P module."""
import logging
from requests import Session
from datetime import datetime
from statistics import median, mean
from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from requests.exceptions import RequestException

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
    Binance P2P Client.
    """
    def __init__(self, databasesession: Optional[AsyncSession] = None):
        self.url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        self.request_session = Session()
        self.database_session = databasesession
        self.controller = BinanceController(session=databasesession) if databasesession else None
        self.logger = logging.getLogger(self.__class__.__name__)

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
        """
        req = BinanceRequest(
            fiat=fiat.value,
            page=page,
            rows=rows,
            tradeType=trade_type.value,
            asset=asset.value
        )
        if rows > 20:
            raise BinanceRequestError(
                message="Rows parameter exceeds the maximum limit of 20. Binance P2P API restricts the number of rows per page to a maximum of 20.",
                details={"rows": rows}
            )
        return req

    def _do_request(self, req: BinanceRequest) -> dict:
        """
        Do the request to Binance P2P.

        Args:
            req (BinanceRequest): BinanceRequest object.

        Returns:
            dict: Response data.
        
        Raises:
            BinanceConnectionError: If there was an error connecting to Binance P2P.
        """
        body = req.model_dump()
        try:
            self.logger.debug("Request Binance P2P")
            res = self.request_session.post(self.url, json=body, headers={"Content-Type": "application/json"}, timeout=15)
            res.raise_for_status()
            self.logger.debug("Response Binance P2P")
            json_data = res.json()
            return json_data
        except RequestException as e:
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

    def _colect_prices(self, data: dict, fiat: FiatCurrency) -> List[float]:
        """
        Colect prices from Binance P2P response.

        Args:
            data (dict): Response data.
            fiat (FiatCurrency): Fiat currency for logging purposes.

        Returns:
            List[float]: List of prices.
        """
        if data.get("code") == "000000" and isinstance(data.get("data"), list) and len(data["data"]) > 0:
            precios = []
            for adv in data["data"]:
                precios.append(float(adv["adv"]["price"]))
            self.logger.info(f"Getting prices: {len(precios)} for {fiat.value}")
            return precios
        else:
            self.logger.error("Binance response error:", data)
            return None

    def _calculate_med(self, prices: Optional[List[float]]) -> Dict[str, Optional[float]]:
        """
        Calculate the median price.

        Args:
            prices (Optional[List[float]]): List of prices.

        Returns:
            Dict[str, float]: Median and average price
        """
        if not prices:
            self.logger.warning("Empty price list received from Binance")
            return {"median_price": None, "average_price": None}
        try:
            median_price = median(prices)
            average_price = mean(prices)
            return {"median_price": median_price, "average_price": average_price}
        except Exception as e:
            self.logger.error(f"Error calculating median price: {e}")
            return {"median_price": None, "average_price": None}

    def get_real_time_pair(
            self, 
            fiat: FiatCurrency = FiatCurrency.VES, 
            asset: BinanceAsset = BinanceAsset.USDT,
            trade_type: TradeType = TradeType.BUY,
            rows: int = 20
        ) -> Optional[BinanceRealTimeResponse]:
        """
        Get the real-time pair from Binance P2P.

        Args:
            fiat (FiatCurrency, optional): Fiat currency. Defaults to FiatCurrency.VES.
            asset (BinanceAsset, optional): Asset (USDT, BTC, etc). Defaults to BinanceAsset.USDT.
            trade_type (TradeType, optional): Trade type. Defaults to TradeType.BUY.
            rows (int, optional): Number of rows per page. Defaults to 20, max 20.

        Returns:
            Optional[BinanceRealTimeResponse]: BinanceRespBinanceRealTimeResponseonse object.
        """
        body = self._build_request(fiat=fiat, page=1, rows=rows, trade_type=trade_type, asset=asset)
        data = self._do_request(body)
        if not data:
            self.logger.warning("No data received from Binance")
            return None
        precios = self._colect_prices(data, fiat=fiat)
        medians = self._calculate_med(precios)
    
        pair = BinanceRealTimeResponse(
            fiat=fiat,
            asset=asset,
            trade_type=trade_type,
            prices=precios,
            average_price=medians.get("average_price"),
            median_price=medians.get("median_price")
        )
        return pair

    def get_real_time_usdt_ves_pair(self) -> Optional[BinanceRealTimeResponse]:
        """
        Get the USDT/VES pair.

        Returns:
            Optional[BinanceRealTimeResponse]: USDT/VES pair data for BUY trade type.
        """
        return self.get_real_time_pair(fiat=FiatCurrency.VES, asset=BinanceAsset.USDT, trade_type=TradeType.BUY, rows=20)
    
    # Additional methods for database operations
    async def save_binance_currency(
            self, 
            currency: FiatCurrency, 
            asset: BinanceAsset, 
            trade_type: TradeType
    ) -> BinanceCurrencyResponse:
        """
        Fetch the current real-time P2P rate statistics and persist them to the database.

        Args:
            currency (FiatCurrency): The target fiat currency (e.g., VES).
            asset (BinanceAsset): The digital asset or stablecoin (e.g., USDT).
            trade_type (TradeType): The order book perspective (BUY or SELL).

        Returns:
            BinanceCurrencyResponse: The validated output representation of the saved database record.

        Raises:
            DatabaseSessionError: If execution context lacks an active database session.
            BinanceRequestError: If no operational pricing data could be fetched from Binance API.
            DatabaseOperationError: If an unexpected error occurs during database write operation.
        """
        if not self.database_session:
            self.logger.error("Database session is not provided.")
            raise DatabaseSessionError(
                message="Database session is required to save rates.",
                details={"error": "No database session provided."}
            )
        
        pair = self.get_real_time_pair(fiat=currency, asset=asset, trade_type=trade_type, rows=20)
        
        if not pair:
            self.logger.error("No data received from Binance for saving.")
            raise BinanceRequestError(
                message="No data received from Binance for saving.",
                details={"currency": currency.value, "asset": asset.value, "trade_type": trade_type.value}
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
        Retrieve the latest recorded exchange rate statistics for a specific trading pair.

        Args:
            fiat (FiatCurrency): The target fiat currency.
            asset (BinanceAsset): The target digital asset.
            trade_type (TradeType): The order book perspective.

        Returns:
            BinanceCurrencyResponse: The most recent validated database entry matching criteria.

        Raises:
            DatabaseSessionError: If execution context lacks an active database session.
            RegisterNotFoundError: If no record matches the specified trading pair attributes.
            DatabaseOperationError: If an unexpected database persistence or system exception occurs.
        """
        if not self.database_session:
            self.logger.error("Database session is not provided.")
            raise DatabaseSessionError(
                message="Database session is required to retrieve rates.",
                details={"error": "No database session provided."}
            )
        
        try:
            last_saved_pair = await self.controller.get_last_register_by_pair(fiat=fiat, asset=asset, trade_type=trade_type)

            if not last_saved_pair:
                self.logger.warning("No saved currency rate found in the database.")
                raise RegisterNotFoundError(
                    message="No saved currency rate found in the database.",
                    details={"fiat": fiat.value, "asset": asset.value, "trade_type": trade_type.value}
                )

            return last_saved_pair
        except RegisterNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error occurred while retrieving the last saved currency rate: {e}")
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
            fiat (FiatCurrency): The target fiat currency filter.
            asset (BinanceAsset): The target digital asset stablecoin filter.
            trade_type (TradeType): The operational perspective filter.
            skip (int): The number of records to skip for pagination offsets. Defaults to 0.
            limit (int): The maximum chunk size window of records to slice. Defaults to 100.

        Returns:
            BinanceCurrencyListResponse: Aggregated dataset container along with global filter counters.

        Raises:
            DatabaseSessionError: If execution context lacks an active database session.
            RegisterNotFoundError: If the requested query filter resolves to an empty dataset.
            DatabaseOperationError: If an unexpected exception occurs during query resolution.
        """
        if not self.database_session:
            self.logger.error("Database session is not provided.")
            raise DatabaseSessionError(
                message="Database session is required to retrieve rates.",
                details={"error": "No database session provided."}
            )
        
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
                    details={"fiat": fiat.value, "asset": asset.value, "trade_type": trade_type.value}
                )

            return all_saved_pairs
        except RegisterNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error occurred while retrieving all saved currency rates: {e}")
            raise DatabaseOperationError(
                message="Unexpected error occurred while retrieving all saved currency rates.",
                details={"fiat": fiat.value, "asset": asset.value, "trade_type": trade_type.value, "error": str(e)}
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
        Query historical trading pair metrics bounded inside specific chronological boundaries.

        Args:
            fiat (FiatCurrency): The target fiat currency filter.
            asset (BinanceAsset): The target digital asset filter.
            trade_type (TradeType): The operational perspective filter.
            start_time (datetime): Chronological lower bound constraint parameter.
            end_time (datetime): Chronological upper bound constraint parameter.
            skip (int): Offset records window marker for slice pagination. Defaults to 0.
            limit (int): Partition size configuration constraint. Defaults to 100.

        Returns:
            BinanceCurrencyListResponse: Ordered records context wrapper payload containing targeted sets.

        Raises:
            DatabaseSessionError: If execution context lacks an active database session.
            RegisterNotFoundError: If no dataset elements fall into the designated range boundaries.
            DatabaseOperationError: If an unexpected operation anomaly happens on execution blocks.
        """
        if not self.database_session:
            self.logger.error("Database session is not provided.")
            raise DatabaseSessionError(
                message="Database session is required to retrieve rates.",
                details={"error": "No database session provided."}
            )
        
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
        except RegisterNotFoundError:
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