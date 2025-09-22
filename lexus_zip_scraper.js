const { chromium } = require('playwright');
const fs = require('fs');

async function scrapeLexusByZip() {
  console.log('🚀 Starting Lexus ZIP Code Scraper...');
  
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
    console.log('🔍 Looking for ZIP code input field...');
    
    // Wait for the ZIP input field
    await page.waitForSelector('input[placeholder="Enter ZIP"]', { timeout: 10000 });
    console.log('✅ Found ZIP input field!');
    
    // Read existing Lexus.json
    let lexusData;
    try {
      lexusData = JSON.parse(fs.readFileSync('Lexus.json', 'utf8'));
    } catch (error) {
      lexusData = {
        brand: "Lexus",
        scraped_date: new Date().toISOString(),
        total_dealers: 0,
        states: {}
      };
    }
    
    // ZIP codes for major cities in each state (starting with Kentucky)
    const stateZipCodes = {
      'Kentucky': ['40202', '40502', '42101', '42431', '42701'],
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
    
    let totalDealers = 0;
    
    for (const [state, zipCodes] of Object.entries(stateZipCodes)) {
      console.log(`\n🌎 Processing ${state}...`);
      
      const stateDealers = new Set(); // Use Set to avoid duplicates
      
      for (const zipCode of zipCodes) {
        console.log(`   📍 Searching ZIP code ${zipCode}...`);
        
        try {
          // Clear and enter ZIP code
          await page.fill('input[placeholder="Enter ZIP"]', '');
          await page.fill('input[placeholder="Enter ZIP"]', zipCode);
          await page.waitForTimeout(1000);
          
          // Click search button
          await page.click('button:has-text("Zip Search Icon")');
          await page.waitForTimeout(3000);
          
          // Extract dealer data
          const dealers = await page.evaluate(() => {
            const dealerContainers = document.querySelectorAll('[data-testid="DealerCard"]');
            const dealers = [];
            
            dealerContainers.forEach(container => {
              try {
                const nameElement = container.querySelector('[data-testid="Typography"]');
                const name = nameElement ? nameElement.textContent.trim() : '';
                
                if (name) {
                  // Extract address
                  const addressElements = container.querySelectorAll('div');
                  let address = '';
                  let cityStateZip = '';
                  
                  for (let i = 0; i < addressElements.length; i++) {
                    const text = addressElements[i].textContent.trim();
                    if (text && !text.includes('Contact:') && !text.includes('Hours:') && 
                        !text.includes('SE HABLA') && !text.includes('Mon') && 
                        !text.includes('Tue') && !text.includes('Wed') && 
                        !text.includes('Thu') && !text.includes('Fri') && 
                        !text.includes('Sat') && !text.includes('Sun') &&
                        !text.includes('am') && !text.includes('pm') &&
                        !text.includes('Elite') && !text.includes('Monogram') &&
                        !text.includes('Certified') && !text.includes('Collision') &&
                        !text.includes('DEALER') && !text.includes('SITE') &&
                        !text.includes('SERVICE') && !text.includes('CONTACT') &&
                        text !== name) {
                      if (text.includes(',')) {
                        cityStateZip = text;
                      } else if (text.length > 5) {
                        address = text;
                      }
                    }
                  }
                  
                  // Extract phone
                  const phoneElement = container.querySelector('a[href^="tel:"]');
                  const phone = phoneElement ? phoneElement.textContent.trim() : '';
                  
                  // Extract hours
                  const hours = [];
                  const hoursList = container.querySelector('ul');
                  if (hoursList) {
                    const hoursItems = hoursList.querySelectorAll('li');
                    hoursItems.forEach(item => {
                      const dayElement = item.querySelector('div:first-child');
                      const timeElement = item.querySelector('div:last-child');
                      if (dayElement && timeElement) {
                        hours.push(`${dayElement.textContent.trim()} ${timeElement.textContent.trim()}`);
                      }
                    });
                  }
                  
                  // Extract badges
                  const badges = [];
                  const badgeElements = container.querySelectorAll('img[alt*="Dealer"], img[alt*="Elite"], img[alt*="Monogram"], img[alt*="Certified"]');
                  badgeElements.forEach(badge => {
                    const altText = badge.getAttribute('alt');
                    if (altText && !altText.includes('Tooltip') && !altText.includes('Icon')) {
                      badges.push(altText);
                    }
                  });
                  
                  // Extract links
                  const links = {};
                  const linkElements = container.querySelectorAll('a');
                  linkElements.forEach(link => {
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
              } catch (error) {
                console.error('Error extracting dealer data:', error);
              }
            });
            
            return dealers;
          });
          
          // Add unique dealers to state set
          dealers.forEach(dealer => {
            stateDealers.add(JSON.stringify(dealer));
          });
          
          console.log(`   ✅ Found ${dealers.length} dealers for ZIP ${zipCode}`);
          
        } catch (error) {
          console.log(`   ⚠️  Error searching ZIP ${zipCode}: ${error.message}`);
        }
      }
      
      // Convert Set back to array
      const uniqueDealers = Array.from(stateDealers).map(dealer => JSON.parse(dealer));
      
      if (uniqueDealers.length > 0) {
        lexusData.states[state] = uniqueDealers;
        totalDealers += uniqueDealers.length;
        console.log(`   ✅ Added ${uniqueDealers.length} unique dealers for ${state}`);
      } else {
        lexusData.states[state] = [];
        console.log(`   ⚠️  No dealers found for ${state}`);
      }
      
      // Update total and save
      lexusData.total_dealers = totalDealers;
      fs.writeFileSync('Lexus.json', JSON.stringify(lexusData, null, 2));
      console.log(`   💾 Saved data. Total dealers: ${totalDealers}`);
      
      // Wait before next state
      await page.waitForTimeout(2000);
    }
    
    console.log('\n🎉 Scraping completed!');
    console.log(`📊 Total dealers found: ${totalDealers}`);
    
  } catch (error) {
    console.error('❌ Error during scraping:', error);
  } finally {
    console.log('🔚 Closing browser...');
    await browser.close();
  }
}

scrapeLexusByZip();
