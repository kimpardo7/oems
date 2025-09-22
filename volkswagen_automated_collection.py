#!/usr/bin/env python3
"""
Automated Volkswagen Dealer Collection Script
This script will systematically search each US state and collect all dealer data efficiently.
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
from selenium.webdriver.common.keys import Keys

# US States list
US_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
    "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
    "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma",
    "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming"
]

def setup_driver():
    """Setup Chrome driver with appropriate options"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def search_state_and_extract_dealers(driver, state_name):
    """Search for a specific state and extract dealer information"""
    try:
        print(f"Searching for dealers in {state_name}...")
        
        # Navigate to the dealer search page
        driver.get("https://www.vw.com/en/dealer-search.html?---=%7B%22dealer-search_featureappsection%22%3A%22%2F%22%7D")
        
        # Wait for page to load
        wait = WebDriverWait(driver, 10)
        search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[role="combobox"]')))
        
        # Clear and type state name
        search_input.clear()
        search_input.send_keys(state_name)
        
        # Wait for suggestions to appear
        time.sleep(2)
        
        # Click on the first state suggestion
        try:
            state_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{state_name}, USA')]")))
            state_option.click()
        except TimeoutException:
            # Try alternative selector
            state_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{state_name}')]")))
            state_option.click()
        
        # Wait for results to load
        time.sleep(3)
        
        # Extract dealer information
        dealers = []
        
        # Get all dealer buttons from the map
        dealer_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[aria-label*="Volkswagen"], button[aria-label*="VW"]')
        
        for button in dealer_buttons:
            try:
                dealer_name = button.get_attribute('aria-label') or button.text.strip()
                if dealer_name and ('Volkswagen' in dealer_name or 'VW' in dealer_name):
                    # Clean up the name
                    clean_name = dealer_name.replace('More information ', '').strip()
                    if clean_name and len(clean_name) > 5:
                        dealers.append({
                            "name": clean_name,
                            "address": "",
                            "phone": "",
                            "hours": "",
                            "services": [],
                            "rating": "",
                            "reviews": "",
                            "distance": ""
                        })
            except Exception as e:
                continue
        
        # Also try to extract from visible text elements
        try:
            all_buttons = driver.find_elements(By.TAG_NAME, 'button')
            for button in all_buttons:
                text = button.text.strip()
                if text and ('Volkswagen' in text or 'VW' in text) and len(text) > 5:
                    if not any(d['name'] == text for d in dealers):
                        dealers.append({
                            "name": text,
                            "address": "",
                            "phone": "",
                            "hours": "",
                            "services": [],
                            "rating": "",
                            "reviews": "",
                            "distance": ""
                        })
        except Exception as e:
            pass
        
        # Try to get detailed information from dealer panels
        try:
            dealer_panels = driver.find_elements(By.CSS_SELECTOR, 'group[cursor="pointer"]')
            for panel in dealer_panels:
                try:
                    # Extract detailed info
                    name_el = panel.find_element(By.CSS_SELECTOR, 'generic[ref*="e"]')
                    if name_el:
                        name = name_el.text.strip()
                        if name:
                            # Find existing dealer or create new one
                            existing_dealer = next((d for d in dealers if d['name'] == name), None)
                            if not existing_dealer:
                                existing_dealer = {
                                    "name": name,
                                    "address": "",
                                    "phone": "",
                                    "hours": "",
                                    "services": [],
                                    "rating": "",
                                    "reviews": "",
                                    "distance": ""
                                }
                                dealers.append(existing_dealer)
                            
                            # Try to extract additional details
                            try:
                                address_el = panel.find_element(By.CSS_SELECTOR, 'paragraph[ref*="e"]')
                                if address_el:
                                    existing_dealer['address'] = address_el.text.strip()
                            except:
                                pass
                            
                            try:
                                phone_el = panel.find_element(By.CSS_SELECTOR, 'link[href^="tel:"]')
                                if phone_el:
                                    existing_dealer['phone'] = phone_el.text.strip()
                            except:
                                pass
                            
                            try:
                                hours_el = panel.find_element(By.CSS_SELECTOR, 'generic[ref*="e"]')
                                if hours_el and 'Closed' in hours_el.text:
                                    existing_dealer['hours'] = hours_el.text.strip()
                            except:
                                pass
                                
                except Exception as e:
                    continue
        except Exception as e:
            pass
        
        # Remove duplicates
        unique_dealers = []
        seen_names = set()
        for dealer in dealers:
            if dealer['name'] not in seen_names:
                unique_dealers.append(dealer)
                seen_names.add(dealer['name'])
        
        print(f"Found {len(unique_dealers)} dealers in {state_name}")
        return unique_dealers
        
    except Exception as e:
        print(f"Error searching {state_name}: {str(e)}")
        return []

def main():
    """Main function to collect all dealer data"""
    driver = setup_driver()
    all_dealers = {}
    total_dealers = 0
    
    try:
        for state in US_STATES:
            dealers = search_state_and_extract_dealers(driver, state)
            if dealers:
                all_dealers[state] = {
                    "state": state,
                    "total_dealers": len(dealers),
                    "dealers": dealers
                }
                total_dealers += len(dealers)
                print(f"✓ {state}: {len(dealers)} dealers")
            else:
                print(f"✗ {state}: No dealers found")
            
            # Small delay between states
            time.sleep(random.uniform(1, 3))
        
        # Create final data structure
        final_data = {
            "oem": "Volkswagen",
            "zip_code": "multiple",
            "total_dealers_found": total_dealers,
            "method": "automated_state_search",
            "states_searched": len(all_dealers),
            "states": all_dealers
        }
        
        # Save to file
        with open('/Users/kimseanpardo/autodealerships/data/volkswagen_complete.json', 'w') as f:
            json.dump(final_data, f, indent=2)
        
        print(f"\n✅ Collection complete!")
        print(f"Total dealers found: {total_dealers}")
        print(f"States searched: {len(all_dealers)}")
        print(f"Data saved to: volkswagen_complete.json")
        
    except Exception as e:
        print(f"Error in main process: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

