const { chromium } = require('playwright');
const fs = require('fs');

async function searchDifferentZips() {
  console.log('🚀 Searching Different ZIP Codes...');
  
  const browser = await chromium.launch({ 
    headless: false, 
    slowMo: 2000,
    args: ['--start-maximized']
  });
  
  const page = await browser.newPage();
  
  try {
    // Different ZIP codes from different states
    const zipCodes = [
      { zip: '40201', state: 'Kentucky', city: 'Louisville' },
      { zip: '40501', state: 'Kentucky', city: 'Lexington' },
      { zip: '42101', state: 'Kentucky', city: 'Bowling Green' },
      { zip: '70112', state: 'Louisiana', city: 'New Orleans' },
      { zip: '70801', state: 'Louisiana', city: 'Baton Rouge' },
      { zip: '71101', state: 'Louisiana', city: 'Shreveport' },
      { zip: '04101', state: 'Maine', city: 'Portland' },
      { zip: '04401', state: 'Maine', city: 'Bangor' },
      { zip: '04038', state: 'Maine', city: 'Biddeford' },
      { zip: '21201', state: 'Maryland', city: 'Baltimore' }
    ];
    
    const allDealers = [];
    
    for (let i = 0; i < zipCodes.length; i++) {
      const { zip, state, city } = zipCodes[i];
      console.log(`\n📍 Searching ZIP ${zip} (${city}, ${state}) - ${i + 1}/${zipCodes.length}...`);
      
      try {
        // Navigate to page fresh each time
        await page.goto('https://www.lexus.com/dealers');
        await page.waitForTimeout(3000);
        
        // Wait for ZIP input
        await page.waitForSelector('input[placeholder="Enter ZIP"]', { timeout: 10000 });
        
        // Clear and enter ZIP code
        await page.fill('input[placeholder="Enter ZIP"]', '');
        await page.fill('input[placeholder="Enter ZIP"]', zip);
        await page.waitForTimeout(1000);
        
        // Click search
        const searchButton = await page.$('button:has-text("Zip Search Icon")');
        if (searchButton) {
          await searchButton.click();
        } else {
          await page.press('input[placeholder="Enter ZIP"]', 'Enter');
        }
        
        await page.waitForTimeout(3000);
        
        // Extract dealers
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
                links: links,
                search_zip: zip,
                search_city: city,
                search_state: state
              });
            }
          });
          
          return dealers;
        });
        
        allDealers.push(...dealers);
        console.log(`   ✅ Found ${dealers.length} dealers for ZIP ${zip} (${city}, ${state})`);
        
        // Show dealer names
        dealers.forEach((dealer, index) => {
          console.log(`      ${index + 1}. ${dealer.name}`);
        });
        
      } catch (error) {
        console.log(`   ⚠️ Error searching ZIP ${zip}: ${error.message}`);
      }
      
      // Wait between searches
      await page.waitForTimeout(2000);
    }
    
    // Save all dealers
    const lexusData = {
      brand: "Lexus",
      scraped_date: new Date().toISOString(),
      total_dealers: allDealers.length,
      dealers: allDealers
    };
    
    fs.writeFileSync('Lexus_different_zips.json', JSON.stringify(lexusData, null, 2));
    
    console.log('\n🎉 Scraping completed!');
    console.log(`📊 Total dealers found: ${allDealers.length}`);
    console.log('📁 Data saved to Lexus_different_zips.json');
    
    // Show summary by state
    const byState = {};
    allDealers.forEach(dealer => {
      const state = dealer.search_state;
      if (!byState[state]) byState[state] = [];
      byState[state].push(dealer);
    });
    
    console.log('\n📊 Summary by state:');
    Object.entries(byState).forEach(([state, dealers]) => {
      console.log(`   ${state}: ${dealers.length} dealers`);
    });
    
  } catch (error) {
    console.error('❌ Error:', error);
  } finally {
    console.log('⏳ Keeping browser open for 60 seconds...');
    await page.waitForTimeout(60000);
    await browser.close();
  }
}

searchDifferentZips();
