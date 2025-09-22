const { chromium } = require('playwright');
const fs = require('fs');

async function diverseLexusScraper() {
  console.log('🚀 Starting Diverse ZIP Code Lexus Scraper...');
  
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
    
    // States with diverse ZIP codes from different regions
    const diverseStates = {
      'Alaska': ['99501', '99701', '99801', '99601', '99901'],
      'Arizona': ['85001', '85701', '86301', '86401', '86501'],
      'Arkansas': ['72201', '72701', '72901', '73001', '73101'],
      'California': ['90210', '94101', '90001', '95801', '92101', '92601', '93001', '95101'],
      'Colorado': ['80201', '80501', '80901', '81001', '81501'],
      'Connecticut': ['06101', '06401', '06701', '06801', '06901'],
      'Delaware': ['19801', '19901', '19701', '19601', '19501'],
      'Florida': ['33101', '33601', '32201', '32801', '33401', '33901', '34201', '34601'],
      'Georgia': ['30301', '31401', '31901', '30001', '30101', '30201', '30501'],
      'Hawaii': ['96801', '96701', '96720', '96734', '96740'],
      'Idaho': ['83701', '83801', '83201', '83301', '83401'],
      'Illinois': ['60601', '61101', '61601', '61801', '62201', '62701', '62901'],
      'Indiana': ['46201', '46601', '46801', '47201', '47401', '47701', '47901'],
      'Iowa': ['50301', '51101', '51501', '52001', '52401', '52701', '52801'],
      'Kansas': ['66101', '66601', '67201', '67501', '67801', '67901', '68001'],
      'Kentucky': ['40201', '40501', '42101', '42401', '42701', '43001', '43201'],
      'Louisiana': ['70112', '70801', '71101', '71401', '70501', '70601', '70701'],
      'Maine': ['04101', '04401', '04038', '04901', '04240', '04301', '04401'],
      'Maryland': ['21201', '21401', '20740', '21701', '21044', '20801', '20901'],
      'Massachusetts': ['02101', '01601', '01060', '01801', '02720', '02301', '02401'],
      'Michigan': ['48201', '49501', '48801', '48901', '49001', '49201', '49401'],
      'Minnesota': ['55401', '55901', '56301', '56501', '56701', '57001', '57101'],
      'Mississippi': ['39201', '39501', '39701', '38801', '38601', '38701', '38901'],
      'Missouri': ['63101', '64101', '65801', '65101', '65401', '65701', '65801'],
      'Montana': ['59101', '59701', '59801', '59901', '59401', '59501', '59601'],
      'Nebraska': ['68101', '68501', '68801', '69101', '69301', '69401', '69501'],
      'Nevada': ['89101', '89501', '89001', '89401', '89701', '89801', '89001'],
      'New Hampshire': ['03101', '03801', '03201', '03060', '03431', '03031', '03101'],
      'New Jersey': ['07001', '07101', '08001', '08501', '08701', '08801', '08901'],
      'New Mexico': ['87101', '87501', '88001', '88201', '88401', '88501', '88601'],
      'New York': ['10001', '12201', '14201', '14601', '13201', '13501', '13601'],
      'North Carolina': ['27601', '28201', '28801', '27401', '27801', '28001', '28101'],
      'North Dakota': ['58101', '58501', '58801', '58701', '58301', '58401', '58501'],
      'Ohio': ['43201', '44101', '45201', '45401', '45801', '46001', '46201'],
      'Oklahoma': ['73101', '74101', '74801', '73501', '73001', '73101', '73201'],
      'Oregon': ['97201', '97401', '97701', '97801', '97001', '97101', '97201'],
      'Pennsylvania': ['19101', '15201', '17101', '18101', '18501', '19001', '19101'],
      'Rhode Island': ['02901', '02801', '02920', '02840', '02860', '02901', '02801'],
      'South Carolina': ['29201', '29401', '29601', '29801', '29001', '29101', '29201'],
      'South Dakota': ['57101', '57501', '57701', '57401', '57301', '57201', '57101'],
      'Tennessee': ['37201', '38101', '37901', '37401', '37001', '37101', '37201'],
      'Texas': ['75201', '77001', '78701', '76101', '79901', '75001', '75101'],
      'Utah': ['84101', '84401', '84601', '84001', '84501', '84601', '84701'],
      'Vermont': ['05401', '05601', '05701', '05001', '05301', '05401', '05501'],
      'Virginia': ['23201', '23401', '23601', '23801', '24001', '24101', '24201'],
      'Washington': ['98101', '98401', '99201', '99301', '98501', '98601', '98701'],
      'West Virginia': ['25301', '25701', '26101', '26501', '26701', '26801', '26901'],
      'Wisconsin': ['53201', '53701', '54301', '54601', '54901', '55001', '55101'],
      'Wyoming': ['82001', '82601', '82801', '82901', '83101', '83201', '83301']
    };
    
    let totalDealers = lexusData.total_dealers;
    let processedStates = 0;
    const totalStates = Object.keys(diverseStates).length;
    
    for (const [state, zipCodes] of Object.entries(diverseStates)) {
      // Skip if state already processed
      if (lexusData.states[state]) {
        console.log(`⏭️  Skipping ${state} (already processed)`);
        continue;
      }
      
      console.log(`\n🌎 Processing ${state} (${processedStates + 1}/${totalStates})...`);
      console.log(`   📍 Using ${zipCodes.length} diverse ZIP codes: ${zipCodes.join(', ')}`);
      
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
    
    console.log('\n🎉 Diverse scraping completed!');
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

diverseLexusScraper();
