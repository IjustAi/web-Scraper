from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import requests
import pandas as pd
import time 
from contact_lead import GetContacts

def LeadGeneration(Query,Location):
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)

    url = 'https://www.monster.com/jobs/search?q=' + Query + '&where='+ Location +'&page=1&so=m.s.sh'

    driver.get(url)
    time.sleep(5)

    scroll_container = driver.find_element(By.CSS_SELECTOR, ".infinite-scroll-component.undefined.ds-infinite-scroll")
    actions = ActionChains(driver)
    actions.move_to_element(scroll_container).click().perform()


    last_height = driver.execute_script('return arguments[0].scrollHeight;', scroll_container)
    no_new_content_loads = 0

    while True:
        actions.send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(5)
        new_height = driver.execute_script('return arguments[0].scrollHeight;', scroll_container)
    
        if new_height == last_height:
            no_new_content_loads += 1
            if no_new_content_loads >= 3:  
                break
        else:
            no_new_content_loads = 0  

        last_height = new_height
    

    soup = BeautifulSoup(driver.page_source,'html.parser')

    for script in soup(["script", "style"]): 
        script.extract() 

    li_elements = soup.find_all('li',class_='sc-blKGMR etPslv')

    leads={}
    lead_num=0

    for li in li_elements:
        result = li.text.strip() if li.text else "N/A"
        
        if result =='N/A':
            break

        a_tag = li.find('a',href=True)
        href = a_tag['href']
        position = a_tag.text.strip()
        c_name = li.find('span', attrs={"data-testid": "company"}).text.strip()

        lead_num+=1
        leads[lead_num] = [c_name, 'N/A', 'N/A', 'N/A', 'N/A', position, 'N/A', 'N/A']
    
    leads_df = pd.DataFrame.from_dict(leads, orient='index',
                                      columns=['Lead Name', 'LinkedIn', 'Website', 'Twitter', 'Contact Info (Email)',
                                               'Position', 'Contact Info (Phone)', 'Notes'])
    print(len(leads_df))
    return leads_df

def get_additional_data(Query,leads_df):
    for idx,row in leads_df.iterrows():
        try:  
            links =GetContacts(row['Lead Name'])
        except Exception as e:
            links = {"Twitter": "N/A", "LinkedIn": "N/A", "Email": "N/A", "Phone": "N/A"}

        leads_df.at[idx, 'LinkedIn'] = links.get("LinkedIn")
        leads_df.at[idx, 'Website'] = links.get("Website")
        leads_df.at[idx, 'Twitter'] = links.get("Twitter")
        leads_df.at[idx, 'Contact Info (Email)'] = links.get("Email")
        leads_df.at[idx, 'Contact Info (Phone)'] = links.get("Phone")
        leads_df.at[idx, 'Notes'] = 'Notes'

    path = "output(Monster)" + Query + ".csv"
    leads_df.to_csv(path, encoding='utf-8-sig')
   

    print("Leads Generation has finished")

def main():
    leads_df=LeadGeneration('Software Engineer','')
    get_additional_data('Software Engineer',leads_df)

if __name__=="__main__":
    main()
