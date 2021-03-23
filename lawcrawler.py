from bs4 import BeautifulSoup
import requests
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from pprint import pprint

driver = webdriver.Chrome('../driver/chromedriver')
driver.implicitly_wait(3) 
        
def save(links):
    for i in range(len(links)):
        driver.get(links[i])
        title =''

        title1 = driver.find_element_by_css_selector('.subtit1').text.replace(" ","")
        title2 = driver.find_element_by_css_selector('#contentBody > h2').text.replace(" ","") 
        title = title1 + title2
        title = title.replace(":", "_")
        
        content = ''
        content = driver.find_element_by_css_selector('#contentBody').text
        
        try:
            print(title)
            if len(title) > 0:
                f = open(title+".txt", "w", encoding="utf-8")
                f.write(str(content))
                f.close()    
            
        except OSError as err:
            print("OS error: {0}".format(err))
            #NOTE: occurs when special chararcter is used in the title
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise


    

def cralwer(keyword):
    ##Loading page
    print('[ Loading... ]')

    

    url = "https://www.law.go.kr/joStmdInfoP.do?lsiSeq=222447&joNo={}&joBrNo=00".format(keyword)
    driver.get(url)
    #load page
    links = []
    for i in range(10):
        try:
            urls = driver.find_elements_by_css_selector('dt.bbg02 > a')
            

            for url in urls:
                link = url.get_attribute('href') 
                if 'LSW' in link:
                    links.append(link)
           

            page = driver.find_element_by_css_selector("#precPageFrm > div.paging > div > a:nth-child(8)")
            page.click()
            time.sleep(3)
            print("")
        except:
            print(str(i)+"page")
    
    save(links)


    
    
    
    


def main():
    keword = input("No: ")
    cralwer(keword)

main()
