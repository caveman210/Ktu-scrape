import os
import shutil
import platform
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.service import Service as FirefoxService

from selenium_stealth import stealth


def path_determiner():
    op_sys = platform.system()
    browsers = []
    check_br = {
        'chrome': {
            "Windows": lambda: os.path.exists(os.path.join(os.environ['ProgramFiles'], "Google/Chrome/Application/chrome.exe")),
            "Linux": lambda: shutil.which('google-chrome') is not None
        },
        'firefox': {
            "Windows": lambda: os.path.exists(os.path.join(os.environ['ProgramFiles'], "Mozilla Firefox/firefox.exe")),
            "Linux": lambda: shutil.which('firefox') is not None
        },
        'chromium': {
            "Linux": lambda: (shutil.which('chromium-browser') or shutil.which('chromium')) is not None
        },
        'edge': {
            "Windows": lambda: os.path.exists(os.path.join(os.environ["ProgramFiles (x86)"], "Microsoft/Edge/Application/msedge.exe")),
            "Linux": lambda: shutil.which('microsoft-edge') is not None
        }
    }

    for browsr, chk in check_br.items():
        check_func = chk.get(op_sys)
        if check_func and check_func():
            browsers.append(browsr)

    print(f"Found installed browsers: {browsers}")
    return browsers


drv_conf = {
    'chrome': {
        'driver': webdriver.Chrome,
        'service': ChromeService,
        'manager': ChromeDriverManager,
        'options': webdriver.ChromeOptions
    },
    'firefox': {
        'driver': webdriver.Firefox,
        'service': FirefoxService,
        'manager': GeckoDriverManager,
        'options': webdriver.FirefoxOptions
    },
    'edge': {
        'driver': webdriver.Edge,
        'service': EdgeService,
        'manager': EdgeChromiumDriverManager,
        'options': webdriver.EdgeOptions
    },
    'chromium': {
        'driver': webdriver.Chrome,
        'service': ChromeService,
        'manager': ChromeDriverManager,
        'options': webdriver.ChromeOptions
    }
}


def browser_sniffer(download_dir):
    installed_browsers = path_determiner()
    priority = [key for key in ['chrome', 'firefox',
                                'edge', 'chromium'] if key in installed_browsers]

    if not priority:
        print("\nNo supported browsers found. Please install Chrome or Firefox.")
        return None

    for browser_name in priority:
        print(f"Trying to launch {browser_name.capitalize()}...")
        try:
            config = drv_conf[browser_name]
            options = config['options']()
            options.add_argument("--start-maximized")
            options.add_argument("--window-size=1920,1080")

            if browser_name in ['chrome', 'chromium', 'edge']:
                prefs = {
                    "download.default_directory": download_dir,
                    "download.prompt_for_download": False,
                    "plugins.always_open_pdf_externally": True
                }
                options.add_experimental_option("prefs", prefs)

            if browser_name == 'firefox':
                options.set_preference("browser.download.dir", download_dir)
                options.set_preference("browser.download.folderList", 2)
                options.set_preference(
                    "browser.helperApps.neverAsk.saveToDisk", "application/pdf")
                options.set_preference("pdfjs.disabled", True)

            if browser_name == 'chromium':
                options.binary_location = shutil.which(
                    'chromium-browser') or shutil.which('chromium')

            service = config['service'](config['manager']().install())
            driver = config['driver'](service=service, options=options)

            if browser_name in ['chrome', 'chromium', 'edge']:
                stealth(driver,
                        languages=["en-US", "en"],
                        vendor="Google Inc.",
                        platform="Win32",
                        webgl_vendor="Intel Inc.",
                        renderer="Intel Iris OpenGL Engine",
                        fix_hairline=True,
                        )

            print(f"Launched {browser_name.capitalize()} successfully.")
            return driver

        except (WebDriverException, KeyError, Exception) as e:
            print(f"An error occurred, unable to launch {
                  browser_name.capitalize()}.")
            print(f"Reason: {e}")
            continue

    print("\nCould not initialize a WebDriver for any installed browser.")
    return None
