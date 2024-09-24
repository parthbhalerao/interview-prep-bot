import os
from dotenv import load_dotenv
from selenium.webdriver import Remote, ChromeOptions  
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection  
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

SBR_WEBDRIVER = 'https://brd-customer-hl_982709ac-zone-empowering_education:xv0c1qvqt14s@brd.superproxy.io:9515'

# Credentials - SBR_WEBDRIVER
def get_SBR_WEBDRIVER():
    # TODO: Add a logging function
    load_dotenv()
    SBR_WEBDRIVER : str = os.getenv('SBR_WEBDRIVER')
    return SBR_WEBDRIVER

# Function to create a session
def create_session(SBR_WEBDRIVER):
    # TODO: Add a logging function
    sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, 'goog', 'chrome')
    return sbr_connection

# Scrape Website Function #
def scrape_website(website):
    print('Launching Chrome Browser...')
    # SBR_WEBDRIVER = get_SBR_WEBDRIVER()
    sbr_connection = create_session(SBR_WEBDRIVER) 
    with Remote(sbr_connection, options=ChromeOptions()) as driver:  
        print('Connected! Navigating...')  
        driver.get(website)

        # CAPTCHA Handling
        print('Waiting for Captcha to solve...')
        solve_res = driver.execute('executeCdpCommand', {
            'cmd': 'Captcha.waitForSolve',
            'params' : {'detectTimeout' : 10000},
        })
        print('Captcha solve status:', solve_res['value']['status'])
        
        # Scraping the website & returning it
        print('Navigated! Scraping page content...')  
        html = driver.page_source  
        return html

# Cleaning the scraped content #
def extract_body_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    body_content = soup.body

    if body_content:
        return str(body_content)
    return ""

def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, 'html.parser')

    for script_or_style in soup(['script', 'style']):
        script_or_style.extract()

    cleaned_content = soup.get_text(separator='\n')
    cleaned_content = '\n'.join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )

    return cleaned_content

# Splitting this content in batches
def split_body_content(content, max_length=6000):
    return [
        content[i : i + max_length] for i in range(0, len(content), max_length)
    ]

# Testing the scrape_website() function
website = 'https://techwithtim.com'
html = scrape_website(website)