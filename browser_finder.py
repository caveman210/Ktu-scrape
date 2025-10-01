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
            "Windows": lambda: os.path.exists(os.path.join(os.environ['ProgramFiles (x86)'], "Microsoft/Edge/Application/msedge.exe")),
            "Linux": lambda: shutil.which('microsoft-edge') is not None
        }
    }

    for browsr, chk in check_br.items():
        check = chk.get(op_sys)
        if check and check():
            browsers.append(browsr)
    print(f"Found browser: {browsers}")
    return browsers


drv_conf = {
    'chrome': {
        'driver': webdriver.Chrome,
        'service': ChromeService,
        'manager': ChromeDriverManager,
        'options': webdriver.ChromeOptions
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
    },
    'firefox': {
        'driver': webdriver.Firefox,
        'service': FirefoxService,
        'manager': GeckoDriverManager,
        'options': webdriver.FirefoxOptions
    },
}


def browser_finder():
    installed = path_determiner()
    priority = [key for key in drv_conf if key in installed]
    for i in priority:
        print(f"Trying {i.capitalize()}..")
        try:
            config = drv_conf[i]
            options_br = config['options']()
            service_br = config['service'](config['manager']().install())

            if i in ['chrome', 'chromium', 'edge']:
                # Basic anti-detection options are still a good idea
                options_br.add_argument("start-maximized")
                options_br.add_experimental_option(
                    "excludeSwitches", ["enable-automation"])
                options_br.add_experimental_option(
                    'useAutomationExtension', False)

                if i == 'chromium':
                    options_br.binary_location = shutil.which(
                        'chromium-browser') or shutil.which('chromium')

                # Create the driver
                driver = config['driver'](
                    service=service_br, options=options_br)

                # APPLY STEALTH
                stealth(driver,
                        languages=["en-US", "en"],
                        vendor="Google Inc.",
                        platform="Win32",
                        webgl_vendor="Intel Inc.",
                        renderer="Intel Iris OpenGL Engine",
                        fix_hairline=True,
                        )

            # --- END OF STEALTH IMPLEMENTATION ---

            # --- START OF NEW ANTI-DETECTION CODE ---
            if i in ['chrome', 'chromium', 'edge']:
                # This is the most important line for Chromium-based browsers
                options_br.add_argument(
                    "--disable-blink-features=AutomationControlled")
                options_br.add_experimental_option(
                    "excludeSwitches", ["enable-automation"])
                options_br.add_experimental_option(
                    'useAutomationExtension', False)

            if i == 'firefox':
                # This is the most important line for Firefox
                options_br.set_preference("dom.webdriver.enabled", False)
                options_br.set_preference('useAutomationExtension', False)
            # --- END OF NEW ANTI-DETECTION CODE ---

            driver = config['driver'](service=service_br, options=options_br)

            print(f"Launched {i.capitalize()} successfully.")
            return driver

        except (WebDriverException, KeyError) as e:
            print(f"Error occured, unable to launch {i.capitalize()}.")
            continue


'''
def check_browser():
    browser = ['chrome', 'firefox', 'edge', 'chromium']

    for i in browser:
        print(f"Launching browser {i.capitalize()}.. ")

        if i == 'chrome':
            options = webdriver.ChromeOptions()
            options.add_argument("--log-level=3")
            driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=options
            )
            print("Launched Chrome.")

        elif i == 'firefox':
            options = webdriver.FirefoxOptions()
            options.add_argument('--log-level=3')
            driver = webdriver.Firefox(
                service=ChromeService(GeckoDriverManager().install()),
                options=options
            )
            print("Launched Firefox.")

        elif i == 'edge':
            options = webdriver.EdgeOptions()
            options.add_argument('--log-level=3')
            driver = webdriver.Edge(
                service=EdgeService(EdgeChromiumDriverManager.install()),
                options=options
            )
            print("Launched Microsoft Edge.")

        elif i == 'chromium':
            chromium = shutil.which(
                'chromium-browser') or shutil.which('chromium')
            if chromium:
                options = webdriver.ChromeOptions()
                options.binary_location = chromium
                driver = webdriver.Chrome(
                    service=ChromeService(ChromeDriverManager.install()),
                    options=options
                )
            print("Launched Chromium with Chrome driver.")
'''
