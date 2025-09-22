#!/usr/bin/env python3
"""
Genesis Dealerships HTML Parser
Parses the provided HTML to extract Genesis dealership information
"""

import json
import re
from datetime import datetime
from bs4 import BeautifulSoup

class GenesisHTMLParser:
    def __init__(self):
        self.dealerships = []
    
    def parse_html(self, html_content):
        """Parse the HTML content to extract dealership information"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all dealership containers
        containers = soup.find_all('div', {'jscontroller': 'AtSb'})
        
        print(f"Found {len(containers)} dealership containers")
        
        for i, container in enumerate(containers):
            try:
                dealership_data = self.extract_dealership_data(container, i)
                if dealership_data and dealership_data.get('name'):
                    self.dealerships.append(dealership_data)
                    print(f"Extracted dealership {len(self.dealerships)}: {dealership_data['name']}")
            except Exception as e:
                print(f"Error extracting dealership {i+1}: {e}")
                continue
    
    def extract_dealership_data(self, container, index):
        """Extract data from a single dealership container"""
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
                'status': '',
                'category': 'Genesis Dealership',
                'latitude': '',
                'longitude': '',
                'review_text': ''
            }
            
            # Extract coordinates from hidden data
            coords_element = container.find('div', class_='rllt__mi')
            if coords_element:
                dealership_data['latitude'] = coords_element.get('data-lat', '')
                dealership_data['longitude'] = coords_element.get('data-lng', '')
            
            # Extract name from the heading
            name_element = container.find('span', class_='OSrXXb')
            if name_element:
                dealership_data['name'] = name_element.get_text(strip=True)
            
            # Extract details from the rllt__details section
            details_element = container.find('div', {'jsname': 'MZArnb'})
            if details_element:
                # Get all text content and split by lines
                details_text = details_element.get_text()
                lines = [line.strip() for line in details_text.split('\n') if line.strip()]
                
                # Parse each line
                for line in lines:
                    # Skip the name line (already extracted)
                    if line == dealership_data['name']:
                        continue
                    
                    # Check if it's a phone number
                    if re.match(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', line):
                        dealership_data['phone'] = line
                    # Check if it's an address (contains city, state pattern)
                    elif re.search(r'[A-Za-z\s]+,\s*[A-Z]{2}', line):
                        dealership_data['address'] = line
                    # Check if it's hours/status
                    elif any(word in line.lower() for word in ['open', 'closed', 'closes', 'opens']):
                        dealership_data['status'] = line
                        dealership_data['hours'] = line
                    # Check if it's a review text
                    elif line.startswith('"') and line.endswith('"'):
                        dealership_data['review_text'] = line.strip('"')
            
            # Extract website URL
            website_element = container.find('a', href=lambda x: x and 'http' in x and 'google.com' not in x)
            if website_element:
                dealership_data['website'] = website_element.get('href', '')
            
            # Only return if we have at least a name and it contains "Genesis"
            if dealership_data['name'] and 'genesis' in dealership_data['name'].lower():
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

def main():
    """Main function to parse the provided HTML"""
    # The HTML content you provided
    html_content = '''<div jscontroller="EfJGEe" class="rlfl__tls rl_tls" jsaction="rcuQ6b:npT2md"><div class="PiKi2c"></div><div jscontroller="AtSb" data-record-click-time="false" id="tsuid_MmbLaL_IF8Cc0PEPiNCF6Qc_13" jsdata="zt2wNd;_;MmbLaL_IF8Cc0PEPiNCF6Qc9 WDO8Ff;_;MmbLaL_IF8Cc0PEPiNCF6Qc13" jsaction="rcuQ6b:npT2md;e3EWke:kN9HDb;v1Cdnb:pFRkQb" data-hveid="CBwQAA"><div style="display:none" data-id="6260508931552110386" data-lat="45.4962707" data-lng="-122.76982790000001" class="rllt__mi"></div><div jsname="jXK9ad" class="uMdZh tIxNaf alUjuf rllt__borderless" jsaction="mouseover:UI3Kjd;mouseleave:Tx5Rb;focusin:UI3Kjd;focusout:Tx5Rb" style="padding-bottom: 8px; margin-bottom: -8px;"><div class="VkpGBb"><div class="cXedhc"><a class="vwVdIc wzN8Ac rllt__link a-no-hover-decoration" jsname="kj0dLd" data-cid="6260508931552110386" role="button" jsaction="click:h5M12e;" tabindex="0" data-ved="2ahUKEwi_qZmBmuGPAxVADjQIHQhoIX0QyTN6BAgcEAE"><div><div jsname="MZArnb" class="rllt__details"><div class="dbg0pd" aria-level="3" role="heading"><span class="OSrXXb">Genesis of Portland</span></div><div>Genesis dealer</div><div>Portland, OR · (971) 277-4958</div><div><span><span style="color:rgba(178,108,0,1.0)">Closes soon</span> ⋅ 7 PM</span></div><span style="display:block;margin-bottom:6px"></span><div class="pJ3Ci"><div class="FyvIhd RCQpbe"><span class="NmuOpc"><div class="NJiz raB6Pe"> <svg class="tZ3wY" height="16" width="16" aria-hidden="true" viewBox="0 0 10.169 10.169" xmlns="http://www.w3.org/2000/svg"> <circle cx="5.084" cy="5.085" fill="#a0c3ff" r="5.0843"></circle> <circle cx="5.133" cy="3.811" fill="#4374e0" r="2.014"></circle> <ellipse cx="5.064" cy="8.165" fill="#4374e0" rx="3.564" ry="1.8067"></ellipse> </svg>  </div></span><span class="uDyWh OSrXXb btbrud">"Jordon made our car buying experience painless and pressure free."</span></div></div></div></div></a></div><a class="yYlJEf Q7PwXb L48Cpd brKmxb" aria-describedby="tsuid_MmbLaL_IF8Cc0PEPiNCF6Qc_13" href="https://www.portlandgenesis.com/?utm_source=Google&amp;utm_medium=Organic&amp;utm_campaign=gbp_profile" data-ved="2ahUKEwi_qZmBmuGPAxVADjQIHQhoIX0QgU96BAgcEAg" ping="/url?sa=t&amp;source=web&amp;rct=j&amp;opi=89978449&amp;url=https://www.portlandgenesis.com/%3Futm_source%3DGoogle%26utm_medium%3DOrganic%26utm_campaign%3Dgbp_profile&amp;ved=2ahUKEwi_qZmBmuGPAxVADjQIHQhoIX0QgU96BAgcEAg"><div class="wLAgVc" style="display:flex;flex-direction:column;align-items:center;justify-content:center"><span class="XBBs5 z1asCe GYDk8c"><svg focusable="false" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"></path></svg></span><span class="BSaJxc">Website</span></div></a><a href="/maps/dir//Genesis+of+Portland,+9008+SW+Canyon+Rd,+Portland,+OR+97225/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x54950b4f54a38391:0x56e1cbb42252e732?sa=X&amp;ved=1t:57443&amp;ictx=111" style="cursor:pointer" data-url="/maps/dir//Genesis+of+Portland,+9008+SW+Canyon+Rd,+Portland,+OR+97225/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x54950b4f54a38391:0x56e1cbb42252e732?sa=X&amp;ved=2ahUKEwi_qZmBmuGPAxVADjQIHQhoIX0Q48ADegQICRAA" tabindex="0" class="yYlJEf Q7PwXb VDgVie brKmxb" aria-describedby="tsuid_MmbLaL_IF8Cc0PEPiNCF6Qc_13" ping="/url?sa=t&amp;source=web&amp;rct=j&amp;opi=89978449&amp;url=/maps/dir//Genesis%2Bof%2BPortland,%2B9008%2BSW%2BCanyon%2BRd,%2BPortland,%2BOR%2B97225/data%3D!4m6!4m5!1m1!4e2!1m2!1m1!1s0x54950b4f54a38391:0x56e1cbb42252e732%3Fsa%3DX%26ved%3D1t:57443%26ictx%3D111&amp;ved=2ahUKEwi_qZmBmuGPAxVADjQIHQhoIX0Q48ADegQIHBAJ"><div><div class="DgBJ7c"><span class="z1asCe QoWzUe"><svg focusable="false" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" enable-background="new 0 0 24 24" height="24" viewBox="0 0 24 24" width="24"><g><rect fill="none" height="24" width="24"></rect></g><g><path d="m21.41 10.59-7.99-8c-.78-.78-2.05-.78-2.83 0l-8.01 8c-.78.78-.78 2.05 0 2.83l8.01 8c.78.78 2.05.78 2.83 0l7.99-8c.79-.79.79-2.05 0-2.83zM13.5 14.5V12H10v3H8v-4c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"></path></g></svg></span><span class="UbRuwe">Directions</span></div></div></a></div></div></div>'''
    
    parser = GenesisHTMLParser()
    
    print("Parsing Genesis dealerships from HTML...")
    parser.parse_html(html_content)
    
    if parser.dealerships:
        print(f"\nSuccessfully parsed {len(parser.dealerships)} Genesis dealerships")
        filename = parser.save_results()
        
        # Print summary
        print("\nDealership Summary:")
        for i, dealer in enumerate(parser.dealerships, 1):
            print(f"{i}. {dealer.get('name', 'Unknown')} - {dealer.get('address', 'No address')} - {dealer.get('phone', 'No phone')}")
    else:
        print("No dealerships were parsed from the HTML.")

if __name__ == "__main__":
    main()
