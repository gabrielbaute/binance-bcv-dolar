"""
General configuration for the app.
"""
import sys
from pathlib import Path  
from pydantic import Field  
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.app_version import __version__

class Config(BaseSettings):
    """
    Config class for environtment variables.
    """
    # ------------ APP INFO ------------  
    APP_NAME: str = "P2P Exchange Tracker"
    APP_VERSION: str =  __version__

    # ------------ Directories and config path ------------  
    # Directory and path config
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    INSTANCE_DIR: Path = BASE_DIR / "instance"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    
    # ----------- LOGGING -------------
    LOG_LEVEL: str = "INFO"
    
    # ----------- API -----------------
    API_HOST: str = "127.0.0.1"  
    API_PORT: int = 8000  
    API_RELOAD: bool = False  
    API_LOG_LEVEL: str = "info"

    # ----------- DATABASE ------------
    DATABASE_URL: str = str(f"sqlite+aiosqlite:///{INSTANCE_DIR / f'dolar_vzla.db'}")  
    DATABASE_ECHO: bool = False  
    DATABASE_POOL_SIZE: int = 5  
    DATABASE_POOL_RECYCLE: int = 3600  
    DATABASE_POOL_TIMEOUT: int = 30  
    DATABASE_POOL_PRE_PING: bool = True

    # ----------- WEBHOOKS ------------
    NTFY_TOPIC: str
    NTFY_URL: str

    # ----------- CRONJOBS ------------
    BINANCE_EXTRA_FIATS: str
    BINANCE_EXTRA_CRON: str
    BINANCE_VES_CRON: str
    BCV_CRON: str

    model_config = SettingsConfigDict(  
        env_file=".env",  
        env_file_encoding="utf-8",  
        extra="ignore"  
    )

    def __init__(self, **values):
        """
        Initialize configuration settings, forcing physical directory verification layout.
        """
        super().__init__(**values)
        self.ensure_dirs()
        
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"sqlite+aiosqlite:///{self.INSTANCE_DIR / 'dolar_vzla.db'}"

    def ensure_dirs(self) -> None:
        try:
            self.INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
            self.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f" CRITICAL ERROR: Could not create directory {dir}. check permissions.")
            sys.exit(1)

config = Config()