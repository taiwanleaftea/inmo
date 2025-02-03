import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Explicitly define LOGGING_CONFIG here
LOGGING_CONFIG = {
    'level': logging.INFO,
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'handlers': [
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
}

# Email configuration
EMAIL_CONFIG = {
    'sender': os.getenv('ALERT_EMAIL'),
    'password': os.getenv('ALERT_EMAIL_PASSWORD'),
    'receiver': os.getenv('ALERT_EMAIL'),
    'smtp_server': "smtp.gmail.com",
    'smtp_port': 587
}

# Logging configuration
LOGGING_CONFIG = {
    'level': logging.INFO,
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'handlers': [
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
}