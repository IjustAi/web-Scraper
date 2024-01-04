from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time 
import re

def GetContacts(Query):
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome( options=options)

    wait = WebDriverWait(driver, 10)

    driver.get('https://www.google.com')
    time.sleep(2)

    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(Query)
    search_box.send_keys(Keys.RETURN)

    time.sleep(3)
    first_result = driver.find_element(By.XPATH, "(//h3)[1]")
    first_result.click()

    try:
        time.sleep(5)
        current_url = driver.current_url
        deny_cookies_btn = wait.until(EC.element_to_be_clickable(driver.find_element(By.ID, value='onetrust-accept-btn-handler')))
        deny_cookies_btn.click()
        time.sleep(7)
    except NoSuchElementException:
        try:
            accept_cookies_btn = wait.until(EC.element_to_be_clickable(driver.find_element(By.ID,value="onetrust-accept-btn-handler")))
            accept_cookies_btn.click()
            time.sleep(7)

        except:
            pass

    try:
        contact_link=wait.until(EC.element_to_be_clickable(driver.find_element(By.PARTIAL_LINK_TEXT, 'Contact')))
        contact_link.click()
        time.sleep(2)

    except NoSuchElementException:
        try:
            contact_link = wait.until(EC.element_to_be_clickable(driver.find_element(By.PARTIAL_LINK_TEXT, "Contact Us")))
            contact_link.click()
            time.sleep(2)
        
        except NoSuchElementException:
            links = {"Twitter": "N/A", "LinkedIn": "N/A", "Email": "N/A", "Phone": "N/A"}
            driver.quit() 
            return links

    time.sleep(2)

    html=driver.page_source
    soup =BeautifulSoup(html,'html.parser')

    links = {"LinkedIn": None, "Website": None, "Twitter": None, "Email": None, "Phone": None}
    links["Website"] = current_url
    phone_pattern = re.compile(
        r"\+1\s*\d{3}\s*\d{3}\s*\d{4}|\+1[-.\s]\d{3}[-.\s]\d{3}[-.\s]\d{4}|1[-.\s]\d{3}[-.\s]\d{3}[-.\s]\d{4}|\(\d{3}\)\s*\d{3}[-.\s]*\d{4}")

    for link in soup.find_all('a',href=True):
        href = link['href']
        text = link.text
        
        if "twitter" in href:
            links["Twitter"] = href
        if "linkedin" in href:
            links["LinkedIn"] = href
        if "mailto" in href:
            href = href.replace("mailto:%20", "")
            href = href.replace("mailto:", "")
            links["Email"] = href
        if "tel:" in href:
            potential_number = href.replace("tel:", "").strip()
            if phone_pattern.match(potential_number):
                links["Phone"] = potential_number
        
    driver.quit()
    return links
    
