const { chromium } = require('playwright');

async function debugLexusPage() {
  console.log('🚀 Starting Lexus page debug...');
  
  const browser = await chromium.launch({ 
    headless: false, 
    slowMo: 2000,
    args: ['--start-maximized']
  });
  
  const page = await browser.newPage();
  
  try {
    console.log('🌐 Navigating to Lexus dealer page...');
    await page.goto('https://www.lexus.com/dealers');
    
    console.log('⏳ Waiting 10 seconds for page to fully load...');
    await page.waitForTimeout(10000);
    
    console.log('📄 Page loaded! You should see the Lexus dealer page now.');
    console.log('🔍 Taking a screenshot...');
    
    await page.screenshot({ path: 'lexus_debug.png', fullPage: true });
    console.log('📸 Screenshot saved as lexus_debug.png');
    
    console.log('🔍 Looking for all possible dropdown selectors...');
    
    // Check for various dropdown selectors
    const selectors = [
      '[role="combobox"]',
      'select',
      '.dropdown',
      '[data-testid*="dropdown"]',
      '[data-testid*="state"]',
      '[aria-haspopup="listbox"]',
      'button[aria-expanded]',
      'input[role="combobox"]'
    ];
    
    for (const selector of selectors) {
      try {
        const elements = await page.$$(selector);
        console.log(`Found ${elements.length} elements with selector: ${selector}`);
        
        if (elements.length > 0) {
          const text = await elements[0].textContent();
          console.log(`  First element text: "${text}"`);
        }
      } catch (error) {
        console.log(`  Error with selector ${selector}: ${error.message}`);
      }
    }
    
    console.log('🔍 Looking for any elements containing "STATE" or "State"...');
    
    const stateElements = await page.$$eval('*', elements => 
      elements
        .filter(el => el.textContent && el.textContent.includes('STATE'))
        .map(el => ({
          tag: el.tagName,
          text: el.textContent.trim(),
          id: el.id,
          className: el.className
        }))
    );
    
    console.log(`Found ${stateElements.length} elements containing "STATE":`);
    stateElements.forEach((el, index) => {
      console.log(`  ${index + 1}. <${el.tag}> id="${el.id}" class="${el.className}"`);
      console.log(`     Text: "${el.text}"`);
    });
    
    console.log('🎯 Looking for clickable elements...');
    
    const clickableElements = await page.$$eval('button, a, [role="button"], [onclick]', elements => 
      elements
        .filter(el => el.textContent && el.textContent.includes('STATE'))
        .map(el => ({
          tag: el.tagName,
          text: el.textContent.trim(),
          id: el.id,
          className: el.className,
          role: el.getAttribute('role')
        }))
    );
    
    console.log(`Found ${clickableElements.length} clickable elements containing "STATE":`);
    clickableElements.forEach((el, index) => {
      console.log(`  ${index + 1}. <${el.tag}> role="${el.role}" id="${el.id}" class="${el.className}"`);
      console.log(`     Text: "${el.text}"`);
    });
    
    console.log('⏳ Keeping browser open for 30 seconds so you can see the page...');
    console.log('👀 Look at the browser window to see what\'s on the page!');
    
    await page.waitForTimeout(30000);
    
  } catch (error) {
    console.error('❌ Error during debugging:', error);
  } finally {
    console.log('🔚 Closing browser...');
    await browser.close();
  }
}

debugLexusPage();
