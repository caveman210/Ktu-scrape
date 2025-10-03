import os
import time
import scraper
import downloadr
import browser_finder

# --- Configuration ---
START_URL = "https://ktu.edu.in/academics/scheme"
DOWNLOAD_DIR = os.path.join(os.path.expanduser(
    "~"), "Downloads", "KTU_Scraper_Downloads")
ANCHOR_TEXT = "B.TECH FULL TIME 2024 SCHEME"
TARGET_TEXT = "Syllabus"

# --- NEW: Helper Function for Tab Management ---


def handle_new_tabs(driver, original_window_handle):
    """
    Checks for new tabs, switches to the new one, and returns its handle.
    """
    new_window_handle = None
    # Wait a moment for the new tab to open
    time.sleep(2)
    for handle in driver.window_handles:
        if handle != original_window_handle:
            new_window_handle = handle
            break

    if new_window_handle:
        print(f"[*] New tab detected. Switching focus...")
        driver.switch_to.window(new_window_handle)

    return new_window_handle

# --- Helper Function for Click-to-Download (Upgraded) ---


def handle_clickable_downloads(driver, elements, download_dir):
    """
    Iterates through clickable elements, handles new tabs, clicks, and waits for a download.
    """
    original_window = driver.current_window_handle

    for element in elements:
        try:
            print(
                f"\n[*] Attempting to download via click on: '{element.text.strip()}'")
            files_before = set(os.listdir(download_dir))

            # Click the element, which might open a new tab
            element.click()

            # Check for and handle a new tab
            new_tab = handle_new_tabs(driver, original_window)

            # Wait for the download to complete
            waited = 0
            download_complete = False
            while waited < 30:  # Max wait 30 seconds
                files_after = set(os.listdir(download_dir))
                new_files = files_after - files_before

                if new_files:
                    new_file = new_files.pop()
                    if not new_file.endswith(('.crdownload', '.part')):
                        print(f"[✔] Download complete: {new_file}")
                        download_complete = True
                        break
                time.sleep(1)
                waited += 1

            if not download_complete:
                print("[✘] Timed out waiting for download to complete.")

            # CRITICAL: If a new tab was opened, close it and switch back
            if new_tab:
                print("[*] Closing new tab and returning to main page.")
                driver.close()
                driver.switch_to.window(original_window)

        except Exception as e:
            print(f"[✘] Error clicking or waiting for download: {e}")
            # Ensure we are back on the main window in case of an error
            driver.switch_to.window(original_window)

# --- Main Workflow ---


def run_scraper():
    """Orchestrates the entire scraping process."""
    print("--- Starting the KTU Syllabus Scraper ---")
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    driver = browser_finder.browser_sniffer(DOWNLOAD_DIR)

    if driver:
        try:
            # --- STEP 1: INITIAL TARGETED TRAVERSAL ---
            original_window = driver.current_window_handle
            click_success = scraper.scrape_links(
                driver, START_URL, ANCHOR_TEXT, TARGET_TEXT)

            if click_success:
                # After the click, check if a new tab was opened for navigation
                handle_new_tabs(driver, original_window)

                print(
                    "\n[+] Navigation successful. Now scanning the new page for downloads...")
                time.sleep(3)

                # --- STEP 2: SCAN AND DOWNLOAD ---
                direct_links, clickable_elements = scraper.find_pdf_links(
                    driver)

                if direct_links:
                    print(f"\n--- Found {len(direct_links)
                                         } direct PDF link(s) to download ---")
                    for link in direct_links:
                        downloadr.download_file(link, DOWNLOAD_DIR)

                if clickable_elements:
                    print(f"\n--- Found {len(clickable_elements)
                                         } clickable element(s) to process ---")
                    handle_clickable_downloads(
                        driver, clickable_elements, DOWNLOAD_DIR)

                if not direct_links and not clickable_elements:
                    print("\n--- No downloadable items found on the target page. ---")
            else:
                print("\n[✘] Initial navigation failed. Cannot proceed. Exiting.")

        finally:
            print("\n[*] Script finished. Closing WebDriver.")
            driver.quit()


if __name__ == "__main__":
    run_scraper()
