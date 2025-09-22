const { chromium } = require('playwright');
const fs = require('fs');

async function scrapeByState() {
  console.log('🚀 Scraping Lexus dealers by STATE dropdown...');
  
  const browser = await chromium.launch({ 
    headless: false, 
    slowMo: 2000,
    args: ['--start-maximized']
  });
  
  const page = await browser.newPage();
  
  try {
    // Navigate to the page
    await page.goto('https://www.lexus.com/dealers');
    await page.waitForTimeout(5000);
    
    // Create fresh data
    const lexusData = {
      brand: "Lexus",
      scraped_date: new Date().toISOString(),
      total_dealers: 0,
      states: {}
    };
    
    // All 50 states
    const allStates = [
      'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia',
      'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland',
      'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey',
      'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina',
      'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
    ];
    
    let totalDealers = 0;
    
    for (let i = 0; i < allStates.length; i++) {
      const state = allStates[i];
      console.log(`\n🌎 Processing ${state} (${i + 1}/${allStates.length})...`);
      
      try {
        // Click on the state dropdown
        console.log('  Clicking state dropdown...');
        await page.click('[role="combobox"]');
        await page.waitForTimeout(2000);
        
        // Select the state
        console.log(`  Selecting ${state}...`);
        await page.click(`[role="option"]:has-text("${state}")`);
        await page.waitForTimeout(3000);
        
        // Extract dealers
        console.log('  Extracting dealers...');
        const dealers = await page.evaluate(() => {
          const containers = document.querySelectorAll('[data-testid="DealerCard"]');
          const dealers = [];
          
          containers.forEach(container => {
            const nameEl = container.querySelector('[data-testid="Typography"]');
            const name = nameEl ? nameEl.textContent.trim() : '';
            
            if (name) {
              // Extract address
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
              
              // Extract phone
              const phoneEl = container.querySelector('a[href^="tel:"]');
              const phone = phoneEl ? phoneEl.textContent.trim() : '';
              
              // Extract hours
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
              
              // Extract badges
              const badges = [];
              const badgeEls = container.querySelectorAll('img[alt*="Dealer"], img[alt*="Elite"], img[alt*="Monogram"], img[alt*="Certified"]');
              badgeEls.forEach(badge => {
                const altText = badge.getAttribute('alt');
                if (altText && !altText.includes('Tooltip') && !altText.includes('Icon')) {
                  badges.push(altText);
                }
              });
              
              // Extract links
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
        
        // Add state data
        if (dealers.length > 0) {
          lexusData.states[state] = dealers;
          totalDealers += dealers.length;
          console.log(`  ✅ Found ${dealers.length} dealers for ${state}`);
          
          // Show dealer names
          dealers.forEach((dealer, index) => {
            console.log(`    ${index + 1}. ${dealer.name}`);
          });
        } else {
          lexusData.states[state] = [];
          console.log(`  ⚠️ No dealers found for ${state}`);
        }
        
        // Update and save
        lexusData.total_dealers = totalDealers;
        fs.writeFileSync('Lexus_by_state.json', JSON.stringify(lexusData, null, 2));
        console.log(`  💾 Saved. Total dealers: ${totalDealers}`);
        
        // Wait before next state
        await page.waitForTimeout(2000);
        
      } catch (error) {
        console.log(`  ❌ Error processing ${state}: ${error.message}`);
      }
    }
    
    console.log('\n🎉 State-by-state scraping completed!');
    console.log(`📊 Final total: ${totalDealers} Lexus dealers across all 50 states`);
    console.log('📁 Data saved to Lexus_by_state.json');
    
  } catch (error) {
    console.error('❌ Error:', error);
  } finally {
    console.log('⏳ Keeping browser open for 60 seconds...');
    await page.waitForTimeout(60000);
    await browser.close();
  }
}

scrapeByState();
