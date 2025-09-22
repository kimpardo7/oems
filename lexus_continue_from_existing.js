const { chromium } = require('playwright');
const fs = require('fs');

async function continueFromExisting() {
  console.log('🚀 Continuing Lexus Scraping from Existing Data...');
  
  const browser = await chromium.launch({ 
    headless: false, 
    slowMo: 1000,
    args: ['--start-maximized']
  });
  
  const page = await browser.newPage();
  
  try {
    // Read the existing comprehensive data
    const lexusData = JSON.parse(fs.readFileSync('Lexus.json', 'utf8'));
    console.log(`📊 Starting with existing data: ${lexusData.total_dealers} dealers`);
    console.log(`📊 States already completed: ${Object.keys(lexusData.states).length}`);
    
    // States to continue from (Kentucky onwards)
    const remainingStates = {
      'Kentucky': ['40201', '40501', '42101', '42401', '42701'],
      'Louisiana': ['70112', '70801', '71101', '71401', '70501'],
      'Maine': ['04101', '04401', '04038', '04901', '04240'],
      'Maryland': ['21201', '21401', '20740', '21701', '21044'],
      'Massachusetts': ['02101', '01601', '01060', '01801', '02720'],
      'Michigan': ['48201', '49501', '48801', '48901', '49001'],
      'Minnesota': ['55401', '55901', '56301', '56501', '56701'],
      'Mississippi': ['39201', '39501', '39701', '38801', '38601'],
      'Missouri': ['63101', '64101', '65801', '65101', '65401'],
      'Montana': ['59101', '59701', '59801', '59901', '59401'],
      'Nebraska': ['68101', '68501', '68801', '69101', '69301'],
      'Nevada': ['89101', '89501', '89001', '89401', '89701'],
      'New Hampshire': ['03101', '03801', '03201', '03060', '03431'],
      'New Jersey': ['07001', '07101', '08001', '08501', '08701'],
      'New Mexico': ['87101', '87501', '88001', '88201', '88401'],
      'New York': ['10001', '12201', '14201', '14601', '13201'],
      'North Carolina': ['27601', '28201', '28801', '27401', '27801'],
      'North Dakota': ['58101', '58501', '58801', '58701', '58301'],
      'Ohio': ['43201', '44101', '45201', '45401', '45801'],
      'Oklahoma': ['73101', '74101', '74801', '73501', '73001'],
      'Oregon': ['97201', '97401', '97701', '97801', '97001'],
      'Pennsylvania': ['19101', '15201', '17101', '18101', '18501'],
      'Rhode Island': ['02901', '02801', '02920', '02840', '02860'],
      'South Carolina': ['29201', '29401', '29601', '29801', '29001'],
      'South Dakota': ['57101', '57501', '57701', '57401', '57301'],
      'Tennessee': ['37201', '38101', '37901', '37401', '37001'],
      'Texas': ['75201', '77001', '78701', '76101', '79901'],
      'Utah': ['84101', '84401', '84601', '84001', '84501'],
      'Vermont': ['05401', '05601', '05701', '05001', '05301'],
      'Virginia': ['23201', '23401', '23601', '23801', '24001'],
      'Washington': ['98101', '98401', '99201', '99301', '98501'],
      'West Virginia': ['25301', '25701', '26101', '26501', '26701'],
      'Wisconsin': ['53201', '53701', '54301', '54601', '54901'],
      'Wyoming': ['82001', '82601', '82801', '82901', '83101']
    };
    
    let totalDealers = lexusData.total_dealers;
    let processedStates = 0;
    const totalRemainingStates = Object.keys(remainingStates).length;
    
    console.log(`🎯 Processing ${totalRemainingStates} remaining states...`);
    
    for (const [state, zipCodes] of Object.entries(remainingStates)) {
      console.log(`\n🌎 Processing ${state} (${processedStates + 1}/${totalRemainingStates})...`);
      console.log(`   📍 Using ${zipCodes.length} ZIP codes: ${zipCodes.join(', ')}`);
      
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
      fs.writeFileSync('Lexus.json', JSON.stringify(lexusData, null, 2));
      console.log(`   💾 Saved to Lexus.json. Total dealers: ${totalDealers}`);
      
      processedStates++;
      
      // Progress update
      console.log(`   📊 Progress: ${processedStates}/${totalRemainingStates} remaining states completed`);
      console.log(`   📊 Overall: ${Object.keys(lexusData.states).length}/50 total states completed`);
      
      // Wait before next state
      await page.waitForTimeout(2000);
    }
    
    console.log('\n🎉 Lexus scraping completed!');
    console.log(`📊 Final total: ${totalDealers} Lexus dealers across all 50 states`);
    console.log('📁 Data saved to Lexus.json');
    
  } catch (error) {
    console.error('❌ Error:', error);
  } finally {
    console.log('⏳ Keeping browser open for 30 seconds...');
    await page.waitForTimeout(30000);
    await browser.close();
  }
}

continueFromExisting();
