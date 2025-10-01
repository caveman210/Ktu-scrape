from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def scrape_links(driver, url):
    print(f"To {url} to find downloads..")
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.visibility_of_all_elements_located(
            (By.CSS_SELECTOR, 'a[href$=".pdf"]')))

        pdf_ele = driver.find_elements(By.CSS_SELECTOR, 'a[href$=".pdf"]')
        if not pdf_ele:
            print("[!] No PDF links found on the page.")
            return []

        pdf_urls = [element.get_attribute('href') for element in pdf_ele]

        print(f"[*] Found {len(pdf_urls)} PDF links.")
        return pdf_urls

    except TimeoutException:
        print(f"Website timed out, could not load elements.")
        return []
    except Exception as e:
        print(f"[✘] An unexpected error occurred while scraping links: {e}")
        return []
