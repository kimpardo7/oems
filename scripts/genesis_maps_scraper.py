#!/usr/bin/env python3
"""
Genesis Dealerships Google Maps Scraper
Scrapes Genesis dealership information from Google Maps search results
"""

import asyncio
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright
import time

class GenesisMapsScraper:
    def __init__(self):
        self.dealerships = []
        self.base_url = "https://www.google.com/search?sca_esv=046dc2c9c0fa6748&tbm=lcl&sxsrf=AE3TifO-comEZ8bw6_XvlwpESQbOCOueag:1758160424081&q=genesis+dealerships+in+usa&rflfq=1&num=10&sa=X&ved=2ahUKEwimj6T8meGPAxWOCjQIHc39G4kQjGp6BAg0EAE&biw=1920&bih=992&dpr=1#rlfi=hd:;si:;mv:[[48.737734599999996,-72.0517989],[29.501963599999996,-125.64065969999999]];tbs:lrf:!1m4!1u3!2m2!3m1!1e1!2m1!1e3!3sIAE,lf:1,lf_ui:3"
        
    async def scrape_dealerships(self):
        """Main method to scrape Genesis dealerships from Google Maps"""
        async with async_playwright() as p:
            # Launch browser with specific settings for Google Maps
            browser = await p.chromium.launch(
                headless=False,  # Set to True for headless mode
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = await context.new_page()
            
            try:
                print("Navigating to Google Maps search...")
                await page.goto(self.base_url, wait_until='networkidle')
                await page.wait_for_timeout(3000)
                
                # Take a screenshot to see the initial state
                await page.screenshot(path='/Users/kimseanpardo/autodealerships/genesis_initial.png')
                print("Screenshot saved: genesis_initial.png")
                
                # Wait for the maps results to load
                print("Waiting for maps results to load...")
                await page.wait_for_timeout(5000)
                
                # Look for the main results container
                results_container = await page.query_selector('[data-value="Search results"]')
                if not results_container:
                    # Try alternative selectors
                    results_container = await page.query_selector('div[role="main"]')
                
                if results_container:
                    print("Found results container, extracting dealerships...")
                    await self.extract_dealerships_from_container(page, results_container)
                else:
                    print("No results container found, trying alternative approach...")
                    await self.extract_dealerships_alternative(page)
                
                # Take a final screenshot
                await page.screenshot(path='/Users/kimseanpardo/autodealerships/genesis_final.png')
                print("Final screenshot saved: genesis_final.png")
                
            except Exception as e:
                print(f"Error during scraping: {e}")
                await page.screenshot(path='/Users/kimseanpardo/autodealerships/genesis_error.png')
                print("Error screenshot saved: genesis_error.png")
            
            finally:
                await browser.close()
    
    async def extract_dealerships_from_container(self, page, container):
        """Extract dealerships from the main results container"""
        try:
            # Look for individual dealership cards
            dealership_cards = await container.query_selector_all('[data-value="Search results"] > div')
            
            if not dealership_cards:
                # Try alternative selectors for dealership cards
                dealership_cards = await page.query_selector_all('div[data-value="Search results"] div[jsaction]')
            
            print(f"Found {len(dealership_cards)} potential dealership cards")
            
            for i, card in enumerate(dealership_cards):
                try:
                    dealership_data = await self.extract_dealership_data(page, card, i)
                    if dealership_data:
                        self.dealerships.append(dealership_data)
                        print(f"Extracted dealership {i+1}: {dealership_data.get('name', 'Unknown')}")
                except Exception as e:
                    print(f"Error extracting dealership {i+1}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in extract_dealerships_from_container: {e}")
    
    async def extract_dealerships_alternative(self, page):
        """Alternative method to extract dealerships when main container approach fails"""
        try:
            # Look for any elements that might contain dealership information
            potential_dealerships = await page.query_selector_all('div[role="article"]')
            
            if not potential_dealerships:
                potential_dealerships = await page.query_selector_all('div[jsaction*="click"]')
            
            print(f"Found {len(potential_dealerships)} potential dealership elements")
            
            for i, element in enumerate(potential_dealerships):
                try:
                    dealership_data = await self.extract_dealership_data(page, element, i)
                    if dealership_data:
                        self.dealerships.append(dealership_data)
                        print(f"Extracted dealership {i+1}: {dealership_data.get('name', 'Unknown')}")
                except Exception as e:
                    print(f"Error extracting dealership {i+1}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in extract_dealerships_alternative: {e}")
    
    async def extract_dealership_data(self, page, element, index):
        """Extract data from a single dealership element"""
        try:
            dealership_data = {
                'index': index,
                'name': '',
                'address': '',
                'phone': '',
                'rating': '',
                'reviews_count': '',
                'website': '',
                'hours': '',
                'category': 'Genesis Dealership'
            }
            
            # Extract name
            name_element = await element.query_selector('h3, [role="heading"], .fontHeadlineSmall')
            if name_element:
                dealership_data['name'] = await name_element.inner_text()
            
            # Extract address
            address_element = await element.query_selector('[data-value="Address"], .fontBodyMedium')
            if address_element:
                dealership_data['address'] = await address_element.inner_text()
            
            # Extract phone
            phone_element = await element.query_selector('[data-value="Phone number"], [href^="tel:"]')
            if phone_element:
                phone_text = await phone_element.inner_text()
                dealership_data['phone'] = phone_text
            
            # Extract rating
            rating_element = await element.query_selector('[aria-label*="stars"], .fontDisplayLarge')
            if rating_element:
                rating_text = await rating_element.inner_text()
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    dealership_data['rating'] = rating_match.group(1)
            
            # Extract reviews count
            reviews_element = await element.query_selector('[aria-label*="reviews"]')
            if reviews_element:
                reviews_text = await reviews_element.inner_text()
                reviews_match = re.search(r'(\d+)', reviews_text)
                if reviews_match:
                    dealership_data['reviews_count'] = reviews_match.group(1)
            
            # Extract website
            website_element = await element.query_selector('[data-value="Website"], [href*="http"]')
            if website_element:
                href = await website_element.get_attribute('href')
                if href and href.startswith('http'):
                    dealership_data['website'] = href
            
            # Only return if we have at least a name
            if dealership_data['name']:
                return dealership_data
            else:
                return None
                
        except Exception as e:
            print(f"Error extracting dealership data: {e}")
            return None
    
    def save_results(self):
        """Save the scraped results to a JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/Users/kimseanpardo/autodealerships/data/genesis_dealers_{timestamp}.json"
        
        results = {
            'scrape_date': datetime.now().isoformat(),
            'total_dealerships': len(self.dealerships),
            'dealerships': self.dealerships
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to: {filename}")
        return filename

async def main():
    """Main function to run the scraper"""
    scraper = GenesisMapsScraper()
    
    print("Starting Genesis dealerships scraper...")
    print(f"Target URL: {scraper.base_url}")
    
    await scraper.scrape_dealerships()
    
    if scraper.dealerships:
        print(f"\nSuccessfully scraped {len(scraper.dealerships)} Genesis dealerships")
        filename = scraper.save_results()
        
        # Print summary
        print("\nDealership Summary:")
        for i, dealer in enumerate(scraper.dealerships, 1):
            print(f"{i}. {dealer.get('name', 'Unknown')} - {dealer.get('address', 'No address')}")
    else:
        print("No dealerships were scraped. Check the screenshots for debugging.")

if __name__ == "__main__":
    asyncio.run(main())
