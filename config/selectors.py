import re
from urllib.parse import urljoin

WEBSITE_CONFIG = {
    'huurwoningen': {
        'base_url': 'https://www.huurwoningen.nl/in/delft/',
        'listings_selector': 'section.listing-search-item',
        'selectors': {
            'title': ('.listing-search-item__title', 'text', None),
            'price': ('.listing-search-item__price', 'text',
                      lambda t: int(re.sub(r'[^\d]', '', t.split('€')[-1]))),
            'rooms': ('li.illustrated-features__item--number-of-rooms', 'text',
                      lambda t: int(re.search(r'\d+', t).group()) if t else 0),
            'size': ('li.illustrated-features__item--surface-area', 'text',
                     lambda t: int(re.search(r'\d+', t).group()) if t else 0),
            'url': ('.listing-search-item__link--title', 'href', None),
        },
        'paginator': '?page={}',
        'delay': (1, 3),
    },
    'pararius': {
        'base_url': 'https://www.pararius.com/apartments/delft',
        'listings_selector': 'li.search-list__item--listing',
        'selectors': {
            'title': ('.listing-search-item__title', 'text', None),
            'price': ('.listing-search-item__price', 'text',
                      lambda t: int(re.sub(r'[^\d]', '', t.split('€')[-1]))),
            'rooms': ('.illustrated-features__item--number-of-rooms', 'text',
                      lambda t: int(re.search(r'\d+', t).group()) if t else 0),
            'size': ('.illustrated-features__item--surface-area', 'text',
                     lambda t: int(re.search(r'\d+', t).group()) if t else 0),
            'url': ('.listing-search-item__link--title', 'href', None),
        },
        'paginator': 'page-{}',
        'delay': (3, 7),
        'required_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Referer': 'https://www.pararius.com/',
        }
    },
    'rentaroom': {
        'base_url': 'https://rent-a-room-delft.nl/grid-default/',
        'listings_selector': 'div.item-listing-wrap',
        'selectors': {
            'title': ('h2.item-title a', 'text', None),
            'price': ('li.item-price', 'text',
                      lambda t: int(re.sub(r'[^\d]', '', t.split('€')[-1]))),
            'rooms': ('li.h-beds span.hz-figure', 'text',
                      lambda t: int(t) if t else 0),
            'size': ('li.h-area span.hz-figure', 'text',
                     lambda t: int(t) if t else 0),
            'url': ('h2.item-title a', 'href', None),
            'rented': ('div.label-status', 'text', 
                      lambda t: 'rented' in t.lower() if t else False),
        },
        'paginator': 'page/{}/',
        'delay': (2, 5),
        'required_headers': {
            'Referer': 'https://rent-a-room-delft.nl/',
        }
    }
}