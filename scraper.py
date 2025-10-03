import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# --- Configuration ---
DOWNLOAD_KEYWORDS = ['download', 'syllabus',
                     'regulation', 'question papers', 'curriculum']

Dwnld_ext = ['.pdf']

# --- Tool 1: The Map Maker ---


def xpath_traversal(scheme_name, target_text):
    """
    Builds the robust 'common ancestor' XPath string.
    """
    # Simple: Find any link that's near the scheme text
    return f"//*[contains(., '{scheme_name}')]/following::a[contains(., '{target_text}')] | //*[contains(., '{scheme_name}')]/following::button[contains(., '{target_text}')]"


# --- Tool 2: The Navigator ---
def scrape_links(driver, url, scheme_name, target_text):
    print(f"Navigating to {url} to perform targeted click...")
    try:
        driver.get(url)
        time.sleep(3)

        print("Looking for 'Syllabus' link under B.TECH FULL TIME 2024 SCHEME...")

        syll_xpath = "//*[contains(., 'B.TECH FULL TIME 2024 SCHEME')]/following::a[contains(., 'Syllabus')][1]"

        wait = WebDriverWait(driver, 15)
        syll_link = wait.until(
            EC.presence_of_element_located((By.XPATH, syll_xpath)))

        print(f"Found syllabus link: '{syll_link.text}'")

        try:
            syll_link.click()
        except:
            print("Regular click failed, using JavaScript click...")
            driver.execute_script("arguments[0].click();", syll_link)

        print("Clicked on Syllabus link")
        return True
        time.sleep(5)

    except TimeoutException:
        print("Timed out waiting for elements")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during navigation: {e}")
        return False

# --- Tool 3: The Treasure Hunter ---


def find_pdf_links(driver):
    """
    SCANS the current page for downloads. Returns two lists.
    """
    print("[*] Scanning current page for all potential downloads...")
    direct_dwnld = set()
    click_dwnld = []

    try:
        xpath = "//a[contains(@href, '.pdf')] | //button | //*[@role='button']"
        wait = WebDriverWait(driver, 10)
        elements = wait.until(
            EC.visibility_of_all_elements_located((By.XPATH, xpath)))

        for elm in elements:
            try:
                url = elm.get_attribute('href')
                text = elm.text.strip().lower()

                if url and any(url.lower().endswith(ext) for ext in Dwnld_ext):
                    direct_dwnld.add(url)
                    continue

                if text and any(keyword in text for keyword in DOWNLOAD_KEYWORDS):
                    if elm.is_displayed() and elm.is_enabled():
                        click_dwnld.append(elm)
            except Exception:
                continue

    except TimeoutException:
        print("No potential download links or buttons were found on this page.")

    found_urls = list(direct_dwnld)
    print(f"[*] Scan complete. Found {len(found_urls)} direct link(s) and {
          len(click_dwnld)} clickable download element(s).")
    return found_urls, click_dwnld
