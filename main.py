import logging
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from config import settings, selectors
from core.scraper import RealEstateScraper
from utils.helpers import configure_logging, load_existing_data
from utils.handlers import filter_listings, prepare_email_content
from core.email_alert import send_alert

def save_updated_data(old_df, new_df):
    """Combine old and new data, removing duplicates"""
    combined = pd.concat([old_df, new_df], ignore_index=True)
    
    # Remove duplicates while keeping first occurrence
    combined = combined.drop_duplicates(
        subset=['url', 'source'], 
        keep='first'
    ).sort_values(by='source', ascending=True)
    
    # Save to Excel with the correct sheet name
    with pd.ExcelWriter('delft_rentals_final.xlsx') as writer:
        combined.to_excel(writer, index=False, sheet_name='All_Listings')
        
        if not combined.empty:
            combined[combined['rooms'] == 1].to_excel(
                writer, index=False, sheet_name='Single_Under600')
            combined[combined['rooms'] >= 2].to_excel(
                writer, index=False, sheet_name='Couple_Over1200')
    
    return combined

def main():
    configure_logging()
    
    # Load previous data
    existing_df = load_existing_data()
    
    # Scrape all sites
    scrapers = {
        name: RealEstateScraper(name, selectors.WEBSITE_CONFIG[name])
        for name in selectors.WEBSITE_CONFIG
    }
    
    results = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(scraper.process_site): name 
                  for name, scraper in scrapers.items()}
        for future in futures:
            try:
                results.append(future.result())
            except Exception as e:
                logging.error(f"Error processing {futures[future]}: {str(e)}")
    
    # Process new data
    new_raw_df = pd.concat(results).pipe(filter_listings)
    new_raw_df['per_person_price'] = new_raw_df['price'] / new_raw_df['rooms']
    
    # Find new listings
    if existing_df.empty:
        new_listings = new_raw_df  # All listings are new if no existing data
    else:
        new_listings = new_raw_df[~new_raw_df['url'].isin(existing_df['url'])]
    
    # Trigger email alert if new listings found
    if not new_listings.empty:
        email_content = prepare_email_content(new_listings)
        send_alert(len(new_listings), email_content, settings.EMAIL_CONFIG)
    
    # Save updated data
    updated_df = save_updated_data(existing_df, new_raw_df)
    logging.info(f"Scraping complete. Total listings: {len(updated_df)}")

if __name__ == "__main__":
    main()