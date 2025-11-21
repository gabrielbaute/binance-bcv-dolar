# app/api/routes/fiat_routes.py
from fastapi import APIRouter, Query
from app.services.fiat_exchange_service import FiatExchengeService
from app.schemas.fiats_pair_response import FiatPairResponse

router = APIRouter(prefix="/fiat", tags=["Fiat Exchange"])
fiat_service = FiatExchengeService()

@router.get("/pair", response_model=FiatPairResponse, summary="Get fiat/fiat pair")
def get_fiat_pair(
    fiat_1: str = Query(..., description="First fiat currency, e.g. VES"),
    fiat_2: str = Query(..., description="Second fiat currency, e.g. PEN")
):
    return fiat_service.get_pair(fiat_1=fiat_1, fiat_2=fiat_2)
