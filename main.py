import os
import browser_finder
import scraper
import downloadr

PAGE_URL = "https://ktu.edu.in/eu/core/syllabus.htm"
DOWNLOAD_DIR = "~/Downloads/KTU_syllabus"


def run_scraper():
    """The main function to orchestrate the scraping process."""
    print("--- Starting the KTU Syllabus Scraper ---")

    driver = browser_finder.browser_finder()

    if driver:
        try:
            pdf_links = scraper.scrape_links(driver, PAGE_URL)

            if pdf_links:
                print(f"\n--- Starting Download of {len(pdf_links)} Files ---")
                for link in pdf_links:
                    downloadr.download_file(link, DOWNLOAD_DIR)
                print("\n--- All downloads attempted. ---")
            else:
                print("--- No links to download. Exiting. ---")

        finally:
            print("\n Closing WebDriver.")
            driver.quit()

    print("\n--- Scraper finished. ---")


if __name__ == "__main__":
    run_scraper()
