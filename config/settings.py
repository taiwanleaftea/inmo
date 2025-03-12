import os
import logging
from dotenv import load_dotenv

load_dotenv()

LOGGING_CONFIG = {
    'level': logging.WARN,  # Changed to DEBUG for detailed logging
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'handlers': [
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
}

EMAIL_CONFIG = {
    'sender': os.getenv('ALERT_EMAIL'),
    'password': os.getenv('ALERT_EMAIL_PASSWORD'),
    'receiver': os.getenv('ALERT_EMAIL'),
    'smtp_server': "smtp.gmail.com",
    'smtp_port': 587
}