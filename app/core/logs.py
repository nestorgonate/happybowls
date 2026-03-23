import sys
import os
import logging.config
from datetime import datetime

if getattr(sys, 'frozen', False):
    # Ejecutable PyInstaller
    application_path = os.path.dirname(sys.executable)
else:
    # Script normal
    application_path = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(application_path, "logs")
if not os.path.exists(log_path):
    os.makedirs(log_path, exist_ok=True)
log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
log_path = os.path.join(log_path, log_filename)
"""
Funcion para crear una carpeta para almacenar los logs
"""

def setupLogs():
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "archivo_handler": {
                "class": "logging.FileHandler",
                "formatter": "default",
                "filename": log_path,
                "mode": "a",
                "encoding": "utf-8",
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "email_organizer": {
                "handlers": ["console", "archivo_handler"], 
                "level": "DEBUG", 
                "propagate": False
            },
            "uvicorn.error": {"level": "INFO", "handlers": ["archivo_handler", "console"]},
            "uvicorn.access": {"level": "INFO", "propagate": False},
        },
    }
    logging.config.dictConfig(LOGGING_CONFIG)