# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LOG_DIR = os.getenv("LOG_DIR", os.path.join(BASE_DIR, "logs"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
