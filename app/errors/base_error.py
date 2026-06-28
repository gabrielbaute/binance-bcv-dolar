from typing import Any, Dict, Optional

class DolarVzlaError(Exception):
    """Base class for errors and exceptions."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}