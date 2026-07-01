from app.errors.base_error import DolarVzlaError

class BCVConnectionError(DolarVzlaError):
    """Error raised when there is a connection issue with the BCV website."""
    def __init__(self, message: str = "Error connecting to the BCV website."):
        super().__init__(message)
    
class BCVReadingRateError(DolarVzlaError):
    """Error raised when there is an issue reading the rate from the BCV website."""
    def __init__(self, message: str = "Error reading the rate from the BCV website."):
        super().__init__(message)

class BinanceConnectionError(DolarVzlaError):
    """Error raised when there is a connection issue with the Binance P2P API."""
    def __init__(self, message: str = "Error connecting to the Binance P2P API."):
        super().__init__(message)

class RegisterNotFoundError(DolarVzlaError):
    """Error raised when a rate register is not found on the database."""
    def __init__(self, message: str = "Register not found"):
        super().__init__(message)

class DatabaseSessionError(DolarVzlaError):
    """Error raised when there is an issue with the database session."""
    def __init__(self, message: str = "Database session error"):
        super().__init__(message)