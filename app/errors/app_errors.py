from typing import Any, Optional
from app.errors.base_error import DolarVzlaError

class BCVConnectionError(DolarVzlaError):
    """Error raised when there is a connection issue with the BCV website."""
    def __init__(self, message: str = "Error connecting to the BCV website.", details=None):
        super().__init__(message, details)
    
class BCVReadingRateError(DolarVzlaError):
    """Error raised when there is an issue reading the rate from the BCV website."""
    def __init__(self, message: str = "Error reading the rate from the BCV website.", details=None):
        super().__init__(message, details)

class RegisterNotFoundError(DolarVzlaError):
    """Error raised when a rate register is not found on the database."""
    def __init__(self, message: str = "Register not found", details=None):
        super().__init__(message, details)

class DatabaseSessionError(DolarVzlaError):
    """Error raised when there is an issue with the database session."""
    def __init__(self, message: str = "Database session error", details=None):
        super().__init__(message, details)

class DatabaseOperationError(DolarVzlaError):
    """Error raised when there is an issue with a database operation."""
    def __init__(self, message: str = "Database operation error", details=None):
        super().__init__(message, details)

class BinanceConnectionError(DolarVzlaError):
    """Error raised when there is a connection issue with the Binance P2P API."""
    def __init__(self, message: str = "Error connecting to the Binance P2P API.", details=None):
        super().__init__(message, details)

class BinanceRequestError(DolarVzlaError):
    """Error raised when there is an issue with the request to the Binance P2P API."""
    def __init__(self, message: str = "Error with the request to the Binance P2P API.", details=None):
        super().__init__(message, details)