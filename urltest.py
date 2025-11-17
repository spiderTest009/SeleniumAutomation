import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from datetime import datetime

# Test URLs list
TEST_URLS = [
    "https://reddensoft.com/our-leadership-team",
    "https://reddensoft.com/blog",
    "https://reddensoft.com/hire-us",
    "https://reddensoft.com/partner-with-us",
    "https://reddensoft.com/realestate-software-development",
    "https://reddensoft.com/healthcare-software-development",
    "https://reddensoft.com/foodtech-software-development",
    "https://reddensoft.com/travel-hospitality-software-development",
    "https://reddensoft.com/automotive-software-development",
    "https://reddensoft.com/edtech-software-development",
    "https://reddensoft.com/ecommerce-software-development",
    "https://reddensoft.com/fintech-software-development",
    "https://reddensoft.com/website-design-services",
    "https://reddensoft.com/graphic-design-services",
    "https://reddensoft.com/ui-ux-design-services",
    "https://reddensoft.com/digital-marketing-services",
    "https://reddensoft.com/app-development-company",
    "https://reddensoft.com/web3-development-company",
    "https://reddensoft.com/saas-development-company",
    "https://reddensoft.com/paas-development-company",
    "https://reddensoft.com/iaas-development-company",
    "https://reddensoft.com/hire-ai-ml-developers",
    "https://reddensoft.com/hire-wordpress-developers",
    "https://reddensoft.com/hire-woocommerce-developers",
    "https://reddensoft.com/hire-shopify-developers",
    "https://reddensoft.com/hire-drupal-developers",
    "https://reddensoft.com/hire-duda-developers",
    "https://reddensoft.com/hire-devops-developers",
    "https://reddensoft.com/hire-python-developers",
    "https://reddensoft.com/hire-angular-developers",
    "https://reddensoft.com/hire-react-developers",
    "https://reddensoft.com/hire-nextjs-developers",
    "https://reddensoft.com/hire-vue-developers",
    "https://reddensoft.com/hire-android-app-developers",
    "https://reddensoft.com/hire-ios-app-developers",
    "https://reddensoft.com/hire-mobile-app-developers",
    "https://reddensoft.com/hire-php-developers",
    "https://reddensoft.com/hire-codeigniter-developers",
    "https://reddensoft.com/hire-full-stack-developers",
    "https://reddensoft.com/hire-laravel-developers",
    "https://reddensoft.com/hire-figma-designers",
    "https://reddensoft.com/hire-adobe-xd-designers",
    "https://reddensoft.com/hire-ui-developers",
    "https://reddensoft.com/ai-applications",
    "https://reddensoft.com/start-a-project",
    "https://reddensoft.com/contact",
    "https://reddensoft.com/portfolio/robocent",
    "https://reddensoft.com/portfolio/candid-sync",
    "https://reddensoft.com/portfolio/trispire",
    "https://reddensoft.com/portfolio/origami",
    "https://reddensoft.com/testimonials",
    "https://reddensoft.com/career"
]

def run_selenium_tests(socketio, emit_log):
    """Run selenium tests with socketio integration"""
    driver = None
    try:
        emit_log("Initializing Chrome WebDriver...", "info")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        emit_log(f"Starting tests for {len(TEST_URLS)} URLs", "success")
        
        passed = 0
        failed = 0
        
        for idx, url in enumerate(TEST_URLS, 1):
            emit_log(f"\n[{idx}/{len(TEST_URLS)}] Testing: {url}", "info")
            
            try:
                driver.get(url)
                time.sleep(1)
                
                title = driver.title
                current_url = driver.current_url
                
                status_code = driver.execute_script(
                    "return window.performance.getEntries()[0].responseStatus || 200"
                )
                
                if title:
                    emit_log(f"✓ Page Title: {title}", "success")
                    emit_log(f"✓ Status: Page Loaded Successfully", "success")
                    emit_log(f"✓ Final URL: {current_url}", "info")
                    passed += 1
                    
                    socketio.emit('test_result', {
                        'url': url,
                        'status': 'pass',
                        'title': title,
                        'status_code': status_code
                    })
                else:
                    emit_log(f"✗ Failed: No title found", "error")
                    failed += 1
                    
                    socketio.emit('test_result', {
                        'url': url,
                        'status': 'fail',
                        'title': 'N/A',
                        'status_code': 0
                    })
                    
            except TimeoutException:
                emit_log(f"✗ Timeout: Page took too long to load", "error")
                failed += 1
                socketio.emit('test_result', {
                    'url': url,
                    'status': 'fail',
                    'title': 'Timeout',
                    'status_code': 0
                })
                
            except Exception as e:
                emit_log(f"✗ Error: {str(e)}", "error")
                failed += 1
                socketio.emit('test_result', {
                    'url': url,
                    'status': 'fail',
                    'title': 'Error',
                    'status_code': 0
                })
        
        emit_log("\n" + "="*50, "info")
        emit_log(f"Test Summary:", "info")
        emit_log(f"Total: {len(TEST_URLS)} | Passed: {passed} | Failed: {failed}", "success")
        emit_log("="*50, "info")
        
    except Exception as e:
        emit_log(f"Fatal Error: {str(e)}", "error")
    
    finally:
        if driver:
            driver.quit()
            emit_log("WebDriver closed", "info")
        
        socketio.emit('test_complete')