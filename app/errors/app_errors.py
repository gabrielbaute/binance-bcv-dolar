from app.errors.base_error import DolarVzlaError

class BCVConnectionError(DolarVzlaError):
    """Error raised when there is a connection issue with the BCV website."""
    def __init__(self, message: str = "Error connecting to the BCV website."):
        super().__init__(message)

class BinanceConnectionError(DolarVzlaError):
    """Error raised when there is a connection issue with the Binance P2P API."""
    def __init__(self, message: str = "Error connecting to the Binance P2P API."):
        super().__init__(message)

class RegisterNotFoundError(DolarVzlaError):
    """Error raised when a rate register is not found on the database."""
    def __init__(self, message: str = "Register not found"):
        super().__init__(message)