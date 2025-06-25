import os
import sys
from seleniumbase import Driver

def setup_chrome_for_render():
    """Configure Chrome for Render's environment"""
    # Render-specific Chrome binary path (if using buildpack)
    chrome_bin = os.environ.get("GOOGLE_CHROME_BIN", "/opt/google/chrome/chrome")
    chromedriver_path = os.environ.get("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")
    
    # Set environment variables for Chrome
    os.environ["CHROME_BIN"] = chrome_bin
    
    return chrome_bin, chromedriver_path

def main():
    driver = None
    try:
        print("🔧 Setting up Chrome...")
        # Setup Chrome paths
        chrome_bin, chromedriver_path = setup_chrome_for_render()
        
        print("🚀 Starting browser...")
        # Configure driver with better stealth options
        driver = Driver(
            uc=True, 
            headless=True,
            browser="chrome",
            # Enhanced stealth options - including user agent in chromium_arg
            chromium_arg="--no-sandbox,--disable-dev-shm-usage,--disable-gpu,--disable-blink-features=AutomationControlled,--disable-extensions,--no-first-run,--disable-default-apps,--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        )
        
        url = "https://auctions.godaddy.com/beta/findApiProxy/v4/aftermarket/find/auction/recommend?endTimeAfter=2025-06-16T06%3A59%3A09.972Z&experimentInfo=aftermarket-semantic-search-202502%3AB&paginationSize=1&paginationStart=0&query=bermudamasterworks.org&useExtRanker=true&useSemanticSearch=true"
        
        print("🚀 Opening URL...")
        
        # Add some stealth measures
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Open page with UC reconnect trick and longer wait
        driver.uc_open_with_reconnect(url, reconnect_time=6)
        
        # Wait a bit more for page to load
        driver.sleep(3)
        
        # Take screenshot
        screenshot_path = "screenshot.png"
        driver.save_screenshot(screenshot_path)
        print("✅ Screenshot saved as screenshot.png")
        
        # Send screenshot to webhook
        try:
            import base64
            import requests
            
            print("📤 Preparing to send screenshot to webhook...")
            
            with open(screenshot_path, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            
            # Prepare webhook payload
            webhook_url = "https://n8n.scrapifyapi.com/webhook/fa92b96f-26c4-43aa-9e9c-acb43c6145ce"
            payload = {
                "screenshot": img_base64,
                "url": url,
                "page_title": driver.get_title(),
                "timestamp": driver.execute_script("return new Date().toISOString()"),
                "status": "success"
            }
            
            print("🚀 Sending to webhook...")
            # Send to webhook
            response = requests.post(webhook_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                print("✅ Screenshot sent to webhook successfully!")
                print(f"Response: {response.text[:200]}...")
            else:
                print(f"❌ Webhook failed with status {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error sending to webhook: {e}")
        
        # Optional: Get page source or other data
        page_title = driver.get_title()
        print(f"📄 Page title: {page_title}")
        
        print("✅ Process completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        if driver:
            print("🔒 Closing driver...")
            driver.quit()
            print("🔒 Driver closed")
        
        print("🏁 Script finished. Exiting...")
        # Force exit to ensure process terminates
        sys.exit(0)

if __name__ == "__main__":
    main()
