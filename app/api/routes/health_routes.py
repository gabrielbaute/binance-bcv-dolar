from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", summary="Healthcheck endpoint")
def healthcheck():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }
