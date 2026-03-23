import os
import sys
import logging
from dotenv import load_dotenv
logger = logging.getLogger("email_organizer")
if getattr(sys, 'frozen', False):
    # Ejecutable PyInstaller
    application_path = os.path.dirname(sys.executable)
else:
    # Script normal
    application_path = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(application_path, 'config.json')

def setupenv():
    load_dotenv()
    environments = ["GEMINI_API_KEY", "DATABASE_URL",
                    "PASSWORD", "GMAIL_CLIENT_ID",
                    "GMAIL_CLIENT_SECRET", "GMAIL_PROJECT_ID",
                    "GMAIL_JSON"]
    for i in environments:
        env = os.getenv(i)
        if env == None:
            logger.error(f"{i} is not set in .env")
            sys.exit(1)