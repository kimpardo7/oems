const { chromium } = require('playwright');
const fs = require('fs');

async function finalLexusScraper() {
  console.log('🚀 Starting Final Lexus Scraper...');
  
  const browser = await chromium.launch({ 
    headless: false, 
    slowMo: 2000,
    args: ['--start-maximized']
  });
  
  const page = await browser.newPage();
  
  try {
    // Create fresh data structure
    const lexusData = {
      brand: "Lexus",
      scraped_date: new Date().toISOString(),
      total_dealers: 0,
      states: {}
    };
    
    // States to process (starting from Kentucky)
    const statesToProcess = [
      'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 
      'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana',
      'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico',
      'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma',
      'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota',
      'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia',
      'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
    ];
    
    // ZIP codes for each state
    const stateZipCodes = {
      'Kentucky': ['40202', '40502', '42101'],
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
    
    let totalDealers = 0;
    
    for (const state of statesToProcess) {
      console.log(`\n🌎 Processing ${state}...`);
      
      // Navigate to the page fresh for each state
      console.log('   🌐 Navigating to Lexus dealer page...');
      await page.goto('https://www.lexus.com/dealers');
      await page.waitForTimeout(3000);
      
      // Wait for ZIP input
      await page.waitForSelector('input[placeholder="Enter ZIP"]', { timeout: 10000 });
      console.log('   ✅ Found ZIP input field');
      
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
                // Extract address
                const addressEls = container.querySelectorAll('div');
                let address = '';
                let cityStateZip = '';
                
                for (let el of addressEls) {
                  const text = el.textContent.trim();
                  if (text && text.includes(',') && text.length > 5 && text.length < 50) {
                    cityStateZip = text;
                  } else if (text && !text.includes('Contact') && !text.includes('Hours') && 
                           !text.includes('Mon') && !text.includes('Tue') && text.length > 5 && text.length < 50) {
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
      fs.writeFileSync('Lexus_final.json', JSON.stringify(lexusData, null, 2));
      console.log(`   💾 Saved. Total dealers: ${totalDealers}`);
      
      // Wait before next state
      await page.waitForTimeout(2000);
    }
    
    console.log('\n🎉 Scraping completed!');
    console.log(`📊 Final total: ${totalDealers} dealers`);
    console.log('📁 Data saved to Lexus_final.json');
    
  } catch (error) {
    console.error('❌ Error:', error);
  } finally {
    console.log('⏳ Keeping browser open for 30 seconds...');
    await page.waitForTimeout(30000);
    await browser.close();
  }
}

finalLexusScraper();
