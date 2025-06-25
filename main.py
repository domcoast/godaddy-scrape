import os
import base64
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from seleniumbase import Driver

app = FastAPI()


class ScrapeRequest(BaseModel):
    query: str  # domain name to search, e.g., "bermudamasterworks.org"


def setup_chrome():
    chrome_bin = os.environ.get("GOOGLE_CHROME_BIN", "/opt/google/chrome/chrome")
    chromedriver_path = os.environ.get("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")
    os.environ["CHROME_BIN"] = chrome_bin
    return chrome_bin, chromedriver_path


def run_scraper(domain_query: str) -> dict:
    setup_chrome()

    # Proxy setup
    proxy = "core-residential.evomi.com:1000"
    proxy_user = "domaincoas3"
    proxy_pass = "qjQDSiuIKepa9XVjiSzK"
    proxy_auth = f"{proxy_user}:{proxy_pass}@{proxy}"

    driver = None
    try:
        url = (
            "https://auctions.godaddy.com/beta/findApiProxy/v4/aftermarket/find/auction/recommend"
            f"?endTimeAfter=2025-06-16T06%3A59%3A09.972Z"
            "&experimentInfo=aftermarket-semantic-search-202502%3AB"
            "&paginationSize=1"
            "&paginationStart=0"
            f"&query={domain_query}"
            "&useExtRanker=true"
            "&useSemanticSearch=true"
        )

        driver = Driver(
            uc=True,
            headless=True,
            browser="chrome",
            proxy=f"http://{proxy_auth}",
            chromium_arg="--no-sandbox,--disable-dev-shm-usage,--disable-gpu,"
                         "--disable-blink-features=AutomationControlled,"
                         "--disable-extensions,--no-first-run,--disable-default-apps,"
                         "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        )

        # Stealth patch
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        driver.uc_open_with_reconnect(url, reconnect_time=6)
        driver.sleep(3)

        screenshot_path = "screenshot.png"
        driver.save_screenshot(screenshot_path)

        with open(screenshot_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        page_title = driver.get_title()
        timestamp = driver.execute_script("return new Date().toISOString()")

        # Send to webhook using proxy
        webhook_url = "https://n8n.scrapifyapi.com/webhook/fa92b96f-26c4-43aa-9e9c-acb43c6145ce"
        proxies = {
            "http": f"http://{proxy_auth}",
            "https": f"http://{proxy_auth}",
        }
        payload = {
            "screenshot": img_base64,
            "url": url,
            "page_title": page_title,
            "timestamp": timestamp,
            "status": "success"
        }

        response = requests.post(webhook_url, json=payload, timeout=30, proxies=proxies)
        if response.status_code != 200:
            raise Exception(f"Webhook failed with {response.status_code}: {response.text}")

        return {
            "title": page_title,
            "timestamp": timestamp,
            "screenshot_base64": img_base64,
            "webhook_response": response.text[:200]
        }

    finally:
        if driver:
            driver.quit()


@app.post("/run-scraper")
def scrape(request: ScrapeRequest):
    try:
        result = run_scraper(request.query)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
