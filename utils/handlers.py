import pandas as pd

def filter_listings(df):
    return df[df['price'] <= df['rooms'] * 600].drop_duplicates(['url', 'source'])

def prepare_email_content(df):
    return df.to_html(index=False, border=1, columns=['title', 'price', 'rooms', 'url', 'source'])