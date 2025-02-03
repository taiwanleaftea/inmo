from config.settings import LOGGING_CONFIG  # Add this import
import pandas as pd
import logging

def configure_logging():
    logging.basicConfig(**LOGGING_CONFIG)  # Now has access to the config

def load_existing_data():
    try:
        return pd.read_excel('delft_rentals_final.xlsx', sheet_name='All_Listings')
    except FileNotFoundError:
        return pd.DataFrame()