#!/usr/bin/env python3
"""
Infiniti Debug Script
Analyzes the page structure to understand how to interact with the retailer locator
"""

import time
from playwright.sync_api import sync_playwright

def debug_infiniti_page():
    """Debug the Infiniti page structure"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_default_timeout(60000)
        
        try:
            print("Navigating to Infiniti retailer locator...")
            page.goto("https://www.infinitiusa.com/retailer-locator.html", 
                     wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)
            
            print("Taking screenshot...")
            page.screenshot(path="infiniti_debug_initial.png")
            
            # Get page title and URL
            title = page.title()
            url = page.url
            print(f"Page title: {title}")
            print(f"Current URL: {url}")
            
            # Find all input fields
            print("\n=== INPUT FIELDS ===")
            inputs = page.locator('input')
            input_count = inputs.count()
            print(f"Found {input_count} input fields:")
            
            for i in range(input_count):
                try:
                    input_elem = inputs.nth(i)
                    if input_elem.is_visible():
                        placeholder = input_elem.get_attribute('placeholder') or 'No placeholder'
                        input_type = input_elem.get_attribute('type') or 'No type'
                        name = input_elem.get_attribute('name') or 'No name'
                        id_attr = input_elem.get_attribute('id') or 'No id'
                        class_attr = input_elem.get_attribute('class') or 'No class'
                        
                        print(f"  Input {i}:")
                        print(f"    Placeholder: {placeholder}")
                        print(f"    Type: {input_type}")
                        print(f"    Name: {name}")
                        print(f"    ID: {id_attr}")
                        print(f"    Class: {class_attr}")
                        print()
                except Exception as e:
                    print(f"  Error reading input {i}: {e}")
            
            # Find all buttons
            print("\n=== BUTTONS ===")
            buttons = page.locator('button')
            button_count = buttons.count()
            print(f"Found {button_count} buttons:")
            
            for i in range(button_count):
                try:
                    button_elem = buttons.nth(i)
                    if button_elem.is_visible():
                        text = button_elem.text_content() or 'No text'
                        type_attr = button_elem.get_attribute('type') or 'No type'
                        class_attr = button_elem.get_attribute('class') or 'No class'
                        
                        print(f"  Button {i}:")
                        print(f"    Text: {text}")
                        print(f"    Type: {type_attr}")
                        print(f"    Class: {class_attr}")
                        print()
                except Exception as e:
                    print(f"  Error reading button {i}: {e}")
            
            # Look for specific elements mentioned in the user query
            print("\n=== LOOKING FOR SPECIFIC ELEMENTS ===")
            
            # Look for the menu item mentioned in the user query
            menu_selectors = [
                'button[data-panel="Retailer_Locator"]',
                'button:has-text("Retailer Locator")',
                '.c_320-menu-link',
                'button[role="menuitem"]'
            ]
            
            for selector in menu_selectors:
                try:
                    element = page.locator(selector)
                    if element.count() > 0:
                        print(f"Found element with selector: {selector}")
                        if element.first.is_visible():
                            print(f"  Element is visible")
                            text = element.first.text_content() or 'No text'
                            print(f"  Text: {text}")
                        else:
                            print(f"  Element is not visible")
                except Exception as e:
                    print(f"  Error with selector {selector}: {e}")
            
            # Look for the predict-input mentioned in the user query
            predict_selectors = [
                '.predict-input',
                'input[name="predict-input"]',
                '.predict-input_field',
                'input[autocomplete="postal-code"]'
            ]
            
            for selector in predict_selectors:
                try:
                    element = page.locator(selector)
                    if element.count() > 0:
                        print(f"Found predict-input element with selector: {selector}")
                        if element.first.is_visible():
                            print(f"  Element is visible")
                        else:
                            print(f"  Element is not visible")
                except Exception as e:
                    print(f"  Error with selector {selector}: {e}")
            
            # Get page HTML to analyze structure
            print("\n=== PAGE HTML ANALYSIS ===")
            html_content = page.content()
            
            # Look for key terms in the HTML
            key_terms = ['predict-input', 'Retailer_Locator', 'zip', 'postal-code', 'search']
            for term in key_terms:
                if term.lower() in html_content.lower():
                    print(f"Found '{term}' in page HTML")
                else:
                    print(f"'{term}' NOT found in page HTML")
            
            # Save HTML for manual inspection
            with open("infiniti_page_source.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print("\nPage HTML saved to infiniti_page_source.html")
            
        except Exception as e:
            print(f"Error during debug: {e}")
            page.screenshot(path="infiniti_debug_error.png")
        
        finally:
            browser.close()

if __name__ == "__main__":
    debug_infiniti_page()
