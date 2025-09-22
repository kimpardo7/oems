#!/usr/bin/env python3
"""
Comprehensive Volkswagen Dealer Collection Script
This script will systematically search each US state and collect all dealer data.
"""

import json
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# US States list
US_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
    "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
    "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
    "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia",
    "Washington", "West Virginia", "Wisconsin", "Wyoming"
]

def setup_driver():
    """Setup Chrome driver with appropriate options"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def search_state_dealers(driver, state):
    """Search for dealers in a specific state"""
    print(f"Searching for dealers in {state}...")
    
    try:
        # Navigate to the dealer search page
        driver.get("https://www.vw.com/en/dealer-search.html?---=%7B%22dealer-search_featureappsection%22%3A%22%2F%22%7D")
        
        # Wait for page to load
        wait = WebDriverWait(driver, 10)
        search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[role="combobox"]')))
        
        # Clear and type state name
        search_input.clear()
        search_input.send_keys(state)
        
        # Wait for suggestions to appear
        time.sleep(2)
        
        # Click on the first state suggestion
        try:
            state_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{state}, USA')]")))
            state_option.click()
        except TimeoutException:
            # Try alternative selector
            state_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{state}')]")))
            state_option.click()
        
        # Wait for dealers to load
        time.sleep(3)
        
        # Extract dealer information
        dealers = extract_dealer_info(driver)
        
        print(f"Found {len(dealers)} dealers in {state}")
        return dealers
        
    except Exception as e:
        print(f"Error searching {state}: {str(e)}")
        return []

def extract_dealer_info(driver):
    """Extract dealer information from the current page"""
    dealers = []
    
    try:
        # Look for dealer buttons on the map
        dealer_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[aria-label*="Volkswagen"], button[aria-label*="VW"]')
        
        for button in dealer_buttons:
            try:
                name = button.get_attribute('aria-label') or button.text.strip()
                if name and ('Volkswagen' in name or 'VW' in name):
                    # Clean up the name
                    clean_name = name.replace('More information ', '').strip()
                    
                    dealers.append({
                        'name': clean_name,
                        'address': '',
                        'phone': '',
                        'hours': '',
                        'services': [],
                        'rating': '',
                        'reviews': '',
                        'distance': ''
                    })
            except Exception as e:
                continue
        
        # Also try to get detailed info from visible dealer panels
        try:
            dealer_panels = driver.find_elements(By.CSS_SELECTOR, 'group[cursor="pointer"]')
            for panel in dealer_panels:
                try:
                    # Extract detailed information
                    name_el = panel.find_element(By.CSS_SELECTOR, 'generic[ref*="e1"]')
                    name = name_el.text.strip() if name_el else ''
                    
                    address_el = panel.find_element(By.CSS_SELECTOR, 'paragraph[ref*="e1"]')
                    address = address_el.text.strip() if address_el else ''
                    
                    phone_el = panel.find_element(By.CSS_SELECTOR, 'link[href^="tel:"]')
                    phone = phone_el.text.strip() if phone_el else ''
                    
                    # Update existing dealer or add new one
                    existing_dealer = next((d for d in dealers if d['name'] == name), None)
                    if existing_dealer:
                        existing_dealer.update({
                            'address': address,
                            'phone': phone
                        })
                    else:
                        dealers.append({
                            'name': name,
                            'address': address,
                            'phone': phone,
                            'hours': '',
                            'services': [],
                            'rating': '',
                            'reviews': '',
                            'distance': ''
                        })
                except Exception as e:
                    continue
        except Exception as e:
            pass
            
    except Exception as e:
        print(f"Error extracting dealer info: {str(e)}")
    
    return dealers

def main():
    """Main function to collect all dealer data"""
    print("Starting comprehensive Volkswagen dealer collection...")
    
    # Load existing data
    try:
        with open('/Users/kimseanpardo/autodealerships/data/volkswagen.json', 'r') as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = {
            "brand": "Volkswagen",
            "total_dealers": 0,
            "states": {}
        }
    
    driver = setup_driver()
    all_dealers = {}
    
    try:
        for state in US_STATES:
            print(f"\nProcessing {state}...")
            
            # Skip if we already have data for this state
            if state in existing_data.get('states', {}):
                print(f"State {state} already processed, skipping...")
                continue
            
            dealers = search_state_dealers(driver, state)
            
            if dealers:
                all_dealers[state] = {
                    'state': state,
                    'total_dealers': len(dealers),
                    'dealers': dealers
                }
                print(f"Collected {len(dealers)} dealers from {state}")
            else:
                print(f"No dealers found for {state}")
            
            # Add random delay to avoid being blocked
            time.sleep(random.uniform(2, 5))
        
        # Update existing data
        if 'states' not in existing_data:
            existing_data['states'] = {}
        
        existing_data['states'].update(all_dealers)
        
        # Calculate total dealers
        total_dealers = sum(state_data['total_dealers'] for state_data in existing_data['states'].values())
        existing_data['total_dealers'] = total_dealers
        
        # Save updated data
        with open('/Users/kimseanpardo/autodealerships/data/volkswagen.json', 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        print(f"\nCollection complete! Total dealers collected: {total_dealers}")
        print(f"Data saved to /Users/kimseanpardo/autodealerships/data/volkswagen.json")
        
    except Exception as e:
        print(f"Error during collection: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()