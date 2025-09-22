const { chromium } = require('playwright');

async function interactiveLexusScraper() {
  console.log('🚀 Starting Interactive Lexus Scraper...');
  
  const browser = await chromium.launch({ 
    headless: false, 
    slowMo: 2000,
    args: ['--start-maximized']
  });
  
  const page = await browser.newPage();
  
  try {
    console.log('🌐 Navigating to Lexus dealer page...');
    await page.goto('https://www.lexus.com/dealers');
    
    console.log('⏳ Waiting for page to load...');
    await page.waitForTimeout(5000);
    
    console.log('📄 Page loaded! You should see the Lexus dealer page now.');
    console.log('👀 Please look at the browser window and tell me what you see!');
    
    // Take a screenshot
    await page.screenshot({ path: 'lexus_current_page.png', fullPage: true });
    console.log('📸 Screenshot saved as lexus_current_page.png');
    
    console.log('🔍 Looking for any search or filter elements...');
    
    // Look for common search/filter elements
    const searchElements = await page.$$eval('input, button, select, [role="button"], [role="combobox"]', elements => 
      elements
        .filter(el => el.textContent || el.placeholder || el.value)
        .map(el => ({
          tag: el.tagName,
          text: el.textContent?.trim() || '',
          placeholder: el.placeholder || '',
          value: el.value || '',
          id: el.id || '',
          className: el.className || '',
          role: el.getAttribute('role') || ''
        }))
        .filter(el => el.text || el.placeholder || el.value)
    );
    
    console.log(`Found ${searchElements.length} interactive elements:`);
    searchElements.forEach((el, index) => {
      console.log(`  ${index + 1}. <${el.tag}> role="${el.role}" id="${el.id}"`);
      if (el.text) console.log(`     Text: "${el.text}"`);
      if (el.placeholder) console.log(`     Placeholder: "${el.placeholder}"`);
      if (el.value) console.log(`     Value: "${el.value}"`);
      if (el.className) console.log(`     Class: "${el.className}"`);
    });
    
    console.log('🔍 Looking for any elements that might be related to location search...');
    
    const locationElements = await page.$$eval('*', elements => 
      elements
        .filter(el => {
          const text = el.textContent?.toLowerCase() || '';
          return text.includes('state') || text.includes('location') || 
                 text.includes('zip') || text.includes('city') || 
                 text.includes('search') || text.includes('find')
        })
        .map(el => ({
          tag: el.tagName,
          text: el.textContent?.trim() || '',
          id: el.id || '',
          className: el.className || ''
        }))
        .filter(el => el.text.length < 100) // Avoid very long text
    );
    
    console.log(`Found ${locationElements.length} location-related elements:`);
    locationElements.forEach((el, index) => {
      console.log(`  ${index + 1}. <${el.tag}> id="${el.id}" class="${el.className}"`);
      console.log(`     Text: "${el.text}"`);
    });
    
    console.log('⏳ Keeping browser open for 60 seconds...');
    console.log('👀 Please look at the browser window and tell me:');
    console.log('   1. Do you see a search box or dropdown?');
    console.log('   2. What does the page look like?');
    console.log('   3. Are there any buttons or filters visible?');
    
    await page.waitForTimeout(60000);
    
  } catch (error) {
    console.error('❌ Error during interactive scraping:', error);
  } finally {
    console.log('🔚 Closing browser...');
    await browser.close();
  }
}

interactiveLexusScraper();
