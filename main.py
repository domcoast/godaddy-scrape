import os
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
    try:
        # Setup Chrome paths
        chrome_bin, chromedriver_path = setup_chrome_for_render()
        
        # Configure driver with Render-friendly options
        driver = Driver(
            uc=True, 
            headless=True,
            # Additional options for cloud deployment
            browser="chrome",
            # Disable GPU and sandbox for cloud environments
            chromium_arg="--no-sandbox,--disable-dev-shm-usage,--disable-gpu,--remote-debugging-port=9222"
        )
        
        url = "https://auctions.godaddy.com/beta/findApiProxy/v4/aftermarket/find/auction/recommend?endTimeAfter=2025-06-16T06%3A59%3A09.972Z&experimentInfo=aftermarket-semantic-search-202502%3AB&paginationSize=1&paginationStart=0&query=bermudamasterworks.org&useExtRanker=true&useSemanticSearch=true"
        
        print("🚀 Opening URL...")
        # Open page with UC reconnect trick
        driver.uc_open_with_reconnect(url, reconnect_time=4)
        
        # Take screenshot
        driver.save_screenshot("screenshot.png")
        print("✅ Screenshot saved as screenshot.png")
        
        # Optional: Get page source or other data
        page_title = driver.get_title()
        print(f"📄 Page title: {page_title}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()
            print("🔒 Driver closed")

if __name__ == "__main__":
    main()
