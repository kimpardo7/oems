const { chromium } = require('playwright');
const fs = require('fs');

async function simpleLexusScraper() {
  console.log('🚀 Starting Simple Lexus Scraper...');
  
  const browser = await chromium.launch({ 
    headless: false, 
    slowMo: 2000,
    args: ['--start-maximized']
  });
  
  const page = await browser.newPage();
  
  try {
    console.log('🌐 Navigating to Lexus dealer page...');
    await page.goto('https://www.lexus.com/dealers');
    await page.waitForTimeout(5000);
    
    console.log('📄 Page loaded! Looking for ZIP input...');
    await page.waitForSelector('input[placeholder="Enter ZIP"]', { timeout: 10000 });
    
    // Create fresh data structure
    const lexusData = {
      brand: "Lexus",
      scraped_date: new Date().toISOString(),
      total_dealers: 0,
      states: {}
    };
    
    // Just process a few states to test
    const testStates = ['Kentucky', 'Louisiana', 'Maine'];
    const stateZipCodes = {
      'Kentucky': ['40202', '40502'],
      'Louisiana': ['70112', '70801'],
      'Maine': ['04101', '04401']
    };
    
    let totalDealers = 0;
    
    for (const state of testStates) {
      console.log(`\n🌎 Processing ${state}...`);
      
      const stateDealers = new Set();
      const zipCodes = stateZipCodes[state] || [];
      
      for (const zipCode of zipCodes) {
        console.log(`   📍 Searching ZIP ${zipCode}...`);
        
        try {
          // Clear and enter ZIP code
          await page.fill('input[placeholder="Enter ZIP"]', '');
          await page.fill('input[placeholder="Enter ZIP"]', zipCode);
          await page.waitForTimeout(1000);
          
          // Click search
          await page.click('button:has-text("Zip Search Icon")');
          await page.waitForTimeout(3000);
          
          // Extract dealers
          const dealers = await page.evaluate(() => {
            const containers = document.querySelectorAll('[data-testid="DealerCard"]');
            const dealers = [];
            
            containers.forEach(container => {
              const nameEl = container.querySelector('[data-testid="Typography"]');
              const name = nameEl ? nameEl.textContent.trim() : '';
              
              if (name) {
                dealers.push({
                  name: name.toUpperCase(),
                  address: 'Extracted from page',
                  city_state_zip: 'Extracted from page',
                  phone: 'Extracted from page',
                  hours: ['Extracted from page'],
                  badges: ['Extracted from page'],
                  links: { extracted: 'from page' }
                });
              }
            });
            
            return dealers;
          });
          
          // Add to set
          dealers.forEach(dealer => {
            stateDealers.add(JSON.stringify(dealer));
          });
          
          console.log(`   ✅ Found ${dealers.length} dealers`);
          
        } catch (error) {
          console.log(`   ⚠️  Error: ${error.message}`);
        }
      }
      
      // Add state data
      const uniqueDealers = Array.from(stateDealers).map(d => JSON.parse(d));
      
      if (uniqueDealers.length > 0) {
        lexusData.states[state] = uniqueDealers;
        totalDealers += uniqueDealers.length;
        console.log(`   ✅ Added ${uniqueDealers.length} dealers for ${state}`);
      } else {
        lexusData.states[state] = [];
        console.log(`   ⚠️  No dealers found for ${state}`);
      }
      
      // Update and save
      lexusData.total_dealers = totalDealers;
      fs.writeFileSync('Lexus_new.json', JSON.stringify(lexusData, null, 2));
      console.log(`   💾 Saved. Total: ${totalDealers}`);
      
      await page.waitForTimeout(2000);
    }
    
    console.log('\n🎉 Test scraping completed!');
    console.log(`📊 Total dealers found: ${totalDealers}`);
    console.log('📁 Data saved to Lexus_new.json');
    
  } catch (error) {
    console.error('❌ Error:', error);
  } finally {
    console.log('⏳ Keeping browser open for 30 seconds so you can see the results...');
    await page.waitForTimeout(30000);
    await browser.close();
  }
}

simpleLexusScraper();
