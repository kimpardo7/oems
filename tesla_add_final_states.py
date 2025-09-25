#!/usr/bin/env python3
"""
Tesla Final States Scraper
Adds remaining major states to reach closer to 272 target.
Current: 178 dealerships
Target: 220+ dealerships (adding 40+ more)
"""

import json

def add_remaining_major_states():
    """Add dealerships from remaining major states"""
    
    new_dealerships = []
    
    # PENNSYLVANIA (8+ dealerships)
    pennsylvania = [
        {'name': 'Pittsburgh', 'address': '1400 Brockwell St', 'city': 'Bridgeville', 'state': 'Pennsylvania', 'zip': '15017', 'phone': '4123195316', 'lat': 40.3605312, 'lng': -80.1208653},
        {'name': 'Devon', 'address': '470 W. Lancaster Avenue', 'city': 'Devon', 'state': 'Pennsylvania', 'zip': '19333', 'phone': '610-407-7030', 'lat': 40.045865, 'lng': -75.433279},
        {'name': 'Tesla - King of Prussia Mall', 'address': '160 N Gulph Rd Suit 1310B', 'city': 'King of Prussia', 'state': 'Pennsylvania', 'zip': '19406', 'phone': '(484) 235-5858', 'lat': 40.088359, 'lng': -75.3909134},
        {'name': 'Mechanicsburg', 'address': '6458 Carlisle Pike', 'city': 'Mechanicsburg', 'state': 'Pennsylvania', 'zip': '17050', 'phone': '717-590-6241', 'lat': 40.2474461, 'lng': -77.0162336},
        {'name': 'Tesla - Wexford', 'address': '14010 Perry Hwy', 'city': 'Wexford', 'state': 'Pennsylvania', 'zip': '15090', 'phone': '(878) 332-6091', 'lat': 40.6461445, 'lng': -80.0711121},
        {'name': 'Warminster', 'address': '700 York Rd', 'city': 'Warminster', 'state': 'Pennsylvania', 'zip': '18974', 'phone': '(215) 347-1004', 'lat': 40.211002, 'lng': -75.1010818},
        {'name': 'West Chester', 'address': '1568 W CHESTER PIKE', 'city': 'West Chester', 'state': 'Pennsylvania', 'zip': '19382', 'phone': '610-883-5044', 'lat': 39.9657699, 'lng': -75.5248494}
    ]
    
    # MASSACHUSETTS (6+ dealerships)
    massachusetts = [
        {'name': 'Boston-Boylston Street', 'address': '888 Boylston Street Suite 055', 'city': 'Boston', 'state': 'Massachusetts', 'zip': '02116', 'phone': '6174764003', 'lat': 42.3475062, 'lng': -71.0839303},
        {'name': 'Dedham', 'address': '840 Providence Highway', 'city': 'Dedham', 'state': 'Massachusetts', 'zip': '02026', 'phone': '7814713001', 'lat': 42.235962, 'lng': -71.178212},
        {'name': 'Norwell', 'address': '98 Accord Park Dr', 'city': 'Norwell', 'state': 'Massachusetts', 'zip': '02061', 'phone': '781-763-0035', 'lat': 42.1665499, 'lng': -70.887739},
        {'name': 'Peabody', 'address': '210 Andover St', 'city': 'Peabody', 'state': 'Massachusetts', 'zip': '01960', 'phone': '978-326-1623', 'lat': 42.5411906, 'lng': -70.9407857},
        {'name': 'Tesla Natick', 'address': '1245 Worcester St Space 3018', 'city': 'Natick', 'state': 'Massachusetts', 'zip': '01760', 'phone': '(508) 975-4230', 'lat': 42.302269, 'lng': -71.3833728}
    ]
    
    # MICHIGAN (6+ dealerships)
    michigan = [
        {'name': 'Ann Arbor', 'address': '3530 Jackson Rd', 'city': 'Ann Arbor', 'state': 'Michigan', 'zip': '48103', 'phone': '734 887 7853', 'lat': 42.2857319, 'lng': -83.8020491},
        {'name': 'Grand Rapids', 'address': '2919 29th Street SE', 'city': 'Grand Rapids', 'state': 'Michigan', 'zip': '49512', 'phone': '616-228-6758', 'lat': 42.910868, 'lng': -85.595622},
        {'name': 'Somerset Collection', 'address': '2800 W. Big Beaver Road Space #N-114', 'city': 'Troy', 'state': 'Michigan', 'zip': '48084', 'phone': '248-205-1997', 'lat': 42.563075, 'lng': -83.183398},
        {'name': 'Tesla Meridian Mall Pop Up', 'address': '1982 W Grand River Ave', 'city': 'Meridian Township', 'state': 'Michigan', 'zip': '48864', 'phone': '', 'lat': 42.72555, 'lng': -84.4183167},
        {'name': 'Twelve Oaks Mall- Novi', 'address': '27804X Novi Rd', 'city': 'Novi', 'state': 'Michigan', 'zip': '48377', 'phone': '(248) 205-1997', 'lat': 42.4921678, 'lng': -83.4687821},
        {'name': 'West Bloomfield Township', 'address': '6800 Orchard Lake Rd', 'city': 'West Bloomfield Township', 'state': 'Michigan', 'zip': '48322-3412', 'phone': '(248) 862-7298', 'lat': 42.538233, 'lng': -83.3616583}
    ]
    
    # MINNESOTA (7+ dealerships)
    minnesota = [
        {'name': 'Golden Valley', 'address': '700 Ottawa Ave N', 'city': 'Golden Valley', 'state': 'Minnesota', 'zip': '55422', 'phone': '(763) 656-6995', 'lat': 44.9864, 'lng': -93.3393452},
        {'name': 'St. Paul – Lake Elmo', 'address': '9800 Hudson Blvd N', 'city': 'Lake Elmo', 'state': 'Minnesota', 'zip': '55042', 'phone': '(763) 347-3895', 'lat': 44.9498624, 'lng': -92.9074207},
        {'name': 'Mall of America Kiosk', 'address': '60 E Broadway', 'city': 'Bloomington', 'state': 'Minnesota', 'zip': '55425', 'phone': '(763) 656-6995', 'lat': 44.8548651, 'lng': -93.2422148},
        {'name': 'Minneapolis-Eden Prairie', 'address': '6801 Washington Ave S', 'city': 'Minneapolis', 'state': 'Minnesota', 'zip': '55439', 'phone': '952-433-1373', 'lat': 44.87963, 'lng': -93.3992963},
        {'name': 'Rogers', 'address': '22015 S Diamond Lake Rd', 'city': 'Rogers', 'state': 'Minnesota', 'zip': '55374', 'phone': '612-486-9600', 'lat': 45.1991036, 'lng': -93.5599668},
        {'name': 'St. Paul', 'address': '2590 West Maplewood Drive', 'city': 'Maplewood', 'state': 'Minnesota', 'zip': '55109', 'phone': '(763) 347-7123', 'lat': 45.017892, 'lng': -93.050723},
        {'name': 'Tesla Apache Mall Pop Up', 'address': '333 Apache Mall', 'city': 'Rochester', 'state': 'Minnesota', 'zip': '55902', 'phone': '(763) 347-3895', 'lat': 44.0046562, 'lng': -92.4789815}
    ]
    
    # NEVADA (3+ dealerships)
    nevada = [
        {'name': 'Las Vegas - E. Sahara', 'address': '3250 E SAHARA AVE', 'city': 'Las Vegas', 'state': 'Nevada', 'zip': '89104', 'phone': '(702) 473-7223', 'lat': 36.1451074, 'lng': -115.1034963},
        {'name': 'Las Vegas-W. Sahara Ave', 'address': '7077 West Sahara Avenue', 'city': 'Las Vegas', 'state': 'Nevada', 'zip': '89117', 'phone': '7029146500', 'lat': 36.143473, 'lng': -115.246794},
        {'name': 'Reno', 'address': '9732 S Virginia Street', 'city': 'Reno', 'state': 'Nevada', 'zip': '89511', 'phone': '775-453-7957', 'lat': 39.444704, 'lng': -119.769792}
    ]
    
    # NEW JERSEY (8+ dealerships)
    new_jersey = [
        {'name': 'American Dream East Rutherford', 'address': '1 American Dream Way', 'city': 'East Rutherford', 'state': 'New Jersey', 'zip': '07073', 'phone': '(833) 263-7326', 'lat': 40.8094502, 'lng': -74.0669268},
        {'name': 'Cherry Hill', 'address': '1605 Route 70 West', 'city': 'Cherry Hill', 'state': 'New Jersey', 'zip': '08002', 'phone': '856-356-1088', 'lat': 39.9173111, 'lng': -75.0297792},
        {'name': 'Eatontown', 'address': '269 Route 35', 'city': 'Eatontown', 'state': 'New Jersey', 'zip': '07724', 'phone': '7326762011', 'lat': 40.2836156, 'lng': -74.0486475},
        {'name': 'Englewood', 'address': '45 Cedar Ln', 'city': 'Englewood', 'state': 'New Jersey', 'zip': '07631', 'phone': '(201) 477-7975', 'lat': 40.8773612, 'lng': -73.9887879},
        {'name': 'Garden State Plaza', 'address': 'One Garden State Plaza Suite 2124', 'city': 'Paramus', 'state': 'New Jersey', 'zip': '07652', 'phone': '201.291.5630', 'lat': 40.9176228, 'lng': -74.076344},
        {'name': 'Lawrence Township', 'address': '3371 Brunswick Pike', 'city': 'Lawrence Township', 'state': 'New Jersey', 'zip': '08648', 'phone': '609-806-2611', 'lat': 40.2950005, 'lng': -74.684471},
        {'name': 'Paramus', 'address': '530 NJ-17', 'city': 'Paramus', 'state': 'New Jersey', 'zip': '07652', 'phone': '201-225-2544', 'lat': 40.957709, 'lng': -74.0734305},
        {'name': 'Springfield', 'address': '135 US 22', 'city': 'Springfield', 'state': 'New Jersey', 'zip': '07081', 'phone': '973-921-0925', 'lat': 40.6860212, 'lng': -74.3166015}
    ]
    
    # OHIO (6+ dealerships)
    ohio = [
        {'name': 'Cincinnati - Oakley', 'address': '5245 Ridge Ave', 'city': 'Cincinnati', 'state': 'Ohio', 'zip': '45213', 'phone': '(513) 514-2898', 'lat': 39.1679441, 'lng': -84.4256369},
        {'name': 'Cleveland - Lyndhurst', 'address': '5180 Mayfield Rd', 'city': 'Lyndhurst', 'state': 'Ohio', 'zip': '44124', 'phone': '440-461-1016', 'lat': 41.5191779, 'lng': -81.493795},
        {'name': 'Columbus - Easton', 'address': '4099 Easton Loop West', 'city': 'Columbus', 'state': 'Ohio', 'zip': '43219', 'phone': '(614) 934-6869', 'lat': 40.051938, 'lng': -82.91798},
        {'name': 'Tesla Service Akron', 'address': '52 Springside Dr', 'city': 'Akron', 'state': 'Ohio', 'zip': '44333', 'phone': '330-598-6036', 'lat': 41.1339817, 'lng': -81.6457631},
        {'name': 'Tesla Service Dayton-Moraine', 'address': '1927 W Dorothy Ln', 'city': 'Moraine', 'state': 'Ohio', 'zip': '45439', 'phone': '(937) 269-0237', 'lat': 39.7100729, 'lng': -84.2075513}
    ]
    
    # Add all new states
    all_new_states = [pennsylvania, massachusetts, michigan, minnesota, nevada, new_jersey, ohio]
    
    for state_data in all_new_states:
        for dealer in state_data:
            new_dealerships.append({
                'name': dealer['name'],
                'address': dealer['address'],
                'city': dealer['city'],
                'state': dealer['state'],
                'zip_code': dealer['zip'],
                'phone': dealer['phone'],
                'latitude': dealer['lat'],
                'longitude': dealer['lng'],
                'website_url': f"https://www.tesla.com/findus/location/store/{dealer['name'].lower().replace(' ', '').replace('-', '')}",
                'demo_drive_url': f"https://www.tesla.com/drive?lat={dealer['lat']}&lng={dealer['lng']}"
            })
    
    return new_dealerships

def main():
    print("="*60)
    print("TESLA FINAL STATES SCRAPER")
    print("="*60)
    print("Adding remaining major states to reach target")
    print("="*60)
    
    # Load existing data
    with open('/Users/kimseanpardo/autodealerships/tesla_dealerships_usa.json', 'r') as f:
        data = json.load(f)
    
    # Remove metadata for processing
    metadata = data[0] if data[0].get('_metadata') else None
    existing_dealerships = data[1:] if metadata else data
    
    print(f"Current dealerships: {len(existing_dealerships)}")
    
    # Add new dealerships
    new_dealerships = add_remaining_major_states()
    print(f"Adding {len(new_dealerships)} new dealerships")
    
    # Combine data
    all_dealerships = existing_dealerships + new_dealerships
    
    # Update metadata
    if metadata:
        metadata['_metadata']['total_dealerships'] = len(all_dealerships)
        metadata['_metadata']['progress_percentage'] = round(len(all_dealerships) / 272 * 100, 1)
        metadata['_metadata']['still_needed'] = 272 - len(all_dealerships)
        metadata['_metadata']['states_covered'] = len(set(d['state'] for d in all_dealerships))
        all_data = [metadata] + all_dealerships
    else:
        all_data = all_dealerships
    
    # Save updated data
    with open('/Users/kimseanpardo/autodealerships/tesla_dealerships_usa.json', 'w') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ UPDATED: {len(all_dealerships)} total dealerships")
    
    # Statistics
    states = {}
    for dealer in all_dealerships:
        state = dealer['state']
        states[state] = states.get(state, 0) + 1
    
    print(f"\n📊 FINAL STATISTICS:")
    print(f"Total dealerships: {len(all_dealerships)}")
    print(f"States covered: {len(states)}")
    print(f"Progress: {len(all_dealerships)}/272 ({len(all_dealerships)/272*100:.1f}%)")
    print(f"Still needed: {272 - len(all_dealerships)} dealerships")
    
    print(f"\n📋 BY STATE:")
    for state, count in sorted(states.items()):
        print(f"  {state}: {count}")
    
    print(f"\n🎯 ACHIEVEMENT:")
    print(f"Added {len(new_dealerships)} more dealerships!")
    print(f"New total: {len(all_dealerships)} (was {len(existing_dealerships)})")
    print(f"Successfully reached {len(all_dealerships)/272*100:.1f}% of target!")

if __name__ == "__main__":
    main()
