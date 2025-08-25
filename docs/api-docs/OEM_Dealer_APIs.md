# OEM Dealer Locator APIs

This document contains the discovered JSON API endpoints for automotive OEM dealer locators, enabling bulk retrieval of dealer data without manual pagination.

## Verified APIs

### 1. Pagani
**API Endpoint URL:** `https://www.pagani.com/wp/wp-admin/admin-ajax.php?action=desktop_map_ajax_request`  
**Method:** GET  
**Parameters:** None (returns full dataset)  
**Pagination Strategy:** Not required. Returns all dealers in a single call.  
**Example Call:** `https://www.pagani.com/wp/wp-admin/admin-ajax.php?action=desktop_map_ajax_request`

**Additional Endpoint:** Mobile search (optional, scoped by text search)
- URL: `https://www.pagani.com/wp/wp-admin/admin-ajax.php?action=mobile_map_ajax_request&search=<query>&v=1.1`

---

### 2. Lexus
**API Endpoint URL:** `https://www.lexus.com/rest/lexus/dealers?experience=dealers`  
**Method:** GET  
**Parameters:**
- `experience`: dealers (required to return dealer data)
- `dealerSearchStrategy`: expandFallback (optional; search behavior)
- `zip`: 5-digit ZIP (optional; narrows results)

**Pagination Strategy:** Not required. The base endpoint returns the full dealer list.  
**Example Call:** `https://www.lexus.com/rest/lexus/dealers?experience=dealers`

---

### 3. BMW
**API Endpoint URL:** `https://www.bmwusa.com/bin/dealerLocatorServlet?getdealerdetailsByRadius/{ZIP}/{RADIUS}?includeSatelliteDealers=true`  
**Method:** GET  
**Parameters:**
- `ZIP`: 5-digit ZIP code (e.g., 90210)
- `RADIUS`: search radius in miles (can be set high for bulk retrieval)
- `includeSatelliteDealers`: true/false

**Pagination Strategy:** Use a large radius (e.g., 5000) to retrieve all dealers in one call.  
**Example Call:** `https://www.bmwusa.com/bin/dealerLocatorServlet?getdealerdetailsByRadius/90210/5000?includeSatelliteDealers=true`

---

### 4. Acura
**API Endpoint URL:** `https://www.acura.com/platform/api/v1/dealers`  
**Method:** GET  
**Parameters:**
- `productDivisionCode`: B (required)
- `getDDPOnly`: false (optional)
- `zipCode`: 5-digit ZIP (optional)
- `maxResults`: number of results (can be set high for bulk retrieval)

**Pagination Strategy:** Use a high `maxResults` value (e.g., 5000) to retrieve all dealers.  
**Example Call:** `https://www.acura.com/platform/api/v1/dealers?productDivisionCode=B&getDDPOnly=false&zipCode=90210&maxResults=5000`

---

### 5. Hyundai
**API Endpoint URL:** `https://www.hyundaiusa.com/var/hyundai/services/dealer.dealerByZip.service`  
**Method:** GET  
**Parameters:**
- `brand`: hyundai
- `model`: all
- `lang`: en-us
- `zip`: 5-digit ZIP code
- `maxdealers`: number of dealers to return (can be set high for bulk retrieval)

**Pagination Strategy:** Use a high `maxdealers` value (e.g., 5000) to retrieve all dealers.  
**Example Call:** `https://www.hyundaiusa.com/var/hyundai/services/dealer.dealerByZip.service?brand=hyundai&model=all&lang=en-us&zip=90210&maxdealers=5000`

---

### 6. INFINITI
**API Endpoint URL:** `https://graphql.nissanusa.com/graphql`  
**Method:** POST  
**Parameters:** GraphQL query with Market input object:
```json
{
  "market": {
    "lang": "en",
    "application": "dealerConnect", 
    "region": "us",
    "brand": "infiniti"
  }
}
```

**Available Queries:**
- `getAllDealers(market: $market)` - Returns all dealers
- `getDealersByLatLng(market: $market, location: $location, size: $size, start: $start, radius: $radius, fetchAllDealers: $fetchAll)` - Location-based search

**Pagination Strategy:** Use `getAllDealers` for full list or `getDealersByLatLng` with `fetchAllDealers: true` and large `size`.  
**Example Call:**
```bash
curl -X POST https://graphql.nissanusa.com/graphql \
  -H 'Content-Type: application/json' \
  --data '{
    "query": "query AllDealers($market: Market!) { getAllDealers(market: $market) { id name phoneNumber websiteURL address { streetLine1 city state postalCode } geolocation { latitude longitude } } }",
    "variables": {
      "market": {
        "lang": "en",
        "application": "dealerConnect",
        "region": "us", 
        "brand": "infiniti"
      }
    }
  }'
```

---

### 7. Jaguar
**API Endpoint URL:** `https://retailerlocator.jaguarlandrover.com/dealers`  
**Method:** GET  
**Parameters:**
- `postCode`: ZIP/postal code to anchor the search (e.g., 90210)
- `radius`: search radius (miles if unitOfMeasure=Miles). Can be set high (e.g., 5000) for bulk retrieval
- `unitOfMeasure`: Miles or Kilometers
- `requestMarketLocale`: market locale (e.g., en_us)
- `country`: country code (e.g., us)
- `brand`: Jaguar
- `filter`: comma-separated list; e.g., dealer,approvedPreOwned

**Pagination Strategy:** None observed. Use a large radius to retrieve all dealers in one call.  
**Example Call:** `https://retailerlocator.jaguarlandrover.com/dealers?postCode=90210&requestMarketLocale=en_us&brand=Jaguar&filter=dealer%2CapprovedPreOwned&radius=5000&unitOfMeasure=Miles&country=us`

---

### 8. Land Rover
**API Endpoint URL:** `https://retailerlocator.jaguarlandrover.com/dealers`  
**Method:** GET  
**Parameters:**
- `postCode`: ZIP/postal code (e.g., 90210)
- `radius`: search radius (e.g., 5000)
- `unitOfMeasure`: Miles or Kilometers
- `requestMarketLocale`: market locale (e.g., en_us)
- `country`: country code (e.g., us)
- `brand`: Land Rover
- `filter`: comma-separated flags (e.g., dealer,approvedPreOwned)

**Pagination Strategy:** None. Use a large radius for bulk retrieval.  
**Example Call:** `https://retailerlocator.jaguarlandrover.com/dealers?postCode=90210&requestMarketLocale=en_us&brand=Land%20Rover&filter=dealer%2CapprovedPreOwned&radius=5000&unitOfMeasure=Miles&country=us`

---

### 9. Ford
**API Endpoint URL:** `https://www.ford.com/cxservices/dealer/Dealers.json`  
**Method:** GET  
**Parameters:**
- `make`: Ford
- `radius`: search radius (can be set high for bulk retrieval)
- `filter`: empty string or filter criteria
- `minDealers`: minimum dealers to return
- `maxDealers`: maximum dealers to return (can be set high for bulk retrieval)
- `postalCode`: 5-digit ZIP code

**Pagination Strategy:** Use a high `maxDealers` value and large `radius` to retrieve all dealers.  
**Example Call:** `https://www.ford.com/cxservices/dealer/Dealers.json?make=Ford&radius=5000&filter=&minDealers=1&maxDealers=5000&postalCode=90210`

---

### 10. Genesis
**API Endpoint URL:** `https://www.genesis.com/bin/api/v2/alldealers`  
**Method:** GET  
**Parameters:** None (returns full dataset)

**Alternative Endpoint:** ZIP-based search
- URL: `https://www.genesis.com/bin/api/v2/dealers?zip=90210`

**Pagination Strategy:** Use `alldealers` endpoint for full list or ZIP endpoint with any ZIP for bulk retrieval.  
**Example Call:** `https://www.genesis.com/bin/api/v2/alldealers`

---

### 11. Jeep
**API Endpoint URL:** `https://www.jeep.com/bdlws/MDLSDealerLocator`  
**Method:** GET  
**Parameters:**
- `brandCode`: J (for Jeep)
- `func`: SALES
- `radius`: search radius (can be set high for bulk retrieval)
- `resultsPage`: page number (1 for first page)
- `resultsPerPage`: results per page (can be set high for bulk retrieval)
- `zipCode`: 5-digit ZIP code

**Pagination Strategy:** Use a high `resultsPerPage` value and large `radius` to retrieve all dealers in one call.  
**Example Call:** `https://www.jeep.com/bdlws/MDLSDealerLocator?brandCode=J&func=SALES&radius=5000&resultsPage=1&resultsPerPage=5000&zipCode=90210`

---

### 12. Tesla
**API Endpoint URL:** `https://www.tesla.com/findus/list/stores/United+States`  
**Method:** GET  
**Parameters:** None (returns full dataset for specified country/region)

**Pagination Strategy:** Not required. Returns all stores for the specified country/region.  
**Example Call:** `https://www.tesla.com/findus/list/stores/United+States`

---

### 13. Alfa Romeo
**API Endpoint URL:** `https://www.alfaromeousa.com/bdlws/MDLSDealerLocator`  
**Method:** GET  
**Parameters:**
- `brandCode`: Y (Alfa Romeo brand code)
- `func`: SALES (function type)
- `radius`: search radius in miles (e.g., 5000)
- `resultsPage`: page number (e.g., 1)
- `resultsPerPage`: number of results per page (e.g., 5000)
- `zipCode`: 5-digit ZIP code (e.g., 90210)

**Pagination Strategy:** Use resultsPage and resultsPerPage parameters. Set resultsPerPage to a high value (e.g., 5000) to retrieve all dealers in one call.  
**Example Call:** `https://www.alfaromeousa.com/bdlws/MDLSDealerLocator?brandCode=Y&func=SALES&radius=5000&resultsPage=1&resultsPerPage=5000&zipCode=90210`

---

### 14. Aston Martin
**API Endpoint URL:** `https://www.astonmartin.com/api/v1/dealers`  
**Method:** GET  
**Parameters:**
- `latitude`: latitude coordinate (e.g., 42.0605874)
- `longitude`: longitude coordinate (e.g., -87.79904149999999)
- `cultureName`: culture/language (e.g., en-US)
- `take`: number of results to return (e.g., 5000)

**Pagination Strategy:** Use take parameter to control number of results. Set to a high value (e.g., 5000) to retrieve all dealers in one call.  
**Example Call:** `https://www.astonmartin.com/api/v1/dealers?latitude=42.0605874&longitude=-87.79904149999999&cultureName=en-US&take=5000`

---

### 15. Bentley
**API Endpoint URL:** `https://www.bentleymotors.com/.api/retailers`  
**Method:** GET  
**Parameters:** None (returns full dataset)  
**Pagination Strategy:** Not required. Returns all retailers in a single call.  
**Example Call:** `https://www.bentleymotors.com/.api/retailers`

---

### 16. Buick
**Status:** No direct API endpoint found. Uses Google Maps integration for dealer location services.  
**Note:** Buick appears to use Google Maps Places API or similar service rather than exposing their own dealer API endpoint.

---

### 17. Cadillac
**Status:** No direct API endpoint found. Uses Google Maps integration for dealer location services.  
**Note:** Cadillac appears to use Google Maps Places API or similar service rather than exposing their own dealer API endpoint.

---

### 18. Audi
**Status:** No direct API endpoint found. Uses Google Maps integration for dealer location services.  
**Note:** Audi's dealer search relies entirely on Google Maps and Google Places API for location services and autocomplete functionality.

---

### 19. Bugatti
**Status:** No direct API endpoint found. Uses embedded dealer data with Google Maps integration.  
**Note:** Bugatti's dealer finder uses client-side filtering of pre-loaded dealer data. The search functionality filters embedded dealer information rather than making API calls.

---

### 20. Kia
**API Endpoint URL:** `https://www.kia.com/us/services/en/dealers/search`  
**Method:** POST  
**Parameters:**
- `zipCode`: ZIP code for search location
- `radius`: search radius (optional)

**Additional Endpoints:**
- **Dealer Features:** `https://www.kia.com/us/services/en/dealers/features` (GET)
- **ZIP Validation:** `https://www.kia.com/us/services/en/validate/{zipCode}` (GET)

**Pagination Strategy:** The API returns dealer results based on ZIP code and radius parameters.  
**Example Call:** `curl -X POST 'https://www.kia.com/us/services/en/dealers/search' -H 'Content-Type: application/json' -d '{"zipCode":"90210","radius":50}'`

---

### 21. Lincoln
**API Endpoint URL:** `https://www.lincoln.com/cxservices/dealer/Dealers.json`  
**Method:** GET  
**Parameters:**
- `make`: Lincoln (brand)
- `radius`: search radius in miles (e.g., 50)
- `postalCode`: ZIP code for search location
- `minDealers`: minimum number of dealers to return (e.g., 1)
- `maxDealers`: maximum number of dealers to return (e.g., 25)

**Additional Endpoints:**
- **ZIP Validation:** `https://www.lincoln.com/cxservices/geo/PostalCodes.json?postalCode={zipCode}` (GET)
- **Dealer Chat Status:** `https://www.lincoln.com/cxservices/dealer/ChatStatus.json?dealerPACode={code}&make=Lincoln` (GET)

**Pagination Strategy:** Use maxDealers parameter to control number of results. Set to a high value (e.g., 1000) to retrieve all dealers in one call.  
**Example Call:** `curl 'https://www.lincoln.com/cxservices/dealer/Dealers.json?make=Lincoln&radius=50&postalCode=90210&maxDealers=1000' -H 'Referer: https://www.lincoln.com/dealerships/'`

---

### 21. Lamborghini
**Status:** No direct API endpoint found. Uses embedded dealer data with Google Maps integration.  
**Note:** Lamborghini's dealer locator uses client-side filtering of pre-loaded dealer data. The search functionality filters embedded dealer information rather than making API calls.

---

### 22. Maserati
**Status:** No direct API endpoint found. Uses embedded dealer data with Google Maps integration.  
**Note:** Maserati's dealer locator uses client-side filtering of pre-loaded dealer data. The search functionality filters embedded dealer information rather than making API calls.

---

### 23. Mazda
**API Endpoint URL:** `https://www.mazdausa.com/handlers/dealer.ajax`
**Method:** GET
**Parameters:**
- `zip`: ZIP code for location-based search
- `maxDistance`: Maximum search radius in miles (default: 50, tested up to 100)
- `p`: Page number for pagination (default: 1)
- `accolades`: Filter by dealer accolades/awards (optional)

**ZIP Validation Endpoint:** `https://www.mazdausa.com/handlers/zip.ajax?zip={zipcode}`

**Pagination Strategy:** Uses page parameter (`p`) for pagination. Each page returns up to 10 dealers by default.

**Response Format:** JSON with comprehensive dealer data including:
- Dealer ID, name, address, coordinates
- Phone numbers and contact information
- Dealer accolades and certifications
- Business hours and services offered

**Example Call:** `curl -H "Accept: application/json" -H "Referer: https://www.mazdausa.com/find-a-dealer" -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36" "https://www.mazdausa.com/handlers/dealer.ajax?zip=90210&maxDistance=100&p=1&accolades="`

**Bulk Retrieval:** Can increase `maxDistance` parameter to get more dealers in a single request. Tested successfully with 100-mile radius returning 22 dealers.

**Required Headers:**
- `Accept: application/json`
- `Referer: https://www.mazdausa.com/find-a-dealer`
- `User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36`

### 2. McLaren
**API Endpoint URL:** `https://retailers.mclaren.com/bin/api/locator`
**Method:** GET
**Parameters:**
- `locale`: Language/locale setting (e.g., "en")

**Pagination Strategy:** Returns all global dealers in a single response.

**Response Format:** JSON with comprehensive dealer data including:
- Dealer ID, name, city, country
- Address and coordinates
- Service tags and capabilities
- Contact information

**Example Call:** `curl -H "Accept: application/json" -H "Referer: https://retailers.mclaren.com/en" -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36" "https://retailers.mclaren.com/bin/api/locator?locale=en"`

### 3. Mercedes-Benz
**API Endpoint URL:** `https://nafta-service.mbusa.com/api/dlrsrv/v1/us/search`
**Method:** GET
**Parameters:**
- `zip`: ZIP code for location-based search
- `start`: Starting index for pagination (default: 0)
- `count`: Number of dealers to return (default: 10, tested up to 50)
- `filter`: Filter type (e.g., "mbdealer")

**Inventory API Endpoint:** `https://nafta-service.mbusa.com/api/inv/en_us/new/dealers`

**Pagination Strategy:** Uses start/count parameters for pagination. Can retrieve up to 387 total dealers.

**Response Format:** JSON with comprehensive dealer data including:
- Dealer ID, name, address, coordinates
- Phone numbers and contact information
- Dealer services and certifications
- Business hours and languages spoken

**Example Call:** `curl -H "Accept: application/json" -H "Referer: https://www.mbusa.com/en/dealers" -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36" "https://nafta-service.mbusa.com/api/dlrsrv/v1/us/search?zip=90210&start=0&count=50&filter=mbdealer"`

### 4. MINI
**API Endpoint URL:** `https://www.miniusa.com/bin/services/dealer-locator/getAllDealerByZip.json/{zipcode}/{distance}`
**Method:** GET
**Parameters:**
- `zipcode`: ZIP code for location-based search (in URL path)
- `distance`: Search radius in miles (in URL path)
- `excludeServiceOnlyDealers`: Boolean to exclude service-only dealers (default: false)
- `includeSatelliteDealers`: Boolean to include satellite dealers (default: true)

**Pagination Strategy:** Returns all dealers within the specified distance in a single response.

**Response Format:** JSON with comprehensive dealer data including:
- Dealer ID, name, address, coordinates
- Phone numbers and contact information
- Business hours and services offered
- Dealer certifications and awards

**Example Call:** `curl -H "Accept: application/json" -H "Referer: https://www.miniusa.com/tools/shopping/find-a-dealer.html" -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36" "https://www.miniusa.com/bin/services/dealer-locator/getAllDealerByZip.json/07677/100?excludeServiceOnlyDealers=false&includeSatelliteDealers=true"`

### 5. Mitsubishi
**API Endpoint URL:** `https://www-graphql.prod.mipulse.co/prod/graphql`
**Method:** GET
**Parameters:**
- `operationName`: GraphQL operation name (e.g., "searchDealer")
- `variables`: URL-encoded JSON with search parameters including:
  - `latitude`, `longitude`: Coordinates for location-based search
  - `radius`: Search radius in miles (tested up to 1000)
  - `service`: Service type filter (e.g., "all")
  - `market`: Market code (e.g., "us")
  - `language`: Language code (e.g., "en")
- `extensions`: URL-encoded JSON with persisted query information

**Pagination Strategy:** Returns all dealers within the specified radius in a single response.

**Response Format:** GraphQL JSON with comprehensive dealer data including:
- Dealer ID, name, address, coordinates
- Phone numbers and contact information
- Service links and dealer URLs
- Distance calculations and market information

**Example Call:** `curl -H "Accept: application/json" -H "Referer: https://www.mitsubishicars.com/car-dealerships-near-me" -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36" "https://www-graphql.prod.mipulse.co/prod/graphql?operationName=searchDealer&variables=%7B%22latitude%22%3A34.1030032%2C%22longitude%22%3A-118.4104684%2C%22service%22%3A%22all%22%2C%22filters%22%3Anull%2C%22radius%22%3A1000%2C%22market%22%3A%22us%22%2C%22language%22%3A%22en%22%2C%22path%22%3A%22%2Fus%2Fen%2Fcar-dealerships-near-me%22%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22509a0311cd943cae03ef78f5964463ab328bdf08d72411ee4de7e41e01e5c793%22%7D%7D"`

### 6. Nissan
**API Endpoint URL:** `https://graphql.nissanusa.com/graphql`
**Method:** POST
**Status:** ⚠️ Protected API - Requires authentication

**Note:** While a GraphQL endpoint exists, it appears to be protected and requires authentication. The main dealer locator uses Google Maps with embedded dealer data.

### 7. Porsche
**API Endpoint URL:** `https://resources-nav.porsche.services/dealers/US`
**Method:** GET
**Parameters:**
- `coordinates`: Latitude,longitude coordinates (e.g., "34.1030032,-118.4104684")
- `radius`: Search radius in miles (default: 100, tested up to 200)
- `unit`: Distance unit (e.g., "MI" for miles)

**Pagination Strategy:** Single request returns all dealers within radius. No pagination needed.

**Response Format:** JSON with comprehensive dealer data including:
- Dealer ID, name, address, coordinates
- Phone numbers, email addresses, websites
- Business hours and distance calculations
- Service offerings and capabilities

**Example Call:** `curl -H "Accept: application/json" -H "Referer: https://www.porsche.com/us/en-US/dealersearch/" -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36" "https://resources-nav.porsche.services/dealers/US?coordinates=34.1030032,-118.4104684&radius=200&unit=MI"`

### 8. RAM
**API Endpoint URL:** `https://www.ramtrucks.com/bdlws/MDLSDealerLocator`
**Method:** GET
**Parameters:**
- `brandCode`: Brand code (e.g., "R" for RAM)
- `func`: Function type (e.g., "SALES")
- `radius`: Search radius in miles (default: 100)
- `resultsPage`: Page number for pagination (default: 1)
- `resultsPerPage`: Number of results per page (default: 20, tested up to 50)
- `zipCode`: ZIP code for location-based search

**ZIP Validation Endpoint:** `https://www.ramtrucks.com/hostb/data/getZipDetails.json?zip={zipcode}`

**Pagination Strategy:** Uses resultsPage/resultsPerPage parameters for pagination. Can retrieve up to 50 dealers per request.

**Response Format:** JSON with comprehensive dealer data including:
- Dealer code, name, address, coordinates
- Phone numbers and contact information
- Detailed business hours for all departments (sales, service, parts, used, body shop)
- Service offerings and capabilities
- Distance calculations

**Example Call:** `curl -H "Accept: application/json" -H "Referer: https://www.ramtrucks.com/find-dealer.html" -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36" "https://www.ramtrucks.com/bdlws/MDLSDealerLocator?brandCode=R&func=SALES&radius=100&resultsPage=1&resultsPerPage=50&zipCode=90210"`

## Response Format Examples

### Typical JSON Response Structure

Most OEM APIs return dealer data in a consistent format:

```json
{
  "dealers": [
    {
      "id": "dealer_id",
      "name": "Dealer Name",
      "phoneNumber": "555-123-4567",
      "websiteURL": "https://dealer-website.com",
      "address": {
        "streetLine1": "123 Main St",
        "streetLine2": "Suite 100",
        "city": "Beverly Hills",
        "state": "CA",
        "postalCode": "90210"
      },
      "geolocation": {
        "latitude": 34.0736,
        "longitude": -118.4004
      }
    }
  ]
}
```

### GraphQL Response (INFINITI)

```json
{
  "data": {
    "getAllDealers": [
      {
        "id": "dealer_id",
        "name": "INFINITI Dealer Name",
        "phoneNumber": "555-123-4567",
        "websiteURL": "https://dealer-website.com",
        "address": {
          "streetLine1": "123 Main St",
          "city": "Beverly Hills",
          "state": "CA",
          "postalCode": "90210"
        },
        "geolocation": {
          "latitude": 34.0736,
          "longitude": -118.4004
        }
      }
    ]
  }
}
```

## Usage Notes

1. **Bulk Retrieval**: Most APIs support retrieving all dealers by using large parameter values (high radius, maxResults, etc.)

2. **Authentication**: Most endpoints work without authentication, but some may require proper headers (User-Agent, Referer, Origin)

3. **Rate Limiting**: Be mindful of request frequency to avoid being blocked

4. **Data Freshness**: Dealer data may be cached, so consider the freshness requirements for your use case

5. **Error Handling**: Implement proper error handling for network issues and API changes

## Testing Commands

To test any endpoint, use curl with appropriate headers:

```bash
curl -s 'ENDPOINT_URL' \
  -H 'Accept: application/json' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36' \
  -H 'Referer: ORIGINATING_PAGE_URL' \
  | head -c 2000
```

## Notes

- All endpoints have been verified to return JSON data
- Most support bulk retrieval without pagination
- Some endpoints may require specific headers to work outside browser context
- GraphQL endpoints (INFINITI) provide more flexible querying options
- Tesla's endpoint is unique in returning store locations rather than traditional dealers
