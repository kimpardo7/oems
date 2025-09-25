#!/usr/bin/env python3
"""
Tesla Complete Dealership Scraper
Extracts ALL Tesla dealerships from the browser snapshot data.
Target: ~272 dealerships across all US states
Current: 78 (Arizona: 8, California: 70)
Missing: ~194 dealerships
"""

import json
import re

def extract_all_tesla_dealerships_complete():
    """Extract ALL Tesla dealerships from the comprehensive browser snapshot data"""
    
    dealerships = []
    
    # ARIZONA (8 dealerships) - Already complete
    arizona = [
        {'name': 'Glendale', 'address': '9245 W Glendale Ave', 'city': 'Glendale', 'state': 'Arizona', 'zip': '85305', 'phone': '(602) 337-5554', 'lat': 33.5368835, 'lng': -112.2578684},
        {'name': 'Mesa', 'address': '7444 E Hampton Ave', 'city': 'Mesa', 'state': 'Arizona', 'zip': '85209', 'phone': '6026273515', 'lat': 33.3919982, 'lng': -111.6711962},
        {'name': 'Scottsdale', 'address': '8300 E Raintree Dr', 'city': 'Scottsdale', 'state': 'Arizona', 'zip': '85260', 'phone': '480-361-0036', 'lat': 33.6197263, 'lng': -111.9019416},
        {'name': 'Scottsdale-Fashion Square', 'address': '7014 E. Camelback Road Suite #1210', 'city': 'Scottsdale', 'state': 'Arizona', 'zip': '85251', 'phone': '(480) 946-3735', 'lat': 33.503167, 'lng': -111.92968},
        {'name': 'Scottsdale-Kierland Commons', 'address': '15215 N. Kierland Blvd #165B1A', 'city': 'Scottsdale', 'state': 'Arizona', 'zip': '85254', 'phone': '480-333-0029', 'lat': 33.625049, 'lng': -111.928706},
        {'name': 'Tempe - E. University Drive', 'address': '2077 East University Drive', 'city': 'Tempe', 'state': 'Arizona', 'zip': '85281', 'phone': '602-643-0024', 'lat': 33.421679, 'lng': -111.897325},
        {'name': 'Deer Valley', 'address': '21030 N 19th Ave', 'city': 'Phoenix', 'state': 'Arizona', 'zip': '85027', 'phone': '(480) 293-2097', 'lat': 33.6779561, 'lng': -112.1008029},
        {'name': 'Tucson', 'address': '5081 N Oracle Rd', 'city': 'Tucson', 'state': 'Arizona', 'zip': '85704', 'phone': '520/416-7974', 'lat': 32.2986337, 'lng': -110.9790634}
    ]
    
    # CALIFORNIA (70+ dealerships) - Already complete
    california = [
        {'name': 'Santa Rosa', 'address': '3286 Airway Drive', 'city': 'Santa Rosa', 'state': 'California', 'zip': '95403', 'phone': '707-806-5040', 'lat': 38.4741754, 'lng': -122.737459},
        {'name': 'Alhambra', 'address': '1200 W Main St', 'city': 'Alhambra', 'state': 'California', 'zip': '91801', 'phone': '626-313-5967', 'lat': 34.0911499, 'lng': -118.1360862},
        {'name': 'Aliso Viejo', 'address': '26501 Aliso Creek Rd', 'city': 'Aliso Viejo', 'state': 'California', 'zip': '92656', 'phone': '(949) 860-8050', 'lat': 33.5795431, 'lng': -117.7239588},
        {'name': 'Bakersfield', 'address': '5206 Young St Suite B', 'city': 'Bakersfield', 'state': 'California', 'zip': '93311', 'phone': '661-885-3939', 'lat': 35.307366, 'lng': -119.098094},
        {'name': 'Berkeley', 'address': '1731 Fourth St', 'city': 'Berkeley', 'state': 'California', 'zip': '94710', 'phone': '(510) 898-7773', 'lat': 37.8709978, 'lng': -122.3007859},
        {'name': 'Brea-Brea Mall', 'address': '1065 BREA MALL', 'city': 'BREA', 'state': 'California', 'zip': '92821', 'phone': '7146740296', 'lat': 33.9153422, 'lng': -117.8864509},
        {'name': 'Buena Park', 'address': '6692 Auto Center Drive', 'city': 'Buena Park', 'state': 'California', 'zip': '90621', 'phone': '714-735-5696', 'lat': 33.863556, 'lng': -117.99074},
        {'name': 'Burbank', 'address': '811 South San Fernando Boulevard', 'city': 'Burbank', 'state': 'California', 'zip': '91502', 'phone': '818-480-9217', 'lat': 34.174826, 'lng': -118.301286},
        {'name': 'Burlingame', 'address': '50 Edwards Ct', 'city': 'Burlingame', 'state': 'California', 'zip': '94010', 'phone': '(650)642-1176', 'lat': 37.593128, 'lng': -122.367306},
        {'name': 'Camarillo', 'address': '311 E Daily Drive', 'city': 'Camarillo', 'state': 'California', 'zip': '93010', 'phone': '805-465-1696', 'lat': 34.2198123, 'lng': -119.0655388},
        {'name': 'Canoga Park-Topanga', 'address': '6600 Topanga Canyon Blvd Suite 1049', 'city': 'Canoga Park', 'state': 'California', 'zip': '91303', 'phone': '(818) 703-0271', 'lat': 34.1911359, 'lng': -118.6024654},
        {'name': 'Carlsbad', 'address': '3248 Lionshead Avenue', 'city': 'Carlsbad', 'state': 'California', 'zip': '92010', 'phone': '760-305-4041', 'lat': 33.133367, 'lng': -117.234576},
        {'name': 'Chico-Huss', 'address': '349 Huss Drive', 'city': 'Chico', 'state': 'California', 'zip': '95928', 'phone': '530-801-2318', 'lat': 39.70651, 'lng': -121.819925},
        {'name': 'Chula Vista', 'address': '2015 Birch Rd Suite 1015', 'city': 'Chula Vista', 'state': 'California', 'zip': '91915', 'phone': '(619) 205-4264', 'lat': 32.6235848, 'lng': -116.9674171},
        {'name': 'Colma', 'address': '1500 Collins Ave', 'city': 'Colma', 'state': 'California', 'zip': '94014', 'phone': '650-488-2984', 'lat': 37.670637, 'lng': -122.463544},
        {'name': 'Corte Madera', 'address': '201 Casa Buena Dr', 'city': 'Corte Madera', 'state': 'California', 'zip': '94925', 'phone': '415-413-9275', 'lat': 37.9242062, 'lng': -122.5145997},
        {'name': 'Culver City Supercharger', 'address': '6000 Sepulveda Blvd.', 'city': 'Culver City', 'state': 'California', 'zip': '90230-6421', 'phone': '', 'lat': 33.9854311, 'lng': -118.3933176},
        {'name': 'Dublin', 'address': '6701 Amador Plaza Road', 'city': 'Dublin', 'state': 'California', 'zip': '94568', 'phone': '925-361-1173', 'lat': 37.7027521, 'lng': -121.9248667},
        {'name': 'Elk Grove Remote Demonstration Drive', 'address': '8525 Bond Rd', 'city': 'Elk Grove', 'state': 'California', 'zip': '95624', 'phone': '', 'lat': 38.423845, 'lng': -121.388777},
        {'name': 'Encinitas', 'address': '1302 Encinitas Blvd', 'city': 'Encinitas', 'state': 'California', 'zip': '92024', 'phone': '(760) 697-9348', 'lat': 33.0465631, 'lng': -117.2631315},
        {'name': 'Fremont', 'address': '45500 Fremont Blvd', 'city': 'Fremont', 'state': 'California', 'zip': '94538', 'phone': '(510) 249-3500', 'lat': 37.4936059, 'lng': -121.9451429},
        {'name': 'Fresno', 'address': '711 W Palmdon Dr', 'city': 'Fresno', 'state': 'California', 'zip': '93704', 'phone': '(559) 492-4880', 'lat': 36.836137, 'lng': -119.805655},
        {'name': 'Gilroy', 'address': '500 Automall Dr', 'city': 'Gilroy', 'state': 'California', 'zip': '95020', 'phone': '408-427-0048', 'lat': 36.9966859, 'lng': -121.5576048},
        {'name': 'Gilroy Premium Outlets', 'address': 'Leavesley Rd', 'city': 'Gilroy', 'state': 'California', 'zip': '95020-3647', 'phone': '', 'lat': 37.0256162, 'lng': -121.5636695},
        {'name': 'Glendale-Americana at Brand', 'address': '539 Americana Way', 'city': 'Glendale', 'state': 'California', 'zip': '91210', 'phone': '818-254-7499', 'lat': 34.1437018, 'lng': -118.2574361},
        {'name': 'Irvine', 'address': '2801 Barranca Pkwy', 'city': 'Irvine', 'state': 'California', 'zip': '92606', 'phone': '949-404-2989', 'lat': 33.6941017, 'lng': -117.8256818},
        {'name': 'Long Beach', 'address': '1800 E SPRING ST', 'city': 'LONG BEACH', 'state': 'California', 'zip': '90755', 'phone': '562-308-5439', 'lat': 33.8109409, 'lng': -118.1697739},
        {'name': 'Los Angeles - Century City', 'address': '10250 Santa Monica Blvd Suite 1340', 'city': 'Los Angeles', 'state': 'California', 'zip': '90067', 'phone': '310-553-5767', 'lat': 34.058126, 'lng': -118.418214},
        {'name': 'Los Angeles-Centinela', 'address': '5840 W Centinela Avenue', 'city': 'Los Angeles', 'state': 'California', 'zip': '90045', 'phone': '310-649-5463', 'lat': 33.97585, 'lng': -118.382923},
        {'name': 'Malibu', 'address': '23401 Civic Center Way Building #2 Suite 2D', 'city': 'Malibu', 'state': 'California', 'zip': '90265', 'phone': '3104944018', 'lat': 34.0369024, 'lng': -118.6864607},
        {'name': 'Mission Viejo-Shops at Mission Viejo', 'address': '820 THE SHOPS AT MISSION VIEJO', 'city': 'MISSION VIEJO', 'state': 'California', 'zip': '92691', 'phone': '9493476820', 'lat': 33.5582235, 'lng': -117.66913},
        {'name': 'Monterey', 'address': '1901 1901 Del Monte Blvd Seaside, CA 93955', 'city': 'Seaside', 'state': 'California', 'zip': '93955', 'phone': '831-264-6896', 'lat': 36.6171238, 'lng': -121.8438038},
        {'name': 'Napa Premium outlets', 'address': '629 Factory Stores Drive', 'city': 'Napa', 'state': 'California', 'zip': '94558', 'phone': '', 'lat': 38.2948329, 'lng': -122.3027269},
        {'name': 'Newport Beach-Fashion Island', 'address': '367 Newport Center Dr', 'city': 'Newport Beach', 'state': 'California', 'zip': '92660', 'phone': '(949) 219-0040', 'lat': 33.6151888, 'lng': -117.8753716},
        {'name': 'North Hollywood', 'address': '13005 Sherman Way', 'city': 'North Hollywood', 'state': 'California', 'zip': '91605', 'phone': '(747) 256-3468', 'lat': 34.2025104, 'lng': -118.4166509},
        {'name': 'Salinas', 'address': '796 Northridge Dr', 'city': 'Salinas', 'state': 'California', 'zip': '93906', 'phone': '', 'lat': 36.7207925, 'lng': -121.6573191},
        {'name': 'Tesla - Norwalk', 'address': '11729 Imperial Hwy.', 'city': 'Norwalk', 'state': 'California', 'zip': '90650-2819', 'phone': '(562) 356-5406', 'lat': 33.9182525, 'lng': -118.0828218},
        {'name': 'Palm Springs', 'address': '68080 Perez Road', 'city': 'Cathedral City', 'state': 'California', 'zip': '92234', 'phone': '760- 321-0821', 'lat': 33.786118, 'lng': -116.475114},
        {'name': 'Palo Alto', 'address': '4180 El Camino Real', 'city': 'Palo Alto', 'state': 'California', 'zip': '94306', 'phone': '650-681-5800', 'lat': 37.4108121, 'lng': -122.1245258},
        {'name': 'Palo Alto-Stanford Shopping Center', 'address': '660 Stanford Shopping Center Suite 359B', 'city': 'Palo Alto', 'state': 'California', 'zip': '94304', 'phone': '650-798-0649', 'lat': 37.4421471, 'lng': -122.1729613},
        {'name': 'Pasadena-Colorado Blvd', 'address': '117 West Colorado Blvd', 'city': 'Pasadena', 'state': 'California', 'zip': '91105', 'phone': '626 356-7519', 'lat': 34.1460088, 'lng': -118.1529974},
        {'name': 'Promenade Temecula', 'address': '40820 Winchester Rd.', 'city': 'Temecula', 'state': 'California', 'zip': '92591-5525', 'phone': '', 'lat': 33.5245692, 'lng': -117.1546001},
        {'name': 'Riverside', 'address': '7920 Lindbergh Drive', 'city': 'Riverside', 'state': 'California', 'zip': '92508', 'phone': '951-429-6030', 'lat': 33.9060972, 'lng': -117.3250245},
        {'name': 'Rocklin', 'address': '4361 Granite Drive', 'city': 'Rocklin', 'state': 'California', 'zip': '95677', 'phone': '916-652-7740', 'lat': 38.800537, 'lng': -121.210485},
        {'name': 'Sacramento', 'address': '2535 Arden Way', 'city': 'Sacramento', 'state': 'California', 'zip': '95825', 'phone': '916-830-2191', 'lat': 38.5966464, 'lng': -121.4027029},
        {'name': 'San Diego - Miramar', 'address': '9250 Trade Pl', 'city': 'San Diego', 'state': 'California', 'zip': '92121', 'phone': '858-271-5100', 'lat': 32.8920334, 'lng': -117.1549447},
        {'name': 'San Diego-UTC', 'address': '4545 La Jolla Village Dr C17', 'city': 'San Diego', 'state': 'California', 'zip': '92122', 'phone': '858.558.1555', 'lat': 32.8712551, 'lng': -117.210474},
        {'name': 'San Francisco - Van Ness', 'address': '999 Van Ness Avenue', 'city': 'San Francisco', 'state': 'California', 'zip': '94109', 'phone': '415-268-9487', 'lat': 37.784428, 'lng': -122.421806},
        {'name': 'San Jose-Santana Row', 'address': '333 Santana Row Suite 1015', 'city': 'San Jose', 'state': 'California', 'zip': '95128', 'phone': '(408) 249-2815', 'lat': 37.322453, 'lng': -121.947954},
        {'name': 'San Luis Obispo', 'address': '1381 CALLE JOAQUIN', 'city': 'SAN LUIS OBISPO', 'state': 'California', 'zip': '93405', 'phone': '(805) 242-7173', 'lat': 35.2499324, 'lng': -120.68058},
        {'name': 'Santa Barbara', 'address': '400 Hitchcock Way', 'city': 'Santa Barbara', 'state': 'California', 'zip': '93105', 'phone': '805-770-6090', 'lat': 34.433626, 'lng': -119.74541},
        {'name': 'Santa Clarita', 'address': '24050 Creekside Rd', 'city': 'Santa Clarita', 'state': 'California', 'zip': '91355', 'phone': '(661) 600-0080', 'lat': 34.4188888, 'lng': -118.5558703},
        {'name': 'Santa Monica Place', 'address': '395 Santa Monica Place #120', 'city': 'Santa Monica', 'state': 'California', 'zip': '90401', 'phone': '310-395-8333', 'lat': 34.013819, 'lng': -118.494028},
        {'name': 'Sherman Oaks - Fashion Square Mall', 'address': '14006 Riverside Dr. Space 78', 'city': 'Sherman Oaks', 'state': 'California', 'zip': '91423', 'phone': '818-464-1459', 'lat': 34.156753, 'lng': -118.437088},
        {'name': 'Stockton', 'address': '3131 Auto Center Circle', 'city': 'Stockton', 'state': 'California', 'zip': '95212', 'phone': '(209) 390-0090', 'lat': 38.0197186, 'lng': -121.2761377},
        {'name': 'Sunnyvale', 'address': '750 El Camino Real', 'city': 'Sunnyvale', 'state': 'California', 'zip': '94087', 'phone': '408-739-2034', 'lat': 37.357529, 'lng': -122.020006},
        {'name': 'Temecula-Rancho Way', 'address': '43191 Rancho Way', 'city': 'Temecula', 'state': 'California', 'zip': '92590', 'phone': '951-514-4971', 'lat': 33.5036971, 'lng': -117.1608121},
        {'name': 'Tesla - Anaheim - Tesla Center', 'address': '5635 E La Palma Ave', 'city': 'Anaheim', 'state': 'California', 'zip': '92807', 'phone': '(714) 696-3004', 'lat': 33.861492, 'lng': -117.7920325},
        {'name': 'Tesla - Thousand Oaks', 'address': '2000 Corporate Center Dr', 'city': 'Thousand Oaks', 'state': 'California', 'zip': '91320-1400', 'phone': '(805) 214-5072', 'lat': 34.1969819, 'lng': -118.9228358},
        {'name': 'Tesla Costa Mesa', 'address': '3020 Pullman Street', 'city': 'Costa Mesa', 'state': 'California', 'zip': '92626', 'phone': '714-641-3949', 'lat': 33.67398, 'lng': -117.882377},
        {'name': 'Tesla Los Cerritos Center Pop-Up', 'address': '239 Los Cerritos Center', 'city': 'Cerritos', 'state': 'California', 'zip': '90703', 'phone': '(562) 402-7467', 'lat': 33.8613973, 'lng': -118.0932468},
        {'name': 'Tesla Los Gatos', 'address': '15500 Los Gatos Blvd', 'city': 'Los Gatos', 'state': 'California', 'zip': '95032', 'phone': '(408) 827-0065', 'lat': 37.2427983, 'lng': -121.9588203},
        {'name': 'Tesla North Sacramento Pre-Owned Sales Center', 'address': '3650 Dudley Blvd', 'city': 'McClellan Park', 'state': 'California', 'zip': '95652', 'phone': '', 'lat': 38.646242, 'lng': -121.4092914},
        {'name': 'Torrance', 'address': '2560 W. 237th St', 'city': 'Torrance', 'state': 'California', 'zip': '90505', 'phone': '310-517-9688', 'lat': 33.8113302, 'lng': -118.3317427},
        {'name': 'Torrance-Del Amo Mall', 'address': '3525 W Carson St. Space 419', 'city': 'Torrance', 'state': 'California', 'zip': '90503', 'phone': '424-2822994', 'lat': 33.83296, 'lng': -118.350753},
        {'name': 'Upland', 'address': '1018 E 20TH ST', 'city': 'UPLAND', 'state': 'California', 'zip': '91784', 'phone': '909-244-1884', 'lat': 34.1356484, 'lng': -117.6389922},
        {'name': 'Vallejo', 'address': '1001 Admiral Callaghan Ln', 'city': 'Vallejo', 'state': 'California', 'zip': '94591', 'phone': '(707) 917-4719', 'lat': 38.1354929, 'lng': -122.2200951},
        {'name': 'Walnut Creek-Broadway Plaza', 'address': '1246 Broadway Plaza Suite 1094', 'city': 'Walnut Creek', 'state': 'California', 'zip': '94596', 'phone': '(925) 210-1792', 'lat': 37.896195, 'lng': -122.058112},
        {'name': 'West Covina', 'address': '1932 E GARVEY AVE S', 'city': 'West Covina', 'state': 'California', 'zip': '91791', 'phone': '(626) 646-1117', 'lat': 34.0711137, 'lng': -117.903924},
        {'name': 'West Los Angeles-Santa Monica Blvd', 'address': '11163 Santa Monica Boulevard', 'city': 'Los Angeles', 'state': 'California', 'zip': '90025', 'phone': '310-473-8337', 'lat': 34.047526, 'lng': -118.445593}
    ]
    
    # COLORADO (7 dealerships)
    colorado = [
        {'name': 'Aurora', 'address': '11951 E 33rd Ave', 'city': 'Aurora', 'state': 'Colorado', 'zip': '80010', 'phone': '7205594589', 'lat': 39.7643657, 'lng': -104.8492014},
        {'name': 'Colorado Springs', 'address': '1323 Motor City Dr', 'city': 'Colorado Springs', 'state': 'Colorado', 'zip': '80905', 'phone': '7192576988', 'lat': 38.815251, 'lng': -104.830295},
        {'name': 'Gypsum', 'address': '550 Plane St.', 'city': 'Gypsum', 'state': 'Colorado', 'zip': '81637', 'phone': '(970) 687-0050', 'lat': 39.6372817, 'lng': -106.9203594},
        {'name': 'Littleton-Broadway', 'address': '5700 S Broadway', 'city': 'Littleton', 'state': 'Colorado', 'zip': '80121', 'phone': '(303) 632-4200', 'lat': 39.6126591, 'lng': -104.9872324},
        {'name': 'Lone Tree-Park Meadows', 'address': '8401 Park Meadows Center Dr Suite #1650', 'city': 'Lone Tree', 'state': 'Colorado', 'zip': '80124', 'phone': '(303) 792-3450', 'lat': 39.5610436, 'lng': -104.8756401},
        {'name': 'Loveland', 'address': '1606 N Lincoln Ave', 'city': 'Loveland', 'state': 'Colorado', 'zip': '80538', 'phone': '970-541-6691', 'lat': 40.4098982, 'lng': -105.0728223},
        {'name': 'Superior', 'address': '2 S Marshall Rd', 'city': 'Superior', 'state': 'Colorado', 'zip': '80027', 'phone': '(720) 302-9952', 'lat': 39.9549413, 'lng': -105.1649426}
    ]
    
    # CONNECTICUT (3 dealerships)
    connecticut = [
        {'name': 'Milford', 'address': '881 Boston Post Rd', 'city': 'Milford', 'state': 'Connecticut', 'zip': '06460', 'phone': '203-701-5700', 'lat': 41.231376, 'lng': -73.052192},
        {'name': 'Mohegan Sun', 'address': '1 Mohegan Sun Blvd', 'city': 'Uncasville', 'state': 'Connecticut', 'zip': '06382', 'phone': '(860) 383-1101', 'lat': 41.4917972, 'lng': -72.0903866},
        {'name': 'Stamford', 'address': '106 Commerce Rd', 'city': 'Stamford', 'state': 'Connecticut', 'zip': '06902', 'phone': '(203) 658-0581', 'lat': 41.0465665, 'lng': -73.565018}
    ]
    
    # DELAWARE (1 dealership)
    delaware = [
        {'name': 'Christiana Mall', 'address': '132 Christiana Mall Space 1401', 'city': 'Newark', 'state': 'Delaware', 'zip': '19702', 'phone': '302-533-3895', 'lat': 39.679184, 'lng': -75.652264}
    ]
    
    # DISTRICT OF COLUMBIA (1 dealership)
    dc = [
        {'name': 'Washington DC', 'address': '3307 M St NW', 'city': 'Washington', 'state': 'District Of Columbia', 'zip': '20007', 'phone': '(202) 916-3936', 'lat': 38.9052344, 'lng': -77.0666818}
    ]
    
    # FLORIDA (26+ dealerships) - Major state
    florida = [
        {'name': 'Aventura-Aventura Mall', 'address': '19565 Biscayne Blvd #1948', 'city': 'Aventura', 'state': 'Florida', 'zip': '33180', 'phone': '(305) 914-3072', 'lat': 25.9583338, 'lng': -80.1424004},
        {'name': 'Boca Raton', 'address': '6000 Glades Road', 'city': 'Boca Raton', 'state': 'Florida', 'zip': '33431', 'phone': '', 'lat': 26.3643454, 'lng': -80.1335081},
        {'name': 'Clermont', 'address': '16775 State Road 50.', 'city': 'Clermont', 'state': 'Florida', 'zip': '34711', 'phone': '(321) 221-6422', 'lat': 28.54791, 'lng': -81.67682},
        {'name': 'Coral Gables Miami', 'address': '3851 Bird Road', 'city': 'Miami', 'state': 'Florida', 'zip': '33146', 'phone': '786-804-6926', 'lat': 25.735192, 'lng': -80.256911},
        {'name': 'Delray Beach', 'address': '3000 S Federal Hwy', 'city': 'Delray Beach', 'state': 'Florida', 'zip': '33483', 'phone': '305-459-8660', 'lat': 26.4267842, 'lng': -80.073725},
        {'name': 'Fort Lauderdale-Federal Highway', 'address': '2829 N. Federal Highway', 'city': 'Fort Lauderdale', 'state': 'Florida', 'zip': '33306', 'phone': '754-816-3069', 'lat': 26.1626399, 'lng': -80.1169462},
        {'name': 'Fort Myers', 'address': '8900 Colonial Center Dr', 'city': 'Fort Myers', 'state': 'Florida', 'zip': '33905', 'phone': '(239) 895-0626', 'lat': 26.613947, 'lng': -81.810224},
        {'name': 'Gainesville', 'address': '2501 N Main St', 'city': 'Gainesville', 'state': 'Florida', 'zip': '32609', 'phone': '(352) 420-8079', 'lat': 29.6755269, 'lng': -82.3200499},
        {'name': 'Tesla - Tampa', 'address': '2223 N Westshore Blvd Suite 128', 'city': 'Tampa', 'state': 'Florida', 'zip': '33607', 'phone': '813.393.3820', 'lat': 27.9646682, 'lng': -82.5206435},
        {'name': 'Jacksonville', 'address': '11650 Abess Blvd', 'city': 'Jacksonville', 'state': 'Florida', 'zip': '32225', 'phone': '904-924-6442', 'lat': 30.3236219, 'lng': -81.5014571},
        {'name': 'Kissimmee', 'address': '2935 N Orange Blossom Trail', 'city': 'Kissimmee', 'state': 'Florida', 'zip': '34744', 'phone': '(407) 552-0106', 'lat': 28.3352865, 'lng': -81.4029987},
        {'name': 'Merritt Island', 'address': '1545 E Merritt Island Causeway', 'city': 'Merritt Island', 'state': 'Florida', 'zip': '32952', 'phone': '321-456-8002', 'lat': 28.3563464, 'lng': -80.6693214},
        {'name': 'Miami Gardens', 'address': '20850 Northwest 2nd Ave', 'city': 'Miami Gardens', 'state': 'Florida', 'zip': '33169', 'phone': '786 654 5885', 'lat': 25.9677585, 'lng': -80.2065534},
        {'name': 'Miami-Dadeland', 'address': '7535 N Kendall Dr #2420', 'city': 'Miami', 'state': 'Florida', 'zip': '33156', 'phone': '(786) 268-7767', 'lat': 25.689606, 'lng': -80.312492},
        {'name': 'Miami-Design District', 'address': '4039 NE 1st Ave', 'city': 'Miami', 'state': 'Florida', 'zip': '33137', 'phone': '(305) 459-8658', 'lat': 25.814317, 'lng': -80.193706},
        {'name': 'Miami SW 8th Street Supercharger', 'address': '701 S Miami Ave', 'city': 'Miami', 'state': 'Florida', 'zip': '33130-1946', 'phone': '', 'lat': 25.7673386, 'lng': -80.1932669},
        {'name': 'Naples-Waterside Shops', 'address': '5415 Tamiami Trail N. H-2', 'city': 'Naples', 'state': 'Florida', 'zip': '34108', 'phone': '', 'lat': 26.213349, 'lng': -81.802654},
        {'name': 'Orlando', 'address': '2214 John Young Pkwy', 'city': 'Orlando', 'state': 'Florida', 'zip': '32804', 'phone': '407-533-4117', 'lat': 28.573101, 'lng': -81.4174589},
        {'name': 'Orlando - Florida Mall Showroom', 'address': '8001 S Orange Blossom Trail Space 1280A', 'city': 'Orlando', 'state': 'Florida', 'zip': '32809', 'phone': '4072043985', 'lat': 28.445935, 'lng': -81.394502},
        {'name': 'Orlando-6855 Lee Vista Blvd', 'address': '6855 Lee Vista Blvd', 'city': 'Orlando', 'state': 'Florida', 'zip': '32822', 'phone': '(689) 256-2518', 'lat': 28.46707, 'lng': -81.28936},
        {'name': 'Sarasota', 'address': '135 University Town Center Dr', 'city': 'Sarasota', 'state': 'Florida', 'zip': '34243', 'phone': '(941) 413-4196', 'lat': 27.3877527, 'lng': -82.4516714},
        {'name': 'St. Petersburg', 'address': '4601 34TH ST N', 'city': 'Saint Petersburg', 'state': 'Florida', 'zip': '33714', 'phone': '(727) 655-6552', 'lat': 27.8141537, 'lng': -82.6785525},
        {'name': 'Tallahassee', 'address': '2412 W Tennessee St', 'city': 'Tallahassee', 'state': 'Florida', 'zip': '32304', 'phone': '(850) 354-7586', 'lat': 30.4484925, 'lng': -84.3271686},
        {'name': 'Tampa', 'address': '11945 North Florida Avenue', 'city': 'Tampa', 'state': 'Florida', 'zip': '33612', 'phone': 'Store & Service:(813) 496-3039', 'lat': 28.057142, 'lng': -82.458289},
        {'name': 'Doral', 'address': '9950 NW 25TH ST', 'city': 'DORAL', 'state': 'Florida', 'zip': '33172', 'phone': '(786) 582-3750', 'lat': 25.795779, 'lng': -80.357621},
        {'name': 'Naples', 'address': '4555 Radio Rd', 'city': 'Naples', 'state': 'Florida', 'zip': '34104', 'phone': '', 'lat': 26.1539081, 'lng': -81.7547313},
        {'name': 'Tesla Paddock Mall Pop Up', 'address': '3100 SW College Rd', 'city': 'Ocala', 'state': 'Florida', 'zip': '34474', 'phone': '(352) 420-8079', 'lat': 29.1590819, 'lng': -82.1730628},
        {'name': 'Pensacola', 'address': '312 E 9 Mile Rd', 'city': 'Pensacola', 'state': 'Florida', 'zip': '32514', 'phone': '(850) 876-7858', 'lat': 30.53425, 'lng': -87.25911},
        {'name': 'Tesla Town Center at Boca Pop-up', 'address': '6000 Glades Rd', 'city': 'Boca Raton', 'state': 'Florida', 'zip': '33431', 'phone': '(561) 368-6000', 'lat': 26.3625607, 'lng': -80.1326512},
        {'name': 'West Palm Beach', 'address': '5544 Okeechobee Boulevard', 'city': 'West Palm Beach', 'state': 'Florida', 'zip': '33417', 'phone': '(561) 841-9281', 'lat': 26.706516, 'lng': -80.128119}
    ]
    
    # Add all states
    all_states = [arizona, california, colorado, connecticut, delaware, dc, florida]
    
    for state_data in all_states:
        for dealer in state_data:
            dealerships.append({
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
    
    return dealerships

def main():
    print("="*60)
    print("TESLA DEALERSHIP COMPREHENSIVE SCRAPER")
    print("="*60)
    print(f"TARGET: ~272 Tesla dealerships in USA")
    print(f"CURRENT: 78 dealerships (Arizona: 8, California: 70)")
    print(f"MISSING: ~194 dealerships")
    print("="*60)
    
    dealerships = extract_all_tesla_dealerships_complete()
    
    # Save to JSON
    output_file = '/Users/kimseanpardo/autodealerships/tesla_dealerships_usa.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dealerships, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ SAVED: {len(dealerships)} dealerships to {output_file}")
    
    # Statistics
    states = {}
    for dealer in dealerships:
        state = dealer['state']
        states[state] = states.get(state, 0) + 1
    
    print(f"\n📊 CURRENT STATISTICS:")
    print(f"Total dealerships: {len(dealerships)}")
    print(f"States covered: {len(states)}")
    print(f"Progress: {len(dealerships)}/272 ({len(dealerships)/272*100:.1f}%)")
    print(f"Still needed: {272 - len(dealerships)} dealerships")
    
    print(f"\n📋 BY STATE:")
    for state, count in sorted(states.items()):
        print(f"  {state}: {count}")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"Need to add ~{272 - len(dealerships)} more dealerships from remaining states")
    print(f"Major states to add: Texas (27), New York, Illinois, Pennsylvania, etc.")

if __name__ == "__main__":
    main()
