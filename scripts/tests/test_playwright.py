import asyncio
from playwright.async_api import async_playwright

async def test_browser():
    print("Testing Playwright browser launch...")
    
    try:
        async with async_playwright() as p:
            print("✅ Playwright context created")
            
            # Try launching browser
            browser = await p.chromium.launch(headless=False)
            print("✅ Browser launched")
            
            context = await browser.new_context()
            print("✅ Browser context created")
            
            page = await context.new_page()
            print("✅ Page created")
            
            # Navigate to a simple page
            await page.goto('https://www.google.com')
            print("✅ Navigated to Google")
            
            await page.wait_for_timeout(3000)
            print("✅ Waited 3 seconds")
            
            await browser.close()
            print("✅ Browser closed successfully")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_browser())
