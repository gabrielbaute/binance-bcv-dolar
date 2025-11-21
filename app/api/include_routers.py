from fastapi import FastAPI

from app.api.routes.bcv_routes import router as bcv_router
from app.api.routes.dolar_routes import router as dolar_router
from app.api.routes.binance_routes import router as binance_router
from app.api.routes.history_routes import router as history_router
from app.api.routes.fiat_routes import router as fiat_router


def include_routers(app: FastAPI):
    """
    Include routers for API routes
    """
    app.include_router(bcv_router)
    app.include_router(dolar_router)
    app.include_router(binance_router)
    app.include_router(history_router)
    app.include_router(fiat_router)