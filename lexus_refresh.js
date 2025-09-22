const { chromium } = require('playwright');

async function refreshLexus() {
  console.log('Starting Lexus scraper with page refresh...');
  
  const browser = await chromium.launch({ 
    headless: false, 
    slowMo: 2000,
    args: ['--start-maximized']
  });
  
  const page = await browser.newPage();
  
  try {
    const zipCodes = ['40201', '40501', '42101', '70112', '70801', '71101', '04101', '04401', '04038', '21201'];
    const allDealers = [];
    
    for (let i = 0; i < zipCodes.length; i++) {
      const zip = zipCodes[i];
      console.log(`\nSearching ZIP ${zip} (${i + 1}/${zipCodes.length})...`);
      
      try {
        // Always start fresh
        await page.goto('https://www.lexus.com/dealers', { waitUntil: 'networkidle' });
        await page.waitForTimeout(5000);
        
        console.log('  Waiting for ZIP input...');
        await page.waitForSelector('input[placeholder="Enter ZIP"]', { timeout: 15000 });
        
        console.log('  Entering ZIP code...');
        await page.fill('input[placeholder="Enter ZIP"]', '');
        await page.fill('input[placeholder="Enter ZIP"]', zip);
        await page.waitForTimeout(1000);
        
        console.log('  Clicking search...');
        const searchButton = await page.$('button:has-text("Zip Search Icon")');
        if (searchButton) {
          await searchButton.click();
        } else {
          await page.press('input[placeholder="Enter ZIP"]', 'Enter');
        }
        
        await page.waitForTimeout(5000);
        
        console.log('  Extracting dealers...');
        const dealers = await page.evaluate((zipCode) => {
          const containers = document.querySelectorAll('[data-testid="DealerCard"]');
          const dealers = [];
          
          containers.forEach(container => {
            const nameEl = container.querySelector('[data-testid="Typography"]');
            const name = nameEl ? nameEl.textContent.trim() : '';
            
            if (name) {
              dealers.push({
                name: name.toUpperCase(),
                search_zip: zipCode
              });
            }
          });
          
          return dealers;
        }, zip);
        
        allDealers.push(...dealers);
        console.log(`  Found ${dealers.length} dealers for ZIP ${zip}`);
        
        dealers.forEach((dealer, index) => {
          console.log(`    ${index + 1}. ${dealer.name}`);
        });
        
      } catch (error) {
        console.log(`  Error searching ZIP ${zip}: ${error.message}`);
      }
      
      console.log('  Waiting before next search...');
      await page.waitForTimeout(3000);
    }
    
    console.log(`\nTotal dealers found: ${allDealers.length}`);
    
    // Show unique dealers
    const uniqueDealers = [];
    const seen = new Set();
    allDealers.forEach(dealer => {
      if (!seen.has(dealer.name)) {
        seen.add(dealer.name);
        uniqueDealers.push(dealer);
      }
    });
    
    console.log(`Unique dealers: ${uniqueDealers.length}`);
    uniqueDealers.forEach((dealer, index) => {
      console.log(`${index + 1}. ${dealer.name} (found via ZIP ${dealer.search_zip})`);
    });
    
    console.log('Keeping browser open for 60 seconds...');
    await page.waitForTimeout(60000);
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
}

refreshLexus();
