"""
Prerequisites
- Selenium: Install Selenium library using pip install selenium.
- WebDriver: The script uses ChromeDriver, which must be installed and its path defined at CHROME_DRIVER_PATH or via an environment variable.

Chrome for Testing and its driver can be installed via npx `@puppeteer/browsers`, which provides the command `install` which can 
be used to install `chrome@<version>` for testing and `chromedriver@<version>`.
Note: 
- Ensure that the version of the driver and test browser match.
- Avoid using the testing browser for casual browsing, as it not updated automaticly.
"""

import base64
import os
import sys
import shutil
import time
from pathlib import Path

from flask import current_app
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.logging import build_logger


def get_browser_and_driver_path():
    CHROME_VERSION = "win64-123.0.6312.122"
    cur_dir = Path(os.getcwd())
    scraper_base_dir = (
        f"{cur_dir.parent if current_app.config['DEBUG'] else cur_dir}"
        f"{os.sep}scraper{os.sep}"
    )
    browser_path = scraper_base_dir + (
        f"chrome{os.sep}{CHROME_VERSION}{os.sep}chrome-win64{os.sep}chrome.exe"
        if sys.platform.startswith('win32')
        else f""
    )

    driver_path = scraper_base_dir + (
        f"chromedriver{os.sep}{CHROME_VERSION}{os.sep}chromedriver-win64{os.sep}chromedriver.exe"
        if sys.platform.startswith('win32')
        else f""
    )



    return browser_path, driver_path


OUTPUT_DIR_PATH = f"{os.getcwd()}{os.sep}pdfs"

log = build_logger(__name__)


def setup_driver():
    """
    Sets up the Selenium WebDriver with the required options for Chrome.
    Ensures the download directory exists and configures Chrome to automatically
    download PDF files to the designated directory without user intervention.
    """
    browser_path, driver_path = get_browser_and_driver_path()

    # Create the output directory if it does not exist
    if not os.path.exists(OUTPUT_DIR_PATH):
        os.makedirs(OUTPUT_DIR_PATH)

    # Configure Chrome options for headless operation and disable GPU
    options = Options()
    options.add_argument('--headless')
    options.binary_location = browser_path
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": OUTPUT_DIR_PATH,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,  # Use the given download directory
            "plugins.always_open_pdf_externally": True,
            "profile.default_content_settings.popups": 0
        }
    )
    # Initialize the ChromeDriver with the specified options and path
    driver = webdriver.Chrome(
        service=Service(executable_path=driver_path),
        options=options
    )

    # Navigate to the initial URL and handle cookie consent
    driver.get("https://issuu.com/kngfdefysiotherapeut")
    button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable(
            (By.ID, "CybotCookiebotDialogBodyButtonDecline"))
    )
    button.click()

    return driver


def download_file(driver, url):
    """
    Navigates to the provided URL and initiates a file download by clicking the download button.
    This function handles iframe contexts and ensures the download button is clickable.
    """

    driver.get(url)

    # Wait for the iframe that contains the download button to become available and switch to it
    iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "DocPageReaderIframe"))
    )
    driver.switch_to.frame(iframe)

    # Find and click the download button
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[data-testid='download-button']"))
    )
    button.click()
    time.sleep(1)  # Sleep briefly to allow the download to initiate


def scrape():
    """
    Main function to set up the driver, collect all target URLs for download,
    and manage the file downloading process.
    """

    driver = setup_driver()

    # Extract pagination elements and store their href attributes
    pagination_elements = driver.find_elements(
        By.CLASS_NAME,
        "pagination-button__page-index"
    )

    overview_pages = [e.get_attribute('href') for e in pagination_elements]

    urls = []

    # Navigate to each pagination page and collect publication URLs
    for p in overview_pages:
        driver.get(p)

        links = driver.find_elements(
            By.CLASS_NAME,
            "PublicationCard__publication-card__card-link__hUKEG__0-0-2875"
        )

        urls += [l.get_attribute('href') for l in links]

    log.info(f"{len(urls)} magazines found.")

    # Process each URL by downloading the associated PDF
    for i, url in enumerate(urls, start=1):
        log.info(f"Scraping {i}: {url}")
        download_file(driver, url)

    # Wait for all files to download completely before exiting
    WebDriverWait(driver, 120, poll_frequency=1).until(
        lambda _: not any(file.endswith('.crdownload')
                          for file in os.listdir(OUTPUT_DIR_PATH))
    )
    log.info(f"Scraping complete.")
    log.info(f"Starting clean up...")

    pdf_files = [file
                 for file in os.listdir(OUTPUT_DIR_PATH)
                 if file.endswith('.pdf')]

    pdfs = []
    for file in pdf_files:
        with open(f"{OUTPUT_DIR_PATH}{os.sep}{file}", "rb") as binary_file:
            pdfs.append({"name": file, "content": base64.b64encode(
                binary_file.read()).decode('utf-8')})

    if not current_app.config['DEBUG']:
        shutil.rmtree(OUTPUT_DIR_PATH)

    log.info(f"Clean up complete")

    return pdfs
