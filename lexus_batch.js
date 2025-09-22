const { chromium } = require('playwright');
const fs = require('fs');

async function batchLexusScraper() {
  console.log('🚀 Starting Batch Lexus Scraper...');
  
  const browser = await chromium.launch({ 
    headless: false, 
    slowMo: 1000,
    args: ['--start-maximized']
  });
  
  const page = await browser.newPage();
  
  try {
    // Read existing data if it exists
    let lexusData;
    try {
      lexusData = JSON.parse(fs.readFileSync('Lexus_complete.json', 'utf8'));
      console.log(`📊 Starting with existing data: ${lexusData.total_dealers} dealers`);
    } catch (error) {
      lexusData = {
        brand: "Lexus",
        scraped_date: new Date().toISOString(),
        total_dealers: 0,
        states: {}
      };
    }
    
    // States to process (starting from Alaska since Alabama is done)
    const statesToProcess = {
      'Alaska': ['99501', '99701', '99801'],
      'Arizona': ['85001', '85701', '86301'],
      'Arkansas': ['72201', '72701', '72901'],
      'California': ['90210', '94101', '90001'],
      'Colorado': ['80201', '80501', '80901'],
      'Connecticut': ['06101', '06401', '06701'],
      'Delaware': ['19801', '19901', '19701'],
      'Florida': ['33101', '33601', '32201'],
      'Georgia': ['30301', '31401', '31901'],
      'Hawaii': ['96801', '96701', '96720'],
      'Idaho': ['83701', '83801', '83201'],
      'Illinois': ['60601', '61101', '61601'],
      'Indiana': ['46201', '46601', '46801'],
      'Iowa': ['50301', '51101', '51501'],
      'Kansas': ['66101', '66601', '67201'],
      'Kentucky': ['40201', '40501', '42101'],
      'Louisiana': ['70112', '70801', '71101'],
      'Maine': ['04101', '04401', '04038'],
      'Maryland': ['21201', '21401', '20740'],
      'Massachusetts': ['02101', '01601', '01060'],
      'Michigan': ['48201', '49501', '48801'],
      'Minnesota': ['55401', '55901', '56301'],
      'Mississippi': ['39201', '39501', '39701'],
      'Missouri': ['63101', '64101', '65801'],
      'Montana': ['59101', '59701', '59801'],
      'Nebraska': ['68101', '68501', '68801'],
      'Nevada': ['89101', '89501', '89001'],
      'New Hampshire': ['03101', '03801', '03201'],
      'New Jersey': ['07001', '07101', '08001'],
      'New Mexico': ['87101', '87501', '88001'],
      'New York': ['10001', '12201', '14201'],
      'North Carolina': ['27601', '28201', '28801'],
      'North Dakota': ['58101', '58501', '58801'],
      'Ohio': ['43201', '44101', '45201'],
      'Oklahoma': ['73101', '74101', '74801'],
      'Oregon': ['97201', '97401', '97701'],
      'Pennsylvania': ['19101', '15201', '17101'],
      'Rhode Island': ['02901', '02801', '02920'],
      'South Carolina': ['29201', '29401', '29601'],
      'South Dakota': ['57101', '57501', '57701'],
      'Tennessee': ['37201', '38101', '37901'],
      'Texas': ['75201', '77001', '78701'],
      'Utah': ['84101', '84401', '84601'],
      'Vermont': ['05401', '05601', '05701'],
      'Virginia': ['23201', '23401', '23601'],
      'Washington': ['98101', '98401', '99201'],
      'West Virginia': ['25301', '25701', '26101'],
      'Wisconsin': ['53201', '53701', '54301'],
      'Wyoming': ['82001', '82601', '82801']
    };
    
    let totalDealers = lexusData.total_dealers;
    let processedStates = 0;
    const totalStates = Object.keys(statesToProcess).length;
    
    for (const [state, zipCodes] of Object.entries(statesToProcess)) {
      // Skip if state already processed
      if (lexusData.states[state]) {
        console.log(`⏭️  Skipping ${state} (already processed)`);
        continue;
      }
      
      console.log(`\n🌎 Processing ${state} (${processedStates + 1}/${totalStates})...`);
      
      const stateDealers = new Set();
      
      for (let i = 0; i < zipCodes.length; i++) {
        const zipCode = zipCodes[i];
        console.log(`   📍 Searching ZIP ${zipCode} (${i + 1}/${zipCodes.length})...`);
        
        try {
          // Navigate to the page fresh for each ZIP code search
          await page.goto('https://www.lexus.com/dealers');
          await page.waitForTimeout(3000);
          
          // Wait for ZIP input
          await page.waitForSelector('input[placeholder="Enter ZIP"]', { timeout: 10000 });
          
          // Clear and enter ZIP code
          await page.fill('input[placeholder="Enter ZIP"]', '');
          await page.fill('input[placeholder="Enter ZIP"]', zipCode);
          await page.waitForTimeout(1000);
          
          // Click search button
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
          
          // Add to set
          dealers.forEach(dealer => {
            stateDealers.add(JSON.stringify(dealer));
          });
          
          console.log(`   ✅ Found ${dealers.length} dealers for ZIP ${zipCode}`);
          
        } catch (error) {
          console.log(`   ⚠️  Error searching ZIP ${zipCode}: ${error.message}`);
        }
        
        // Wait between ZIP code searches
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
        console.log(`   ⚠️  No dealers found for ${state}`);
      }
      
      // Update and save
      lexusData.total_dealers = totalDealers;
      lexusData.scraped_date = new Date().toISOString();
      fs.writeFileSync('Lexus_complete.json', JSON.stringify(lexusData, null, 2));
      console.log(`   💾 Saved. Total dealers: ${totalDealers}`);
      
      processedStates++;
      
      // Progress update
      console.log(`   📊 Progress: ${processedStates}/${totalStates} states completed (${Math.round(processedStates/totalStates*100)}%)`);
      
      // Wait before next state
      await page.waitForTimeout(2000);
    }
    
    console.log('\n🎉 Batch scraping completed!');
    console.log(`📊 Final total: ${totalDealers} Lexus dealers`);
    console.log('📁 Data saved to Lexus_complete.json');
    
  } catch (error) {
    console.error('❌ Error:', error);
  } finally {
    console.log('⏳ Keeping browser open for 30 seconds...');
    await page.waitForTimeout(30000);
    await browser.close();
  }
}

batchLexusScraper();
