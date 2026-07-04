from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.errors import (
    DolarVzlaError,
    BCVConnectionError, 
    BCVReadingRateError,
    RegisterNotFoundError,
    DatabaseSessionError,
    DatabaseOperationError,
    BinanceConnectionError, 
    BinanceRequestError
)

def register_error_handlers(app: FastAPI):
    """
    Registers the global exception handlers for the application.
    """
    @app.exception_handler(DolarVzlaError)
    async def global_octopus_handler(request: Request, exc: DolarVzlaError):
        """
        Map backend errors to HTTP codes for the API
        """
        error_mapping = {
            BCVConnectionError: status.HTTP_408_REQUEST_TIMEOUT,
            BCVReadingRateError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            RegisterNotFoundError: status.HTTP_404_NOT_FOUND,
            DatabaseSessionError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DatabaseOperationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            BinanceConnectionError: status.HTTP_408_REQUEST_TIMEOUT,
            BinanceRequestError: status.HTTP_418_IM_A_TEAPOT
        }

        http_status = error_mapping.get(type(exc), status.HTTP_400_BAD_REQUEST)

        return JSONResponse(
            status_code=http_status,
            content={
                "status": "error",
                "code": exc.__class__.__name__,
                "message": exc.message,
                "details": jsonable_encoder(exc.details or {})
            },
        )
    
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        """
        Capture any uncontrolled errors to prevent information leaks.
        """
        import logging
        logger = logging.getLogger("uvicorn.error")
        logger.error(f"Unhandled error: {str(exc)}", exc_info=True)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "code": "InternalServerError",
                "message": "An unexpected error has occurred on the server."
            },
        )