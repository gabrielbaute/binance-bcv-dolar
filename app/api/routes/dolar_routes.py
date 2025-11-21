from fastapi import APIRouter

from app.services import DolarService
from app.schemas import DolarResponse

router = APIRouter(prefix="/dolar", tags=["Dolar", "Dolar Promedio", "Dolar Actual"])

@router.get("/venezuela", response_model=DolarResponse)
def venezuela_dolar():
    service = DolarService()
    return service.get_average_dolar()