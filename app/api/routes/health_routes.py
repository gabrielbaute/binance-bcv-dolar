from datetime import datetime
from fastapi import APIRouter, Depends

from app.config import Config
from app.api.dependencies import get_config_instance

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", summary="Healthcheck endpoint")
async def healthcheck(
    config_instance: Config = Depends(get_config_instance)
):
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "app_name": config_instance.APP_NAME,
        "app_version": config_instance.APP_VERSION
    }
