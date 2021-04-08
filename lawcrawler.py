from bs4 import BeautifulSoup
import requests
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
import time
import re
import os
from pprint import pprint

#TODO: Check if num of links matches total num of accessible verdicts
#TODO: Split the downloaded files into 대법원/고등법원/지방법원/기타
#TODO: User input should be a list. e.g. 250,251,252,253
#TODO: The crawler should repeat the process for each item in the list

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome('./driver/chromedriver',options=options)
driver.implicitly_wait(3) 

def exclude_special_char(text):
    pattern = r'[0-9a-zA-Zㄱ-ㅎ가-힣.,_ㆍ·\[\]]'
    match_res = re.findall(pattern,text)
    res = match_res
    return res

def check_folder_exists(file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
        print('[Created folder {}.]'.format(file_path))
    return True

def save_links_to_files(links,folder_name):
    count = 0
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
            title = ''.join(exclude_special_char(title))

            if len(title) > 0:
                folder_path = './data/{}'.format(folder_name)

                if check_folder_exists(folder_path):

                    if "대법원" in title:
                        folder_supreme = './data/{}/{}'.format(folder_name, "대법원")
                        check_folder_exists(folder_supreme)
                        f = open(folder_supreme+'/'+title+".txt", "w", encoding="utf-8")
                        f.write(str(content))
                        f.close()
                        count = count + 1

                    elif "고등법원" in title:
                        folder_high = './data/{}/{}'.format(folder_name, "고등법원")
                        check_folder_exists(folder_high)
                        f = open(folder_high+'/'+title+".txt", "w", encoding="utf-8")
                        f.write(str(content))
                        f.close()
                        count = count + 1

                    elif "고법" in title:
                        folder_high = './data/{}/{}'.format(folder_name, "고등법원")
                        check_folder_exists(folder_high)
                        f = open(folder_high+'/'+title+".txt", "w", encoding="utf-8")
                        f.write(str(content))
                        f.close()
                        count = count + 1

                    elif "지방법원" in title:
                        folder_local = './data/{}/{}'.format(folder_name, "지방법원")
                        check_folder_exists(folder_local)
                        f = open(folder_local+'/'+title+".txt", "w", encoding="utf-8")
                        f.write(str(content))
                        f.close()
                        count = count + 1

                    elif "지법" in title:
                        folder_local = './data/{}/{}'.format(folder_name, "지방법원")
                        check_folder_exists(folder_local)
                        f = open(folder_local+'/'+title+".txt", "w", encoding="utf-8")
                        f.write(str(content))
                        f.close()
                        count = count + 1

                    else:
                        folder_etc = './data/{}/{}'.format(folder_name, "기타")
                        check_folder_exists(folder_etc)
                        f = open(folder_etc+'/'+title+".txt", "w", encoding="utf-8")
                        f.write(str(content))
                        f.close()
                        count = count + 1
                        print("[saved all]")
                        
        except OSError as err:
            print("[OS error: {0}]".format(err))
        except:
            print("[Unexpected error:{}]".format(sys.exc_info()[0]))
            raise
    return count    



def find_max_page_nr():
    result = driver.find_element_by_css_selector('#conPrecResultDiv > h2').text
    pattern = r'\(\d/(\d+)\)' #get captured string: group(1)
    searched_result = re.search(pattern, result)
    if searched_result:
        max_page_nr = searched_result.group(1)
        
    return int(max_page_nr)
    
def find_next_page_elm(li_title):
    try:
        page = driver.find_element_by_xpath('//*[@title='+li_title+']/a')
    except WebDriverException:
        page = driver.find_element_by_css_selector("#precPageFrm > div.paging > div > a:nth-child(8)")
    return page


def collect_doc_links(query):
    print('[ Loading... ]')
    url = "https://www.law.go.kr/joStmdInfoP.do?lsiSeq=222447&joNo={}&joBrNo=00".format(query)
    driver.get(url)
    max_page_nr = find_max_page_nr()
    data_links = []
    for i in range(max_page_nr):
        current_page = i + 2 
        urls = driver.find_elements_by_css_selector('dt.bbg02 > a')
        if urls:
            for url in urls:
                link = url.get_attribute('href') 
                if 'LSW' in link:
                    data_links.append(link)
        else:
            print('[No url found on page {}]'.format(current_page))
        try:
            li_title = '"{}페이지"'.format(current_page) #2페이지부터 클릭; added double quotes
            next_page = find_next_page_elm(li_title)
            if next_page:
                print('[Clicking on page {}]'.format(current_page))
            next_page.click()
        except:
            if current_page > max_page_nr:
                print('[Reached the last page.]')
            else:
                print('[Could not click on page {}.]'.format(current_page))
                print('[Skipping to next page.]')
        finally:
            time.sleep(3)

    return data_links

def main():
    user_input = input('[Article number]: ')
    article_list = user_input.split(',')

    for i in range(len(article_list)):
        print('[Start article {} crawling]'.format(article_list[i]))
        article_nr = '%0*d'%(4, int(article_list[i])) #if len(user_input) < 5, pads user_input with 0 
        links = collect_doc_links(article_nr)
        print('[Found {} links to download.]'.format(len(links)))

        if links:
            user_folder_name = '형법{}조'.format(article_list[i])
            download_count = save_links_to_files(links,user_folder_name)
            print('[{} out of {} cases downloaded.]'.format(download_count, len(links)))

        else:
            print('No links found.')
        print("[Article {} Crawling complete.]".format(article_list[i]))
        print('--------------------------------------')
    
if __name__ == '__main__':
    main()