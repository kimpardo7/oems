#!/usr/bin/env python3
"""
Comprehensive Subaru Dealer Scraper
Scrapes ALL Subaru dealers using the official API with extensive zip code coverage
"""

import requests
import json
import time
import random
from typing import List, Dict, Set
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveSubaruDealerScraper:
    def __init__(self):
        self.base_url = "https://www.subaru.com/services/dealers/distances/by/zipcode"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.subaru.com/find/a-retailer.html'
        })
        self.dealers = {}
        self.processed_zips = set()
        self.lock = threading.Lock()
        
        # Comprehensive zip code list covering all US states and territories
        self.zip_codes = [
            # Major metropolitan areas
            '10001', '10002', '10003', '10004', '10005',  # NYC
            '90210', '90211', '90212', '90401', '90402',  # LA
            '60601', '60602', '60603', '60604', '60605',  # Chicago
            '77001', '77002', '77003', '77004', '77005',  # Houston
            '33101', '33102', '33103', '33104', '33105',  # Miami
            '85001', '85002', '85003', '85004', '85005',  # Phoenix
            '98101', '98102', '98103', '98104', '98105',  # Seattle
            '80201', '80202', '80203', '80204', '80205',  # Denver
            '02101', '02102', '02103', '02104', '02105',  # Boston
            '20001', '20002', '20003', '20004', '20005',  # DC
            
            # State capitals and major cities
            '30301', '30302', '30303', '30304', '30305',  # Atlanta
            '28201', '28202', '28203', '28204', '28205',  # Charlotte
            '27601', '27602', '27603', '27604', '27605',  # Raleigh
            '32201', '32202', '32203', '32204', '32205',  # Jacksonville
            '33601', '33602', '33603', '33604', '33605',  # Tampa
            '37201', '37202', '37203', '37204', '37205',  # Nashville
            '46201', '46202', '46203', '46204', '46205',  # Indianapolis
            '43201', '43202', '43203', '43204', '43205',  # Columbus
            '53201', '53202', '53203', '53204', '53205',  # Milwaukee
            '55401', '55402', '55403', '55404', '55405',  # Minneapolis
            '64101', '64102', '64103', '64104', '64105',  # Kansas City
            '63101', '63102', '63103', '63104', '63105',  # St. Louis
            '75201', '75202', '75203', '75204', '75205',  # Dallas
            '70112', '70113', '70114', '70115', '70116',  # New Orleans
            '84101', '84102', '84103', '84104', '84105',  # Salt Lake City
            '87101', '87102', '87103', '87104', '87105',  # Albuquerque
            '83701', '83702', '83703', '83704', '83705',  # Boise
            '59101', '59102', '59103', '59104', '59105',  # Billings
            '57101', '57102', '57103', '57104', '57105',  # Sioux Falls
            '58101', '58102', '58103', '58104', '58105',  # Fargo
            '99501', '99502', '99503', '99504', '99505',  # Anchorage
            '96801', '96802', '96803', '96804', '96805',  # Honolulu
            '96701', '96702', '96703', '96704', '96705',  # Hilo
            '99801', '99802', '99803', '99804', '99805',  # Juneau
            '99701', '99702', '99703', '99704', '99705',  # Fairbanks
            '99901', '99902', '99903', '99904', '99905',  # Ketchikan
            
            # Additional coverage for smaller states and regions
            '21201', '21202', '21203', '21204', '21205',  # Baltimore
            '02101', '02102', '02103', '02104', '02105',  # Boston
            '06101', '06102', '06103', '06104', '06105',  # Hartford
            '19901', '19902', '19903', '19904', '19905',  # Dover
            '20001', '20002', '20003', '20004', '20005',  # Washington DC
            '33101', '33102', '33103', '33104', '33105',  # Miami
            '30301', '30302', '30303', '30304', '30305',  # Atlanta
            '83701', '83702', '83703', '83704', '83705',  # Boise
            '60601', '60602', '60603', '60604', '60605',  # Chicago
            '46201', '46202', '46203', '46204', '46205',  # Indianapolis
            '50301', '50302', '50303', '50304', '50305',  # Des Moines
            '66101', '66102', '66103', '66104', '66105',  # Kansas City
            '40201', '40202', '40203', '40204', '40205',  # Louisville
            '70112', '70113', '70114', '70115', '70116',  # New Orleans
            '04101', '04102', '04103', '04104', '04105',  # Portland ME
            '21201', '21202', '21203', '21204', '21205',  # Baltimore
            '02101', '02102', '02103', '02104', '02105',  # Boston
            '48201', '48202', '48203', '48204', '48205',  # Detroit
            '55401', '55402', '55403', '55404', '55405',  # Minneapolis
            '39201', '39202', '39203', '39204', '39205',  # Jackson
            '64101', '64102', '64103', '64104', '64105',  # Kansas City
            '59101', '59102', '59103', '59104', '59105',  # Billings
            '68101', '68102', '68103', '68104', '68105',  # Omaha
            '89101', '89102', '89103', '89104', '89105',  # Las Vegas
            '03101', '03102', '03103', '03104', '03105',  # Manchester
            '07101', '07102', '07103', '07104', '07105',  # Newark
            '87101', '87102', '87103', '87104', '87105',  # Albuquerque
            '10001', '10002', '10003', '10004', '10005',  # New York
            '27601', '27602', '27603', '27604', '27605',  # Raleigh
            '58101', '58102', '58103', '58104', '58105',  # Fargo
            '43201', '43202', '43203', '43204', '43205',  # Columbus
            '73101', '73102', '73103', '73104', '73105',  # Oklahoma City
            '97201', '97202', '97203', '97204', '97205',  # Portland OR
            '19101', '19102', '19103', '19104', '19105',  # Philadelphia
            '02901', '02902', '02903', '02904', '02905',  # Providence
            '29201', '29202', '29203', '29204', '29205',  # Columbia
            '57101', '57102', '57103', '57104', '57105',  # Sioux Falls
            '37201', '37202', '37203', '37204', '37205',  # Nashville
            '75201', '75202', '75203', '75204', '75205',  # Dallas
            '84101', '84102', '84103', '84104', '84105',  # Salt Lake City
            '05401', '05402', '05403', '05404', '05405',  # Burlington
            '23201', '23202', '23203', '23204', '23205',  # Richmond
            '98101', '98102', '98103', '98104', '98105',  # Seattle
            '25301', '25302', '25303', '25304', '25305',  # Charleston WV
            '53201', '53202', '53203', '53204', '53205',  # Milwaukee
            '82001', '82002', '82003', '82004', '82005',  # Cheyenne
            
            # Additional random zip codes for comprehensive coverage
            '10010', '10011', '10012', '10013', '10014',  # More NYC
            '90220', '90221', '90222', '90223', '90224',  # More LA
            '60610', '60611', '60612', '60613', '60614',  # More Chicago
            '77010', '77011', '77012', '77013', '77014',  # More Houston
            '33110', '33111', '33112', '33113', '33114',  # More Miami
            '85010', '85011', '85012', '85013', '85014',  # More Phoenix
            '98110', '98111', '98112', '98113', '98114',  # More Seattle
            '80210', '80211', '80212', '80213', '80214',  # More Denver
            '02110', '02111', '02112', '02113', '02114',  # More Boston
            '20010', '20011', '20012', '20013', '20014',  # More DC
            '30310', '30311', '30312', '30313', '30314',  # More Atlanta
            '28210', '28211', '28212', '28213', '28214',  # More Charlotte
            '27610', '27611', '27612', '27613', '27614',  # More Raleigh
            '32210', '32211', '32212', '32213', '32214',  # More Jacksonville
            '33610', '33611', '33612', '33613', '33614',  # More Tampa
            '37210', '37211', '37212', '37213', '37214',  # More Nashville
            '46210', '46211', '46212', '46213', '46214',  # More Indianapolis
            '43210', '43211', '43212', '43213', '43214',  # More Columbus
            '53210', '53211', '53212', '53213', '53214',  # More Milwaukee
            '55410', '55411', '55412', '55413', '55414',  # More Minneapolis
            '64110', '64111', '64112', '64113', '64114',  # More Kansas City
            '63110', '63111', '63112', '63113', '63114',  # More St. Louis
            '75210', '75211', '75212', '75213', '75214',  # More Dallas
            '70120', '70121', '70122', '70123', '70124',  # More New Orleans
            '84110', '84111', '84112', '84113', '84114',  # More Salt Lake City
            '87110', '87111', '87112', '87113', '87114',  # More Albuquerque
            '83710', '83711', '83712', '83713', '83714',  # More Boise
            '59110', '59111', '59112', '59113', '59114',  # More Billings
            '57110', '57111', '57112', '57113', '57114',  # More Sioux Falls
            '58110', '58111', '58112', '58113', '58114',  # More Fargo
            '99510', '99511', '99512', '99513', '99514',  # More Anchorage
            '96810', '96811', '96812', '96813', '96814',  # More Honolulu
            '96710', '96711', '96712', '96713', '96714',  # More Hilo
            '99810', '99811', '99812', '99813', '99814',  # More Juneau
            '99710', '99711', '99712', '99713', '99714',  # More Fairbanks
            '99910', '99911', '99912', '99913', '99914',  # More Ketchikan
        ]
        
    def get_dealers_by_zip(self, zip_code: str, count: int = 100) -> List[Dict]:
        """Get dealers for a specific zip code"""
        try:
            params = {
                'zipcode': zip_code,
                'count': count,
                'type': 'Active'
            }
            
            response = self.session.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Found {len(data)} dealers for zip {zip_code}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching dealers for zip {zip_code}: {e}")
            return []
    
    def extract_dealer_info(self, dealer_data: Dict) -> Dict:
        """Extract and clean dealer information"""
        dealer = dealer_data.get('dealer', {})
        distance = dealer_data.get('distance', 0)
        
        return {
            'id': dealer.get('id'),
            'name': dealer.get('name'),
            'address': {
                'street': dealer.get('address', {}).get('street'),
                'street2': dealer.get('address', {}).get('street2'),
                'city': dealer.get('address', {}).get('city'),
                'state': dealer.get('address', {}).get('state'),
                'zipcode': dealer.get('address', {}).get('zipcode'),
                'county': dealer.get('address', {}).get('county')
            },
            'phone': dealer.get('phoneNumber'),
            'service_phone': dealer.get('servicePhoneNumber'),
            'fax': dealer.get('faxNumber'),
            'website': dealer.get('siteUrl'),
            'location': {
                'latitude': dealer.get('location', {}).get('latitude'),
                'longitude': dealer.get('location', {}).get('longitude'),
                'region': dealer.get('location', {}).get('region'),
                'zone': dealer.get('location', {}).get('zone'),
                'district': dealer.get('location', {}).get('district')
            },
            'services': dealer.get('types', []),
            'distance_miles': distance
        }
    
    def process_zip_batch(self, zip_codes_batch: List[str]) -> Dict[str, Dict]:
        """Process a batch of zip codes"""
        batch_dealers = {}
        
        for zip_code in zip_codes_batch:
            if zip_code in self.processed_zips:
                continue
                
            logger.info(f"Processing zip code: {zip_code}")
            dealers_data = self.get_dealers_by_zip(zip_code, 100)
            
            for dealer_data in dealers_data:
                dealer_info = self.extract_dealer_info(dealer_data)
                dealer_id = dealer_info['id']
                
                if dealer_id and dealer_id not in batch_dealers:
                    batch_dealers[dealer_id] = dealer_info
                    logger.info(f"Added dealer: {dealer_info['name']} in {dealer_info['address']['city']}, {dealer_info['address']['state']}")
            
            self.processed_zips.add(zip_code)
            time.sleep(random.uniform(0.3, 0.8))  # Rate limiting
        
        return batch_dealers
    
    def scrape_all_dealers(self):
        """Scrape dealers from comprehensive zip code list"""
        logger.info(f"Starting comprehensive scraping from {len(self.zip_codes)} zip codes")
        
        # Process in batches to avoid overwhelming the API
        batch_size = 10
        zip_batches = [self.zip_codes[i:i + batch_size] for i in range(0, len(self.zip_codes), batch_size)]
        
        for i, batch in enumerate(zip_batches):
            logger.info(f"Processing batch {i+1}/{len(zip_batches)} ({len(batch)} zip codes)")
            
            batch_dealers = self.process_zip_batch(batch)
            
            # Merge with main dealers dict
            with self.lock:
                self.dealers.update(batch_dealers)
                logger.info(f"Total unique dealers so far: {len(self.dealers)}")
            
            # Longer pause between batches
            time.sleep(random.uniform(2, 4))
        
        logger.info(f"Comprehensive scraping complete. Found {len(self.dealers)} unique dealers")
    
    def save_to_json(self, filename: str = 'subaru_comprehensive.json'):
        """Save dealers to JSON file"""
        dealers_list = list(self.dealers.values())
        
        # Sort by state, then city, then name
        dealers_list.sort(key=lambda x: (x['address']['state'], x['address']['city'], x['name']))
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dealers_list, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(dealers_list)} dealers to {filename}")
    
    def get_statistics(self):
        """Get statistics about collected dealers"""
        if not self.dealers:
            return {}
        
        states = {}
        services = {}
        
        for dealer in self.dealers.values():
            state = dealer['address']['state']
            states[state] = states.get(state, 0) + 1
            
            for service in dealer['services']:
                services[service] = services.get(service, 0) + 1
        
        return {
            'total_dealers': len(self.dealers),
            'states': dict(sorted(states.items())),
            'top_services': dict(sorted(services.items(), key=lambda x: x[1], reverse=True)[:10])
        }

def main():
    scraper = ComprehensiveSubaruDealerScraper()
    
    try:
        scraper.scrape_all_dealers()
        scraper.save_to_json('subaru_comprehensive.json')
        
        stats = scraper.get_statistics()
        print(f"\n🎉 COMPREHENSIVE SCRAPING COMPLETE!")
        print(f"📊 Total dealers found: {stats['total_dealers']}")
        print(f"🗺️  States covered: {len(stats['states'])}")
        print(f"🏆 Top 10 states by dealer count:")
        for state, count in list(stats['states'].items())[:10]:
            print(f"  {state}: {count} dealers")
        
        print(f"\n🔧 Top 10 service types:")
        for service, count in list(stats['top_services'].items())[:10]:
            print(f"  {service}: {count} dealers")
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        scraper.save_to_json('subaru_comprehensive_partial.json')
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        scraper.save_to_json('subaru_comprehensive_error.json')

if __name__ == "__main__":
    main()
