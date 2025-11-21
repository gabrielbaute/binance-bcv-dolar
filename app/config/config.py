import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Config class for environtment variables.
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LOG_DIR = os.getenv("LOG_DIR", os.path.join(BASE_DIR, "logs"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    API_PORT = os.getenv("API_PORT", 5000)
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
