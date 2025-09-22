const { chromium } = require('playwright');

async function simpleLexus() {
  console.log('Starting Lexus scraper...');
  
  const browser = await chromium.launch({ 
    headless: false, 
    slowMo: 2000,
    args: ['--start-maximized']
  });
  
  const page = await browser.newPage();
  
  try {
    console.log('Navigating to Lexus page...');
    await page.goto('https://www.lexus.com/dealers');
    await page.waitForTimeout(5000);
    
    console.log('Looking for ZIP input...');
    await page.waitForSelector('input[placeholder="Enter ZIP"]', { timeout: 10000 });
    
    console.log('Entering ZIP code 40201 (Kentucky)...');
    await page.fill('input[placeholder="Enter ZIP"]', '40201');
    await page.waitForTimeout(1000);
    
    console.log('Clicking search...');
    const searchButton = await page.$('button:has-text("Zip Search Icon")');
    if (searchButton) {
      await searchButton.click();
    } else {
      await page.press('input[placeholder="Enter ZIP"]', 'Enter');
    }
    
    await page.waitForTimeout(5000);
    
    console.log('Extracting dealers...');
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
    
    console.log(`Found ${dealers.length} dealers:`);
    dealers.forEach((dealer, index) => {
      console.log(`${index + 1}. ${dealer.name}`);
    });
    
    console.log('Keeping browser open for 60 seconds...');
    await page.waitForTimeout(60000);
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
}

simpleLexus();