"""
General configuration for the app.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Config class for environtment variables.
    """
    APP_NAME = "P2P Exchange Tracker"
    APP_VERSION = "0.1.0"

    # Directory and path config
    BASE_DIR = Path(__file__).resolve().parent
    INSTANCE_DIR = Path(os.getenv("INSTANCE_DIR", BASE_DIR / ".." / "instance"))
    
    
    # Logging config
    LOG_DIR = Path(os.getenv("LOG_DIR", BASE_DIR / "logs"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # API config
    API_PORT = int(os.getenv("API_PORT", 8000))
    API_HOST = os.getenv("API_HOST", "0.0.0.0")

    # Database config
    DATABASE_URL = f"sqlite:///{os.path.join(INSTANCE_DIR, 'exchange_rates.db')}"
    DATABASE_CONNECT_ARGS = {"check_same_thread": False}

    # Webhooks
    NTFY_TOPIC = os.getenv("NTFY_TOPIC", "p2p_tracker_alerts")
    NTFY_URL = os.getenv("NTFY_URL", "https://ntfy.sh")