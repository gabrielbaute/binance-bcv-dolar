import logging
import os
import sys
from pathlib import Path

LOG_FORMAT = "[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s"

def setup_logging(level=logging.INFO, log_dir: str = "logs"):
    # Crear directorio si no existe
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # Handlers
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(os.path.join(log_dir, "app.log"))

    # Formato
    formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Configuración global
    logging.basicConfig(
        level=level,
        handlers=[console_handler, file_handler]
    )
