#!/usr/bin/env python3
"""
Tesla Additional States Scraper
Adds 40+ new dealerships from major missing states.
Current: 120 dealerships
Target: 160+ dealerships (adding 40+)
"""

import json
import re

def add_major_missing_states():
    """Add dealerships from major missing states"""
    
    new_dealerships = []
    
    # TEXAS (27 dealerships) - Major state
    texas = [
        {'name': 'Austin Ridgepoint', 'address': '2323 RIDGEPOINT DR', 'city': 'AUSTIN', 'state': 'Texas', 'zip': '78754', 'phone': '(737) 800-5731', 'lat': 30.3290182, 'lng': -97.6755978},
        {'name': 'Austin-500 E St Elmo Rd', 'address': '500 E St Elmo Rd', 'city': 'Austin', 'state': 'Texas', 'zip': '78745', 'phone': '737-717-8919', 'lat': 30.2153692, 'lng': -97.7616189},
        {'name': 'Brownsville', 'address': '7045 Old Highway 77', 'city': 'Olmito', 'state': 'Texas', 'zip': '78575', 'phone': '956-589-7952', 'lat': 26.012567, 'lng': -97.5313576},
        {'name': 'Corpus Christi-South Padre Island Drive', 'address': '3605 S Padre Island Dr', 'city': 'Corpus Christi', 'state': 'Texas', 'zip': '78415', 'phone': '361-360-7164', 'lat': 27.724281, 'lng': -97.405736},
        {'name': 'Dallas', 'address': '6500 Cedar Springs Road', 'city': 'Dallas', 'state': 'Texas', 'zip': '75235', 'phone': '214-736-0587', 'lat': 32.8323971, 'lng': -96.8375432},
        {'name': 'Dallas-Northpark Center', 'address': '8687 North Central Expwy Suite #1027', 'city': 'Dallas', 'state': 'Texas', 'zip': '75225', 'phone': '469-232-9270', 'lat': 32.8677639, 'lng': -96.7723289},
        {'name': 'El Paso', 'address': '7825 Helen of Troy Dr', 'city': 'El Paso', 'state': 'Texas', 'zip': '79912', 'phone': '(915)352-2852', 'lat': 31.8765065, 'lng': -106.5770986},
        {'name': 'Fort Worth - 5812 N Fwy', 'address': '5812 N Fwy', 'city': 'Fort Worth', 'state': 'Texas', 'zip': '76137', 'phone': '(817) 806-0698', 'lat': 32.85136, 'lng': -97.31137},
        {'name': 'Houston', 'address': '19820 Hempstead Hwy', 'city': 'Houston', 'state': 'Texas', 'zip': '77065', 'phone': '281-571-4390', 'lat': 29.9127482, 'lng': -95.6150909},
        {'name': 'Houston - Richmond', 'address': '21555 Southwest Fwy Building A', 'city': 'Richmond', 'state': 'Texas', 'zip': '77469', 'phone': '346-762-6700', 'lat': 29.5564029, 'lng': -95.7072456},
        {'name': 'Houston-Houston Galleria', 'address': '5135 West Alabama Street Suite 5270', 'city': 'Houston', 'state': 'Texas', 'zip': '77056', 'phone': '(713) 622-3393', 'lat': 29.7377008, 'lng': -95.4645439},
        {'name': 'Houston-Westchase-Westheimer', 'address': '9633 Westheimer Rd', 'city': 'Houston', 'state': 'Texas', 'zip': '77063', 'phone': '713-821-2700', 'lat': 29.7362087, 'lng': -95.5375317},
        {'name': 'League City', 'address': '400 GULF FWY S', 'city': 'LEAGUE CITY', 'state': 'Texas', 'zip': '77573', 'phone': '281-724-6245', 'lat': 29.4992881, 'lng': -95.1108011},
        {'name': 'Lubbock', 'address': '6544 82nd St', 'city': 'Lubbock', 'state': 'Texas', 'zip': '79424', 'phone': '806-503-6224', 'lat': 33.5203948, 'lng': -101.961764},
        {'name': 'Market Street-The Woodlands', 'address': '9595 SIX PINES DR', 'city': 'THE WOODLANDS', 'state': 'Texas', 'zip': '77380', 'phone': '832-616-2822', 'lat': 30.1639605, 'lng': -95.4643004},
        {'name': 'Plano - Democracy Drive', 'address': '5800 Democracy Drive', 'city': 'Plano', 'state': 'Texas', 'zip': '75024', 'phone': '469-366-3436', 'lat': 33.06787, 'lng': -96.822623},
        {'name': 'Plano - Lexington', 'address': '300 Lexington Dr', 'city': 'Plano', 'state': 'Texas', 'zip': '75075', 'phone': '(469) 304-4322', 'lat': 33.0357901, 'lng': -96.70733},
        {'name': 'Plano-Legacy West', 'address': '7500 Windrose Avenue Space B185', 'city': 'Plano', 'state': 'Texas', 'zip': '75024', 'phone': '469-331-9677', 'lat': 33.080875, 'lng': -96.826109},
        {'name': 'Pond Springs', 'address': '12845 N Highway 183', 'city': 'Austin', 'state': 'Texas', 'zip': '78750', 'phone': '737.207.8000', 'lat': 30.4357336, 'lng': -97.7708997},
        {'name': 'San Antonio', 'address': '8320-8434 Airport Blvd', 'city': 'San Antonio', 'state': 'Texas', 'zip': '78216', 'phone': '210-446-2318', 'lat': 29.5148616, 'lng': -98.4761476},
        {'name': 'San Antonio-Dominion', 'address': '23011 IH-10 West', 'city': 'San Antonio', 'state': 'Texas', 'zip': '78257', 'phone': '210-974-6035', 'lat': 29.655276, 'lng': -98.626369},
        {'name': 'Southlake-Southlake Town Center', 'address': '257 Grand Avenue', 'city': 'Southlake', 'state': 'Texas', 'zip': '76092', 'phone': '(817) 722-0386', 'lat': 32.9436533, 'lng': -97.130195},
        {'name': 'Tesla - Flower Mound', 'address': '1805 Justin Rd', 'city': 'Flower Mound', 'state': 'Texas', 'zip': '75028', 'phone': '(469) 528-4713', 'lat': 33.0703601, 'lng': -97.054966},
        {'name': 'Tesla - The Woodlands - Tesla Center', 'address': '9420 College Park Dr', 'city': 'The Woodlands', 'state': 'Texas', 'zip': '77384', 'phone': '(936) 703-1263', 'lat': 30.2289924, 'lng': -95.5088204},
        {'name': 'Tesla Brazos Mall Pop up', 'address': '100 TX-332', 'city': 'Lake Jackson', 'state': 'Texas', 'zip': '77566', 'phone': '(713) 821-2700', 'lat': 29.0506919, 'lng': -95.459119},
        {'name': 'Tesla Cielo Vista Mall Pop-up', 'address': '8401 Gateway Blvd W', 'city': 'El Paso', 'state': 'Texas', 'zip': '79925', 'phone': '(915) 779-7070', 'lat': 31.7753257, 'lng': -106.3791262},
        {'name': 'Tesla Lakeline Mall Pop-Up', 'address': '11200 Lakeline Mall Dr', 'city': 'Cedar Park', 'state': 'Texas', 'zip': '78613', 'phone': '(512) 257-7467', 'lat': 30.4700139, 'lng': -97.8072249},
        {'name': 'Tesla Midland Park Mall Pop Up', 'address': '4511 N Midkiff Rd', 'city': 'Midland', 'state': 'Texas', 'zip': '79705', 'phone': '(806) 503-6224', 'lat': 32.0301564, 'lng': -102.1316508},
        {'name': 'Tesla Parkdale Mall Pop-Up', 'address': '6155 Eastex Fwy', 'city': 'Beaumont', 'state': 'Texas', 'zip': '77706', 'phone': '(409) 898-2222', 'lat': 30.125315, 'lng': -94.16058},
        {'name': 'Tesla Post Oak Mall Pop Up', 'address': '1500 Harvey Rd', 'city': 'College Station', 'state': 'Texas', 'zip': '77840', 'phone': '(281) 571-4390', 'lat': 30.6251971, 'lng': -96.3036686},
        {'name': 'The Domain 11601 Century Oaks Terrace', 'address': '11601 Century Oaks Terrace Suite 123', 'city': 'Austin', 'state': 'Texas', 'zip': '78758', 'phone': '(512) 833-6321', 'lat': 30.4032405, 'lng': -97.7252911},
        {'name': 'Tyler', 'address': '3408 S SW Loop 323', 'city': 'Tyler', 'state': 'Texas', 'zip': '75701', 'phone': '430-205-7160', 'lat': 32.309347, 'lng': -95.338969},
        {'name': 'West Austin', 'address': '7010 State Hwy 71', 'city': 'Austin', 'state': 'Texas', 'zip': '78735', 'phone': '(512) 382-2736', 'lat': 30.2349985, 'lng': -97.873938}
    ]
    
    # NEW YORK (12+ dealerships)
    new_york = [
        {'name': 'Brooklyn', 'address': '106 2nd Ave', 'city': 'Brooklyn', 'state': 'New York', 'zip': '11215', 'phone': '(646) 335-1060', 'lat': 40.6731907, 'lng': -73.9944353},
        {'name': 'Buffalo', 'address': '1216 South Park Ave', 'city': 'Buffalo', 'state': 'New York', 'zip': '14220', 'phone': '(716) 587-3998', 'lat': 42.8605316, 'lng': -78.8378809},
        {'name': 'Latham', 'address': '326 Old Niskayuna Road Suite A', 'city': 'Latham', 'state': 'New York', 'zip': '12110', 'phone': '518-246-2120', 'lat': 42.742458, 'lng': -73.793652},
        {'name': 'Long Island-Syosset', 'address': '7 Aerial Way', 'city': 'Syosset', 'state': 'New York', 'zip': '11791', 'phone': '516-864-0535', 'lat': 40.7999, 'lng': -73.5152},
        {'name': 'Manhasset-Americana Manhasset', 'address': '2122 Northern Blvd', 'city': 'Manhasset', 'state': 'New York', 'zip': '11030', 'phone': '516-734-0271', 'lat': 40.796214, 'lng': -73.669443},
        {'name': 'Westchester', 'address': '115 Kisco Avenue', 'city': 'Mount Kisco', 'state': 'New York', 'zip': '10549', 'phone': '914.218.8900', 'lat': 41.212675, 'lng': -73.727486},
        {'name': 'Oneida', 'address': '5218 Patrick Rd', 'city': 'Verona', 'state': 'New York', 'zip': '13478', 'phone': '', 'lat': 43.1125833, 'lng': -75.591062},
        {'name': 'Rochester', 'address': '3535 W Henrietta Road', 'city': 'Rochester', 'state': 'New York', 'zip': '14623', 'phone': '(585) 613-9120', 'lat': 43.0837122, 'lng': -77.640278},
        {'name': 'Smithtown', 'address': '1000 Nesconset Hwy', 'city': 'Nesconset', 'state': 'New York', 'zip': '11767', 'phone': '6319822134', 'lat': 40.85974, 'lng': -73.14134},
        {'name': 'Syracuse-Fayetteville', 'address': '5427 N BURDICK ST', 'city': 'FAYETTEVILLE', 'state': 'New York', 'zip': '13066', 'phone': '(315) 231-2182', 'lat': 43.0370663, 'lng': -76.0182468},
        {'name': 'Tesla Meatpacking', 'address': '860 Washington St.', 'city': 'New York', 'state': 'New York', 'zip': '10014', 'phone': '2122061204', 'lat': 40.74107, 'lng': -74.007562},
        {'name': 'Westbury', 'address': '1350 CORPORATE DR', 'city': 'WESTBURY', 'state': 'New York', 'zip': '11590', 'phone': '(516) 247-4093', 'lat': 40.7428224, 'lng': -73.5875694},
        {'name': 'White Plains-Tarrytown', 'address': '250 Tarrytown Rd', 'city': 'White Plains', 'state': 'New York', 'zip': '10607', 'phone': '(914) 467-5070', 'lat': 41.0418883, 'lng': -73.7918184}
    ]
    
    # ILLINOIS (10+ dealerships)
    illinois = [
        {'name': 'Bloomington', 'address': '420 Olympia Dr', 'city': 'Bloomington', 'state': 'Illinois', 'zip': '61704', 'phone': '309-445-8919', 'lat': 40.468679, 'lng': -88.907781},
        {'name': 'CherryVale Mall Pop-Up', 'address': '7200 Harrison Ave', 'city': 'Rockford Township', 'state': 'Illinois', 'zip': '61112', 'phone': '', 'lat': 42.2461735, 'lng': -88.9757903},
        {'name': 'Chicago', 'address': '717 S Desplaines St', 'city': 'Chicago', 'state': 'Illinois', 'zip': '60607', 'phone': '(630) 320-7985', 'lat': 41.8730544, 'lng': -87.6428499},
        {'name': 'Chicago-Gold Coast', 'address': '901 N Rush St', 'city': 'Chicago', 'state': 'Illinois', 'zip': '60611', 'phone': '(312) 764-5176', 'lat': 41.899332, 'lng': -87.6266012},
        {'name': 'Chicago-Schaumburg', 'address': '320 West Golf Road', 'city': 'Schaumburg', 'state': 'Illinois', 'zip': '60195', 'phone': '630-283-4328', 'lat': 42.0491005, 'lng': -88.0881959},
        {'name': 'Chicago-Westmont', 'address': '50 W. Ogden Ave', 'city': 'Westmont', 'state': 'Illinois', 'zip': '60559', 'phone': '(630) 541-1214', 'lat': 41.810562, 'lng': -87.978325},
        {'name': 'Libertyville', 'address': '1121 S Milwaukee Ave', 'city': 'Libertyville', 'state': 'Illinois', 'zip': '60048', 'phone': '847-932-6754', 'lat': 42.2667662, 'lng': -87.9511833},
        {'name': 'Naperville', 'address': '3200 Ogden Ave', 'city': 'Lisle', 'state': 'Illinois', 'zip': '60532', 'phone': '630-328-2251', 'lat': 41.7967366, 'lng': -88.1150556},
        {'name': 'Northbrook', 'address': '1200 Skokie Blvd', 'city': 'Northbrook', 'state': 'Illinois', 'zip': '60062', 'phone': '(847) 239-9982', 'lat': 42.1288207, 'lng': -87.7866777},
        {'name': 'Orland Park - 159th St', 'address': '8601 W 159th st', 'city': 'Orland Park', 'state': 'Illinois', 'zip': '60462', 'phone': '708 781 4476', 'lat': 41.6008672, 'lng': -87.8290428},
        {'name': 'Buffalo Grove', 'address': '915 Dundee Rd', 'city': 'Buffalo Grove', 'state': 'Illinois', 'zip': '60089', 'phone': '(847) 660-1126', 'lat': 42.1381894, 'lng': -87.9771961},
        {'name': 'Tesla Rockford', 'address': '1998 McFarland Rd', 'city': 'Rockford', 'state': 'Illinois', 'zip': '61107', 'phone': '(779) 500-6155', 'lat': 42.2928218, 'lng': -88.9790064}
    ]
    
    # Add all new states
    all_new_states = [texas, new_york, illinois]
    
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
    print("TESLA ADDITIONAL STATES SCRAPER")
    print("="*60)
    print("Adding 40+ new dealerships from major missing states")
    print("="*60)
    
    # Load existing data
    with open('/Users/kimseanpardo/autodealerships/tesla_dealerships_usa.json', 'r') as f:
        data = json.load(f)
    
    # Remove metadata for processing
    metadata = data[0] if data[0].get('_metadata') else None
    existing_dealerships = data[1:] if metadata else data
    
    print(f"Current dealerships: {len(existing_dealerships)}")
    
    # Add new dealerships
    new_dealerships = add_major_missing_states()
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
    
    print(f"\n📊 UPDATED STATISTICS:")
    print(f"Total dealerships: {len(all_dealerships)}")
    print(f"States covered: {len(states)}")
    print(f"Progress: {len(all_dealerships)}/272 ({len(all_dealerships)/272*100:.1f}%)")
    print(f"Still needed: {272 - len(all_dealerships)} dealerships")
    
    print(f"\n📋 BY STATE:")
    for state, count in sorted(states.items()):
        print(f"  {state}: {count}")
    
    print(f"\n🎯 ACHIEVEMENT:")
    print(f"Added {len(new_dealerships)} new dealerships!")
    print(f"New total: {len(all_dealerships)} (was {len(existing_dealerships)})")

if __name__ == "__main__":
    main()
