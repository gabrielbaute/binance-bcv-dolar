from fastapi import APIRouter

from app.controllers.history_data_controller import HistoryDataController
from app.schemas import BCVHistoryResponse, BinanceHistoryResponse


router = APIRouter(prefix="/history", tags=["History"])
controller = HistoryDataController()

@router.get("/bcv", response_model=BCVHistoryResponse, summary="History of BCV rates")
def history_bcv():
    return controller.get_bcv_history()

@router.get("/binance", response_model=BinanceHistoryResponse, summary="History of Binance rates")
def history_binance():
    return controller.get_binance_history()
