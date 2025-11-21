from fastapi import APIRouter, Query
from datetime import datetime
from typing import Optional

from app.controllers.history_data_controller import HistoryDataController
from app.schemas import BCVHistoryResponse, BinanceHistoryResponse

router = APIRouter(prefix="/history", tags=["History"])
controller = HistoryDataController()

@router.get("/bcv", response_model=BCVHistoryResponse, summary="Histórico de tasas BCV")
def history_bcv(
    start_date: Optional[datetime] = Query(None, description="Fecha inicial (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="Fecha final (YYYY-MM-DD)"),
    currency: Optional[str] = Query(None, description="Moneda a consultar, ej: USD, EUR")
):
    return controller.get_bcv_history(start_date=start_date, end_date=end_date, currency=currency)

@router.get("/binance", response_model=BinanceHistoryResponse, summary="Histórico de tasas Binance")
def history_binance(
    start_date: Optional[datetime] = Query(None, description="Fecha inicial (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="Fecha final (YYYY-MM-DD)"),
    fiat: Optional[str] = Query(None, description="Fiat a consultar, ej: VES, PEN"),
    asset: Optional[str] = Query(None, description="Cripto a consultar, ej: USDT"),
    trade_type: Optional[str] = Query(None, description="Tipo de operación: BUY o SELL")
):
    return controller.get_binance_history(
        start_date=start_date,
        end_date=end_date,
        fiat=fiat,
        asset=asset,
        trade_type=trade_type
    )
