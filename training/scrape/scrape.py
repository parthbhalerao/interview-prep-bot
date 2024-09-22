from selenium.webdriver import Remote, ChromeOptions  
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection  
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# Credentials - the zone name and password
USER : str = 'brd-customer-hl_982709ac-zone-empowering_education'
PASS : str = 'xv0c1qvqt14s'
AUTH = USER + ':' + PASS

SBR_WEBDRIVER = f'https://{AUTH}@zproxy.lum-superproxy.io:9515'  

# Scrape Website Function #
def scrape_website(website):
    print('Launching Chrome Browser...')

    sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, 'goog', 'chrome')  
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