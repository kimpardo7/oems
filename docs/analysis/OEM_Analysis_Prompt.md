# OEM Dealer API Analysis Prompt

## Task Overview
Systematically analyze automotive OEM websites to identify and extract hidden API endpoints for dealer locator or inventory search functionalities. The goal is to enable direct retrieval of complete dealer or inventory datasets without manual interaction or pagination.

## Core Requirements
1. **Utilize browser automation** (Playwright) to navigate to each OEM's dealer locator page
2. **Observe network requests** (Network tab, XHR/Fetch filter) triggered by search actions
3. **Identify candidate API requests** based on:
   - JSON responses
   - Relevant URL keywords (dealer, locator, inventory, search)
   - Query parameters (lat, lng, zip, radius, page, limit, offset)
4. **Confirm API endpoints** by inspecting JSON responses and testing parameter changes
5. **Test for bulk retrieval capabilities** by increasing limit/size parameters or documenting pagination strategies
6. **Document findings** in specific format for each OEM
7. **Verify endpoints work outside browser** using curl with proper headers

## Analysis Process for Each OEM

### Step 1: Navigate to Dealer Locator
- Read next OEM from `OEMs.txt`
- Navigate to dealer locator URL using Playwright
- Accept cookies/privacy settings if prompted

### Step 2: Interact with Search Functionality
- Click on search input fields (ZIP code, city, etc.)
- Type test search terms (e.g., "90210", "New York")
- Click submit/search buttons
- Observe if search triggers API calls

### Step 3: Analyze Network Requests
- Check network tab for API calls
- Look for endpoints with keywords: dealer, locator, inventory, search
- Identify JSON responses with dealer data
- Note request methods (GET/POST) and parameters

### Step 4: Test API Endpoints
- Use curl to test identified endpoints
- Include proper headers (Accept, Referer, User-Agent, Origin)
- Test parameter variations (limit, radius, etc.)
- Verify data extraction works outside browser

### Step 5: Document Findings
- Update `OEM_Dealer_APIs.md` with detailed API information
- Update `OEM_Tracking.md` with status and progress
- Categorize as: "API Found", "No API Found (Google Maps/Other)", or "Pending"

## Documentation Format

### For API Found:
```markdown
### X. [OEM Name]
**API Endpoint URL:** `[URL]`
**Method:** [GET/POST]
**Parameters:**
- [parameter]: [description]
**Pagination Strategy:** [description]
**Example Call:** `curl [command]`
```

### For No API Found:
```markdown
### X. [OEM Name]
**Status:** No direct API endpoint found. Uses [Google Maps/embedded data/etc.].
**Note:** [Brief explanation of what the site uses instead]
```

## Key Technical Tools
- **Browser Automation:** `mcp_Playwright_browser_navigate`, `mcp_Playwright_browser_click`, `mcp_Playwright_browser_type`, `mcp_Playwright_browser_network_requests`
- **API Testing:** `curl` with headers (`-H 'Referer'`, `-H 'User-Agent'`, `-H 'Accept'`)
- **File Management:** `read_file`, `search_replace`, `edit_file`

## Common Patterns to Look For
1. **Direct APIs:** `/api/dealers`, `/services/dealers`, `/cxservices/dealer`
2. **Google Maps Integration:** No direct API, uses Google Places API
3. **Embedded Data:** Client-side filtering of pre-loaded dealer data
4. **Authentication Required:** APIs that need specific headers or tokens

## Progress Tracking
- Maintain `OEM_Tracking.md` with current status
- Update progress summary (total, found, no API, pending, completion %)
- Ensure no OEMs are skipped from the master list

## Rules to Follow
- Return only structured dealer/inventory data
- Avoid HTML scraping unless no API is available
- Verify endpoints work outside browser
- Test for bulk retrieval capabilities
- Document pagination strategies
- Include example curl commands for working APIs

## Continue Command
"Continue systematically analyzing the remaining OEMs from OEMs.txt. For each OEM:
1. Navigate to their dealer locator page
2. Interact with search functionality to trigger API calls
3. Analyze network requests for dealer/inventory endpoints
4. Test identified APIs with curl
5. Update both OEM_Dealer_APIs.md and OEM_Tracking.md
6. Move to next OEM without stopping until all are completed"
