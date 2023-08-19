import os
import time
import json
import logging
import smtplib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Email settings
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM')
EMAIL_TO = os.getenv('EMAIL_TO')
EMAIL_SUBJECT = os.getenv('EMAIL_SUBJECT')

# SSSB website URLs
SSSB_URLS = [
    'https://sssb.se/en/looking-for-housing/apply-for-apartment/new-constructions/?pagination=0&paginationantal=0',
    'https://sssb.se/en/looking-for-housing/apply-for-apartment/available-apartments/?pagination=0&paginationantal=0'
]

# File path to store previously seen apartments
PREVIOUSLY_SEEN_FILE = './out/previous_apartments.txt'

# Logging settings
LOG_FILE = './out/logfile.log'
LOG_LEVEL = logging.INFO

# EXCLUDE SETTINGS
EXCLUDE_TYPES = json.loads(os.getenv('EXCLUDE_TYPES'))
EXCLUDE_AREAS = json.loads(os.getenv('EXCLUDE_AREAS'))

# Cron settings
TIME_INTERVAL = int(os.getenv('TIME_INTERVAL'))

def setup_logger():
    """Set up logging."""
    logger = logging.getLogger(__name__)
    logger.setLevel(LOG_LEVEL)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

    # Log to file
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Log to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

def send_email(subject, body):
    """Send email notification."""
    message = f'Subject: {subject}\n\n{body}'

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, message)

def parse_text(text):
    return text.encode("ascii", "replace").decode("ascii").strip()

def scrape_sssb_website(logger):
    """Scrape the SSSB website for new apartments/studios."""
    # Load previously seen apartments
    if os.path.exists(PREVIOUSLY_SEEN_FILE):
        with open(PREVIOUSLY_SEEN_FILE, 'r') as f:
            seen_apartments = set(f.read().splitlines())
    else:
        seen_apartments = set()

    # Set up headless web browser
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument("--headless")
    options.add_argument('--disable-dev-shm-usage')

    with webdriver.Chrome(executable_path="/usr/bin/chromedriver", options=options) as driver:
        driver = webdriver.Chrome(options=options)

        for sssb_url in SSSB_URLS:
            driver.get(sssb_url)

            if driver.find_elements(By.CLASS_NAME, 'NoResult'):
                logger.info(f'No apartments found in {sssb_url}.')
                continue

            # Find all apartment/studio listings
            listings = driver.find_elements(By.CSS_SELECTOR, '.ObjektListItem')

            for listing in listings:
                # Extract the listing information
                type_ = parse_text(listing.find_element(By.CSS_SELECTOR, '.ObjektTyp a').text)
                url = parse_text(listing.find_element(By.CSS_SELECTOR, '.ObjektTyp a').get_attribute('href'))
                address = parse_text(listing.find_element(By.CSS_SELECTOR, '.ObjektAdress a').text)

                details = listing.find_element(By.CSS_SELECTOR, '.ObjektDetaljer')

                obj_number = parse_text(details.find_elements(By.CLASS_NAME, 'ObjektNummer')[1].get_attribute('innerText'))
                area = parse_text(details.find_elements(By.CLASS_NAME, 'ObjektOmrade')[1].text)
                floor = parse_text(details.find_elements(By.CLASS_NAME, 'ObjektVaning')[1].text)
                space = parse_text(details.find_elements(By.CLASS_NAME, 'ObjektYta')[1].text)
                rent = parse_text(details.find_elements(By.CLASS_NAME, 'ObjektHyra')[1].text)
                start = parse_text(details.find_elements(By.CLASS_NAME, 'ObjektInflytt')[1].text)

                key = f'{obj_number}@{start}'

                # Check if the listing is new and should not be excluded
                if key not in seen_apartments and\
                        type_ not in EXCLUDE_TYPES and\
                        area not in EXCLUDE_AREAS:
                    # Add the listing to the list of seen listings
                    seen_apartments.add(key)

                    # Print the new listing details
                    logger.info(f'New listing: {url}')
                    body = f'New student apartment/studio available!\n\nTitle: {type_}\nLocation: {area}\nAddress: {address}\nFloor: {floor}\nSpace: {space}\nPrice: {rent}\nStart: {start}\nURL: {url}'
                    send_email(EMAIL_SUBJECT, body)

    # Save the list of seen apartments
    with open(PREVIOUSLY_SEEN_FILE, 'w') as f:
        f.write('\n'.join(seen_apartments))

    # Clean up
    driver.quit()

if __name__ == '__main__':
    logger = setup_logger()
    scrape_sssb_website(logger)
