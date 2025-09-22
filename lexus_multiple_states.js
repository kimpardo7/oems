const { chromium } = require('playwright');
const fs = require('fs');

async function scrapeMultipleStates() {
  console.log('🚀 Scraping Multiple States with Diverse ZIP Codes...');
  
  const browser = await chromium.launch({ 
    headless: false, 
    slowMo: 1000,
    args: ['--start-maximized']
  });
  
  const page = await browser.newPage();
  
  try {
    // Create fresh data
    const lexusData = {
      brand: "Lexus",
      scraped_date: new Date().toISOString(),
      total_dealers: 0,
      states: {}
    };
    
    // Multiple states with diverse ZIP codes
    const statesToProcess = {
      'Kentucky': ['40201', '40501', '42101'],
      'Louisiana': ['70112', '70801', '71101'],
      'Maine': ['04101', '04401', '04038'],
      'Maryland': ['21201', '21401', '20740'],
      'Massachusetts': ['02101', '01601', '01060'],
      'Michigan': ['48201', '49501', '48801'],
      'Minnesota': ['55401', '55901', '56301'],
      'Mississippi': ['39201', '39501', '39701'],
      'Missouri': ['63101', '64101', '65801'],
      'Montana': ['59101', '59701', '59801']
    };
    
    let totalDealers = 0;
    let processedStates = 0;
    
    for (const [state, zipCodes] of Object.entries(statesToProcess)) {
      console.log(`\n🌎 Processing ${state} (${processedStates + 1}/${Object.keys(statesToProcess).length})...`);
      console.log(`   📍 ZIP codes: ${zipCodes.join(', ')}`);
      
      const stateDealers = new Set();
      
      for (const zipCode of zipCodes) {
        console.log(`   📍 Searching ZIP ${zipCode}...`);
        
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
          
          console.log(`   ✅ Found ${dealers.length} dealers for ZIP ${zipCode}`);
          
        } catch (error) {
          console.log(`   ⚠️ Error searching ZIP ${zipCode}: ${error.message}`);
        }
        
        await page.waitForTimeout(2000);
      }
      
      // Add state data
      const uniqueDealers = Array.from(stateDealers).map(d => JSON.parse(d));
      
      if (uniqueDealers.length > 0) {
        lexusData.states[state] = uniqueDealers;
        totalDealers += uniqueDealers.length;
        console.log(`   ✅ Added ${uniqueDealers.length} unique dealers for ${state}`);
      } else {
        lexusData.states[state] = [];
        console.log(`   ⚠️ No dealers found for ${state}`);
      }
      
      // Save data
      lexusData.total_dealers = totalDealers;
      fs.writeFileSync('Lexus_multiple.json', JSON.stringify(lexusData, null, 2));
      console.log(`   💾 Saved. Total dealers: ${totalDealers}`);
      
      processedStates++;
      console.log(`   📊 Progress: ${processedStates}/${Object.keys(statesToProcess).length} states completed`);
      
      await page.waitForTimeout(2000);
    }
    
    console.log('\n🎉 Multiple states scraping completed!');
    console.log(`📊 Final total: ${totalDealers} Lexus dealers`);
    console.log('📁 Data saved to Lexus_multiple.json');
    
  } catch (error) {
    console.error('❌ Error:', error);
  } finally {
    console.log('⏳ Keeping browser open for 60 seconds...');
    await page.waitForTimeout(60000);
    await browser.close();
  }
}

scrapeMultipleStates();
