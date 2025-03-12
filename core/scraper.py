import requests
import time
import random
import pandas as pd
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import logging

class RealEstateScraper:
    def __init__(self, site, config):
        self.site = site
        self.config = config
        self.ua = UserAgent()
        self.session = requests.Session()
        self.logger = logging.getLogger(site)
        
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504, 429],
            allowed_methods=['GET']
        )
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
    
    def get_headers(self):
        base_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'nl-NL,nl;q=0.9',
        }
        base_headers.update(self.config.get('required_headers', {}))
        base_headers['User-Agent'] = self.ua.random
        return base_headers
    
    def get_request_delay(self):
        return random.uniform(*self.config['delay'])
    
    def safe_extract(self, element, selector):
        try:
            if len(selector) == 3:
                css_selector, target_type, processor = selector
            else:
                css_selector, target_type = selector
                processor = None

            target = element.select_one(css_selector)
            if not target:
                self.logger.debug(f"No element found for selector {css_selector} in {element.prettify()}")
                return None
                
            if target_type == 'text':
                value = target.get_text(strip=True)
                self.logger.debug(f"Extracted value '{value}' from {css_selector}")
            elif target_type == 'href':
                value = urljoin(self.config['base_url'], target['href'])
            else:
                value = target.get(target_type, None)

            if processor and value:
                result = processor(value)
                self.logger.debug(f"Processed '{value}' to {result} for {css_selector}")
                return result
            return value
                
        except Exception as e:
            self.logger.warning(f"Extraction error: {str(e)} for {element.prettify()}")
            return None

    def process_listing(self, element):
        self.logger.debug(f"Processing listing: {element.prettify()}")
        try:
            if self.site == 'rentaroom':
                is_rented = self.safe_extract(element, self.config['selectors']['rented'])
                if is_rented:
                    return None

            raw_data = {
                'title': self.safe_extract(element, self.config['selectors']['title']) or '',
                'price': self.safe_extract(element, self.config['selectors']['price']) or 0,
                'rooms': self.safe_extract(element, self.config['selectors']['rooms']) or 0,
                'size': self.safe_extract(element, self.config['selectors']['size']) or 0,
                'url': self.safe_extract(element, self.config['selectors']['url']) or ''
            }

            try:
                raw_data['price'] = int(raw_data['price'])
                raw_data['rooms'] = int(raw_data['rooms'])
                raw_data['size'] = int(raw_data['size'])
            except ValueError:
                self.logger.debug(f"Invalid numeric conversion: {raw_data}")
                return None

            if not all([raw_data['title'], raw_data['price'] > 0, raw_data['url']]):
                self.logger.debug(f"Skipping due to invalid data: {raw_data}")
                return None
                
            listing = {
                'title': raw_data['title'],
                'price': raw_data['price'],
                'rooms': raw_data['rooms'],
                'size': raw_data['size'],
                'url': raw_data['url'],
                'source': self.site
            }
            
            if listing['price'] > (listing['rooms'] * 600):
                self.logger.debug(f"Price {listing['price']} exceeds threshold for {listing['rooms']} rooms")
                return None
                
            self.logger.debug(f"Valid listing: {listing}")
            return listing
                
        except Exception as e:
            self.logger.error(f"Listing processing error: {str(e)}")
            return None

    def scrape_page(self, page):
        try:
            if self.site == 'pararius':
                url = f"{self.config['base_url']}/{self.config['paginator'].format(page)}"
            elif self.site == 'rentaroom':
                url = f"{self.config['base_url']}{self.config['paginator'].format(page)}"
            else:
                url = urljoin(self.config['base_url'], 
                            self.config['paginator'].format(page))
            
            self.logger.info(f"Scraping page {page}: {url}")
            
            response = self.session.get(
                url,
                headers=self.get_headers(),
                timeout=15,
                allow_redirects=True
            )
            
            if response.status_code == 404:
                self.logger.info(f"Reached end of pagination at page {page}")
                return None
            elif response.status_code != 200:
                self.logger.warning(f"Blocked on page {page} (Status: {response.status_code})")
                return []
                
            soup = BeautifulSoup(response.content, 'lxml')
            listings = soup.select(self.config['listings_selector'])
            
            self.logger.info(f"Found {len(listings)} listings on page {page}")
            return listings
            
        except Exception as e:
            self.logger.error(f"Page scraping error: {str(e)}")
            return []

    def process_site(self, max_pages=5):
        results = []
        
        for page in range(1, max_pages + 1):
            listings = self.scrape_page(page)
            if listings is None:
                break
                
            for listing in listings:
                processed_data = self.process_listing(listing)
                if processed_data:
                    results.append(processed_data)
            
            time.sleep(self.get_request_delay())
            
        return pd.DataFrame(results)