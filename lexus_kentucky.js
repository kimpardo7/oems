const { chromium } = require('playwright');
const fs = require('fs');

async function scrapeKentucky() {
  console.log('🚀 Scraping Kentucky Lexus dealers...');
  
  const browser = await chromium.launch({ 
    headless: false, 
    slowMo: 1000,
    args: ['--start-maximized']
  });
  
  const page = await browser.newPage();
  
  try {
    // Read existing data
    const lexusData = JSON.parse(fs.readFileSync('Lexus.json', 'utf8'));
    console.log(`📊 Starting with ${lexusData.total_dealers} dealers`);
    
    // Kentucky ZIP codes
    const kentuckyZips = ['40201', '40501', '42101', '42401', '42701'];
    const stateDealers = new Set();
    
    for (const zipCode of kentuckyZips) {
      console.log(`📍 Searching ZIP ${zipCode}...`);
      
      try {
        await page.goto('https://www.lexus.com/dealers');
        await page.waitForTimeout(3000);
        
        await page.waitForSelector('input[placeholder="Enter ZIP"]', { timeout: 10000 });
        await page.fill('input[placeholder="Enter ZIP"]', '');
        await page.fill('input[placeholder="Enter ZIP"]', zipCode);
        await page.waitForTimeout(1000);
        
        const searchButton = await page.$('button:has-text("Zip Search Icon")');
        if (searchButton) {
          await searchButton.click();
        } else {
          await page.press('input[placeholder="Enter ZIP"]', 'Enter');
        }
        
        await page.waitForTimeout(3000);
        
        const dealers = await page.evaluate(() => {
          const containers = document.querySelectorAll('[data-testid="DealerCard"]');
          const dealers = [];
          
          containers.forEach(container => {
            const nameEl = container.querySelector('[data-testid="Typography"]');
            const name = nameEl ? nameEl.textContent.trim() : '';
            
            if (name) {
              const addressEls = container.querySelectorAll('div');
              let address = '';
              let cityStateZip = '';
              
              for (let el of addressEls) {
                const text = el.textContent.trim();
                if (text && text.includes(',') && text.length > 5 && text.length < 50) {
                  cityStateZip = text;
                } else if (text && !text.includes('Contact') && !text.includes('Hours') && 
                         !text.includes('Mon') && !text.includes('Tue') && 
                         !text.includes('Wed') && !text.includes('Thu') && 
                         !text.includes('Fri') && !text.includes('Sat') && 
                         !text.includes('Sun') && text.length > 5 && text.length < 50) {
                  address = text;
                }
              }
              
              const phoneEl = container.querySelector('a[href^="tel:"]');
              const phone = phoneEl ? phoneEl.textContent.trim() : '';
              
              const hours = [];
              const hoursList = container.querySelector('ul');
              if (hoursList) {
                const hoursItems = hoursList.querySelectorAll('li');
                hoursItems.forEach(item => {
                  const dayEl = item.querySelector('div:first-child');
                  const timeEl = item.querySelector('div:last-child');
                  if (dayEl && timeEl) {
                    hours.push(`${dayEl.textContent.trim()} ${timeEl.textContent.trim()}`);
                  }
                });
              }
              
              const badges = [];
              const badgeEls = container.querySelectorAll('img[alt*="Dealer"], img[alt*="Elite"], img[alt*="Monogram"], img[alt*="Certified"]');
              badgeEls.forEach(badge => {
                const altText = badge.getAttribute('alt');
                if (altText && !altText.includes('Tooltip') && !altText.includes('Icon')) {
                  badges.push(altText);
                }
              });
              
              const links = {};
              const linkEls = container.querySelectorAll('a');
              linkEls.forEach(link => {
                const href = link.getAttribute('href');
                const text = link.textContent.trim();
                
                if (href && text) {
                  if (text.includes('DEALER DETAILS')) {
                    links.dealer_details = href;
                  } else if (text.includes('DEALER SITE')) {
                    links.website = href;
                  } else if (text.includes('SCHEDULE SERVICE')) {
                    links.service = href;
                  } else if (text.includes('CONTACT DEALER')) {
                    links.contact = href;
                  }
                }
              });
              
              dealers.push({
                name: name.toUpperCase(),
                address: address,
                city_state_zip: cityStateZip,
                phone: phone,
                hours: hours,
                badges: badges,
                links: links
              });
            }
          });
          
          return dealers;
        });
        
        dealers.forEach(dealer => {
          stateDealers.add(JSON.stringify(dealer));
        });
        
        console.log(`✅ Found ${dealers.length} dealers for ZIP ${zipCode}`);
        
      } catch (error) {
        console.log(`⚠️ Error searching ZIP ${zipCode}: ${error.message}`);
      }
      
      await page.waitForTimeout(2000);
    }
    
    // Add Kentucky data
    const uniqueDealers = Array.from(stateDealers).map(d => JSON.parse(d));
    
    if (uniqueDealers.length > 0) {
      lexusData.states['Kentucky'] = uniqueDealers;
      lexusData.total_dealers += uniqueDealers.length;
      console.log(`✅ Added ${uniqueDealers.length} dealers for Kentucky`);
    } else {
      lexusData.states['Kentucky'] = [];
      console.log(`⚠️ No dealers found for Kentucky`);
    }
    
    // Save data
    lexusData.scraped_date = new Date().toISOString();
    fs.writeFileSync('Lexus.json', JSON.stringify(lexusData, null, 2));
    console.log(`💾 Saved. Total dealers: ${lexusData.total_dealers}`);
    
  } catch (error) {
    console.error('❌ Error:', error);
  } finally {
    console.log('⏳ Keeping browser open for 30 seconds...');
    await page.waitForTimeout(30000);
    await browser.close();
  }
}

scrapeKentucky();
