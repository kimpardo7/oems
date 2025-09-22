const { chromium } = require('playwright');

async function simpleStateScraper() {
  console.log('Starting Lexus state scraper...');
  
  const browser = await chromium.launch({ 
    headless: false, 
    slowMo: 2000,
    args: ['--start-maximized']
  });
  
  const page = await browser.newPage();
  
  try {
    await page.goto('https://www.lexus.com/dealers');
    await page.waitForTimeout(5000);
    
    const states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California'];
    const allDealers = [];
    
    for (let i = 0; i < states.length; i++) {
      const state = states[i];
      console.log(`\nProcessing ${state} (${i + 1}/${states.length})...`);
      
      try {
        console.log('  Clicking state dropdown...');
        await page.click('[role="combobox"]');
        await page.waitForTimeout(2000);
        
        console.log(`  Selecting ${state}...`);
        await page.click(`[role="option"]:has-text("${state}")`);
        await page.waitForTimeout(3000);
        
        console.log('  Extracting dealers...');
        const dealers = await page.evaluate(() => {
          const containers = document.querySelectorAll('[data-testid="DealerCard"]');
          const dealers = [];
          
          containers.forEach(container => {
            const nameEl = container.querySelector('[data-testid="Typography"]');
            const name = nameEl ? nameEl.textContent.trim() : '';
            
            if (name) {
              dealers.push({
                name: name.toUpperCase()
              });
            }
          });
          
          return dealers;
        });
        
        allDealers.push(...dealers);
        console.log(`  Found ${dealers.length} dealers for ${state}`);
        
        dealers.forEach((dealer, index) => {
          console.log(`    ${index + 1}. ${dealer.name}`);
        });
        
      } catch (error) {
        console.log(`  Error processing ${state}: ${error.message}`);
      }
      
      await page.waitForTimeout(2000);
    }
    
    console.log(`\nTotal dealers found: ${allDealers.length}`);
    
    console.log('Keeping browser open for 60 seconds...');
    await page.waitForTimeout(60000);
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
}

simpleStateScraper();
