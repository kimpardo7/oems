#!/usr/bin/env python3
"""
Convert Toyota dealer data to match Chrysler format
Removes complex fields and massive source_zips arrays
"""

import json
import os
import sys

try:
    import ijson
except ImportError:
    print("ijson not available, trying standard json...")
    ijson = None

def convert_toyota_to_chrysler_format():
    """Convert Toyota data to match Chrysler format"""
    
    # Read Toyota data
    toyota_file = "data/toyota.json"
    if not os.path.exists(toyota_file):
        print(f"Error: {toyota_file} not found")
        return
    
    print("Reading Toyota data...")
    
    if ijson:
        return convert_with_ijson(toyota_file)
    else:
        return convert_with_standard_json(toyota_file)

def convert_with_ijson(toyota_file):
    """Convert using ijson streaming parser"""
    print("Using ijson streaming parser...")
    
    chrysler_format = {
        "oem": "Toyota",
        "zip_code": "multiple",
        "total_dealers_found": 0,
        "method": "converted_from_toyota_format_ijson",
        "dealers": []
    }
    
    dealer_count = 0
    
    try:
        with open(toyota_file, 'rb') as f:
            # Parse each dealer object in the array
            parser = ijson.parse(f)
            
            current_dealer = {}
            in_dealer = False
            current_key = None
            
            for prefix, event, value in parser:
                if prefix == '' and event == 'start_array':
                    continue
                elif prefix.endswith('.dealer_code') and event == 'string':
                    if current_dealer:
                        # Save previous dealer
                        converted_dealer = convert_dealer_to_chrysler_format(current_dealer)
                        if converted_dealer:
                            chrysler_format["dealers"].append(converted_dealer)
                            dealer_count += 1
                    current_dealer = {"dealer_code": value}
                    in_dealer = True
                elif in_dealer and prefix.endswith('.name') and event == 'string':
                    current_dealer["name"] = value
                elif in_dealer and prefix.endswith('.website') and event == 'string':
                    current_dealer["website"] = value
                elif in_dealer and prefix.endswith('.phone') and event == 'string':
                    current_dealer["phone"] = value
                elif in_dealer and prefix.endswith('.email') and event == 'string':
                    current_dealer["email"] = value
                elif in_dealer and prefix.endswith('.address.street') and event == 'string':
                    if "address" not in current_dealer:
                        current_dealer["address"] = {}
                    current_dealer["address"]["street"] = value
                elif in_dealer and prefix.endswith('.address.city') and event == 'string':
                    if "address" not in current_dealer:
                        current_dealer["address"] = {}
                    current_dealer["address"]["city"] = value
                elif in_dealer and prefix.endswith('.address.state') and event == 'string':
                    if "address" not in current_dealer:
                        current_dealer["address"] = {}
                    current_dealer["address"]["state"] = value
                elif in_dealer and prefix.endswith('.address.zip') and event == 'string':
                    if "address" not in current_dealer:
                        current_dealer["address"] = {}
                    current_dealer["address"]["zip"] = value
                elif prefix == '' and event == 'end_array':
                    # Save last dealer
                    if current_dealer:
                        converted_dealer = convert_dealer_to_chrysler_format(current_dealer)
                        if converted_dealer:
                            chrysler_format["dealers"].append(converted_dealer)
                            dealer_count += 1
                    break
                elif in_dealer and prefix.endswith('.source_zips') and event == 'start_array':
                    # Skip the entire source_zips array
                    continue
                elif in_dealer and prefix.endswith('.source_zips') and event == 'end_array':
                    continue
                elif in_dealer and prefix.endswith('.source_zips') and event == 'string':
                    # Skip individual zip codes
                    continue
                elif in_dealer and prefix.endswith('.coordinates') and event == 'start_map':
                    # Skip coordinates
                    continue
                elif in_dealer and prefix.endswith('.coordinates') and event == 'end_map':
                    continue
                elif in_dealer and prefix.endswith('.dealer_attributes') and event == 'start_array':
                    # Skip dealer attributes
                    continue
                elif in_dealer and prefix.endswith('.dealer_attributes') and event == 'end_array':
                    continue
                elif in_dealer and prefix.endswith('.dealer_attributes') and event == 'string':
                    # Skip individual attributes
                    continue
                elif in_dealer and prefix.endswith('.distance') and event == 'number':
                    # Skip distance
                    continue
                elif in_dealer and prefix.endswith('.hours') and event == 'string':
                    # Skip hours
                    continue
                elif in_dealer and prefix.endswith('.fax') and event == 'string':
                    # Skip fax
                    continue
                elif in_dealer and prefix.endswith('') and event == 'end_map':
                    # End of dealer object
                    in_dealer = False
                    
    except Exception as e:
        print(f"Error with ijson parsing: {e}")
        return convert_with_manual_parsing(toyota_file)
    
    chrysler_format["total_dealers_found"] = dealer_count
    
    # Write converted data
    output_file = "data/toyota_converted.json"
    print(f"Writing converted data to {output_file}...")
    
    with open(output_file, 'w') as f:
        json.dump(chrysler_format, f, indent=2)
    
    print(f"Successfully converted {dealer_count} dealers")
    print(f"Output saved to: {output_file}")
    print("Conversion complete!")

def convert_with_standard_json(toyota_file):
    """Convert using standard json parser"""
    print("Using standard JSON parser...")
    
    try:
        with open(toyota_file, 'r') as f:
            toyota_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print("Trying manual parsing approach...")
        return convert_with_manual_parsing(toyota_file)
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    print(f"Found {len(toyota_data)} Toyota dealers")
    
    # Convert to Chrysler format
    chrysler_format = {
        "oem": "Toyota",
        "zip_code": "multiple",
        "total_dealers_found": len(toyota_data),
        "method": "converted_from_toyota_format",
        "dealers": []
    }
    
    for dealer in toyota_data:
        converted_dealer = convert_dealer_to_chrysler_format(dealer)
        if converted_dealer:
            chrysler_format["dealers"].append(converted_dealer)
    
    # Write converted data
    output_file = "data/toyota_converted.json"
    print(f"Writing converted data to {output_file}...")
    
    with open(output_file, 'w') as f:
        json.dump(chrysler_format, f, indent=2)
    
    print(f"Successfully converted {len(chrysler_format['dealers'])} dealers")
    print(f"Output saved to: {output_file}")
    print("Conversion complete!")

def convert_dealer_to_chrysler_format(dealer):
    """Convert a single dealer to Chrysler format"""
    return {
        "Dealer": dealer.get("name", ""),
        "Website": dealer.get("website", ""),
        "Phone": dealer.get("phone", ""),
        "Email": dealer.get("email", ""),
        "Street": dealer.get("address", {}).get("street", ""),
        "City": dealer.get("address", {}).get("city", ""),
        "State": dealer.get("address", {}).get("state", ""),
        "ZIP": dealer.get("address", {}).get("zip", "")
    }

def convert_with_manual_parsing(toyota_file):
    """Alternative conversion method using manual parsing"""
    print("Using manual parsing approach...")
    
    chrysler_format = {
        "oem": "Toyota",
        "zip_code": "multiple",
        "total_dealers_found": 0,
        "method": "converted_from_toyota_format_manual",
        "dealers": []
    }
    
    dealer_count = 0
    
    try:
        with open(toyota_file, 'r') as f:
            content = f.read()
            
        # Find all dealer objects
        import re
        
        # Pattern to match dealer objects
        dealer_pattern = r'"dealer_code":\s*"([^"]+)"[^}]*"name":\s*"([^"]+)"[^}]*"website":\s*"([^"]*)"[^}]*"phone":\s*"([^"]*)"[^}]*"email":\s*"([^"]*)"[^}]*"street":\s*"([^"]*)"[^}]*"city":\s*"([^"]*)"[^}]*"state":\s*"([^"]*)"[^}]*"zip":\s*"([^"]*)"'
        
        matches = re.findall(dealer_pattern, content, re.DOTALL)
        
        for match in matches:
            dealer_code, name, website, phone, email, street, city, state, zip_code = match
            
            converted_dealer = {
                "Dealer": name,
                "Website": website,
                "Phone": phone,
                "Email": email,
                "Street": street,
                "City": city,
                "State": state,
                "ZIP": zip_code
            }
            chrysler_format["dealers"].append(converted_dealer)
            dealer_count += 1
            
    except Exception as e:
        print(f"Error in manual parsing: {e}")
        return
    
    chrysler_format["total_dealers_found"] = dealer_count
    
    # Write converted data
    output_file = "data/toyota_converted.json"
    print(f"Writing converted data to {output_file}...")
    
    with open(output_file, 'w') as f:
        json.dump(chrysler_format, f, indent=2)
    
    print(f"Successfully converted {dealer_count} dealers")
    print(f"Output saved to: {output_file}")
    print("Conversion complete!")

if __name__ == "__main__":
    convert_toyota_to_chrysler_format()
