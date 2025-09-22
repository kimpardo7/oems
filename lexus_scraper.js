const { chromium } = require('playwright');
const fs = require('fs');

async function scrapeLexusDealers() {
  const browser = await chromium.launch({ 
    headless: false, 
    slowMo: 2000,
    args: ['--start-maximized', '--window-size=1400,900']
  });
  const page = await browser.newPage();
  
  // Set viewport to make sure it's visible
  await page.setViewportSize({ width: 1400, height: 900 });
  
  try {
    // Navigate to Lexus dealer page
    await page.goto('https://www.lexus.com/dealers');
    await page.waitForLoadState('networkidle');
    
    // Read existing Lexus.json
    const lexusData = JSON.parse(fs.readFileSync('Lexus.json', 'utf8'));
    
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
    
    for (const state of statesToProcess) {
      console.log(`\n🌎 Processing ${state}...`);
      
      // Click on STATE dropdown
      console.log(`   📍 Clicking STATE dropdown...`);
      await page.click('[role="combobox"]');
      await page.waitForTimeout(3000); // Longer delay to see the dropdown open
      
      // Select the state
      console.log(`   🎯 Selecting ${state}...`);
      await page.click(`[role="option"]:has-text("${state}")`);
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(3000); // Wait to see the results load
      
      // Extract dealer data
      const dealers = await page.evaluate(() => {
        const dealerContainers = document.querySelectorAll('[data-testid="DealerCard"]');
        const dealers = [];
        
        dealerContainers.forEach(container => {
          try {
            const nameElement = container.querySelector('[data-testid="Typography"]');
            const name = nameElement ? nameElement.textContent.trim() : '';
            
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
            
            const phoneElement = container.querySelector('a[href^="tel:"]');
            const phone = phoneElement ? phoneElement.textContent.trim() : '';
            
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
            
            const badges = [];
            const badgeElements = container.querySelectorAll('img[alt*="Dealer"], img[alt*="Elite"], img[alt*="Monogram"], img[alt*="Certified"]');
            badgeElements.forEach(badge => {
              const altText = badge.getAttribute('alt');
              if (altText && !altText.includes('Tooltip') && !altText.includes('Icon')) {
                badges.push(altText);
              }
            });
            
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
            
            if (name) {
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
      
      // Add dealers to the data
      if (dealers.length > 0) {
        lexusData.states[state] = dealers;
        lexusData.total_dealers += dealers.length;
        console.log(`   ✅ Added ${dealers.length} dealers for ${state}`);
        console.log(`   📊 Total dealers so far: ${lexusData.total_dealers}`);
      } else {
        lexusData.states[state] = [];
        console.log(`   ⚠️  No dealers found for ${state}`);
      }
      
      // Save updated data
      console.log(`   💾 Saving data to Lexus.json...`);
      fs.writeFileSync('Lexus.json', JSON.stringify(lexusData, null, 2));
      
      // Wait a bit before next state
      console.log(`   ⏳ Waiting before next state...`);
      await page.waitForTimeout(5000); // Longer delay to see the results
    }
    
    console.log('Scraping completed!');
    console.log(`Total dealers: ${lexusData.total_dealers}`);
    
  } catch (error) {
    console.error('Error during scraping:', error);
  } finally {
    await browser.close();
  }
}

scrapeLexusDealers();
