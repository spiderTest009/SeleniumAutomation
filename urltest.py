import time
import os
from selenium.webdriver import Remote
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

TEST_URLS = [
    "https://reddensoft.com/our-leadership-team",
    "https://reddensoft.com/blog",
    "https://reddensoft.com/hire-us",
    "https://reddensoft.com/contact",
]

BROWSERLESS_KEY = os.getenv("BROWSERLESS_KEY")


def run_selenium_tests(socketio, emit_log):
    """Uses Browserless remote Chrome so Railway works"""

    if not BROWSERLESS_KEY:
        emit_log("❌ Missing BROWSERLESS_KEY environment variable", "error")
        socketio.emit("test_complete")
        return

    endpoint = f"https://chrome.browserless.io/webdriver?token={BROWSERLESS_KEY}"

    driver = None

    try:
        emit_log("🌐 Connecting to Browserless remote Chrome...", "info")

        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--headless=new")

        driver = Remote(
            command_executor=endpoint,
            options=chrome_options
        )
        driver.set_page_load_timeout(20)

        emit_log(f"🔍 Starting tests for {len(TEST_URLS)} URLs", "success")

        passed = failed = 0

        for i, url in enumerate(TEST_URLS, 1):
            emit_log(f"\n[{i}/{len(TEST_URLS)}] Testing: {url}", "info")

            try:
                driver.get(url)
                time.sleep(1)

                title = driver.title or "No Title"
                final_url = driver.current_url

                emit_log(f"✓ Loaded: {final_url}", "success")
                emit_log(f"✓ Title: {title}", "success")
                passed += 1

                socketio.emit("test_result", {
                    "url": url,
                    "status": "pass",
                    "title": title,
                    "status_code": 200
                })

            except TimeoutException:
                emit_log("⏳ Timeout loading page", "error")
                failed += 1
                socketio.emit("test_result", {
                    "url": url,
                    "status": "fail",
                    "title": "Timeout",
                    "status_code": 0
                })

            except Exception as e:
                emit_log(f"❌ Error: {str(e)}", "error")
                failed += 1

                socketio.emit("test_result", {
                    "url": url,
                    "status": "fail",
                    "title": "Error",
                    "status_code": 0
                })

        emit_log("\n==== SUMMARY ====", "info")
        emit_log(f"Total: {len(TEST_URLS)} | Passed: {passed} | Failed: {failed}",
                 "success")

    finally:
        if driver:
            driver.quit()
            emit_log("🔻 Remote WebDriver closed", "info")

        socketio.emit("test_complete")
