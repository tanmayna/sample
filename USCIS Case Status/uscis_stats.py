#Enter you case number here
your_case_number = 'YSC2090254738'

# Importing packages

import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

import random
import datetime
import time
import os
import warnings
warnings.filterwarnings("ignore")

def create_phantomjs(url, wait_time = 1):
    '''
    This function creates a 'headless browser' i.e. an invisible browser
    '''
    driver = webdriver.PhantomJS()
    driver.set_window_size(1920,1080)
    time.sleep(wait_time)
    driver.get(url)
    time.sleep(wait_time*2)
    return driver

def check_mine():
    '''
    This function checks your case status
    '''
    driver = create_phantomjs(r'https://egov.uscis.gov/casestatus/landing.do')
    driver.find_elements_by_class_name('form-control')[0].send_keys(your_case_number)
    driver.find_elements_by_class_name('btn2')[0].click()
    result = driver.find_elements_by_class_name('rows')[0].text.split('\n')[0]
    
    print('\n')
    print('Your case: ' + result)
    print('\n')
    return driver

def check_range(wait_time = 1):
    '''
    This function checks a random sample of users in your series
    '''
    d = {}
    l = []
    total_users = 100
    
    cnt = 0
    print('Checking ' + str(total_users) + ' random cases of series ' + str(your_case_number[:-3]) + 'XXX')
    for i in range(total_users):
        if(i%10==0):
            print(str(total_users - cnt*10) + ' to go..')
            cnt+=1
        
        flag = 0
        while(flag == 0):
            rand_num = random.randint(100,999)
            if(rand_num not in l):
                flag = 1
        
        l.append(rand_num)
        
        time.sleep(wait_time)
        driver.find_elements_by_class_name('form-control')[0].send_keys(str(your_case_number[:-3]) + str(rand_num))
        driver.find_elements_by_class_name('btn2')[0].click()
        time.sleep(wait_time)
        
        result = driver.find_elements_by_class_name('rows')[0].text.split('\n')[0]

        if(result in d):
            d[result]+=1
        else:
            d[result]=1
        
    return d

def check_case_percentage(d):
    successful_cases = 0

    try:
        successful_cases+= d['Card Was Delivered To Me By The Post Office']
    except:
        pass
    try:
        successful_cases+= d['Fingerprint Fee Was Received']
    except:
        pass
    try:
        successful_cases+= d['Notice Was Returned To USCIS Because The Post Office Could Not Deliver It']
    except:
        pass
    try:
        successful_cases+= d['Card Was Picked Up By The United States Postal Service']
    except:
        pass
    try:
        successful_cases+= d['New Card Is Being Produced']
    except:
        pass
    try:
        successful_cases+= d['Card Was Mailed To Me']
    except:
        pass
    try:
        successful_cases+= d['Case Was Approved']
    except:
        pass
    try:
        successful_cases+= d['Card Was Returned To USCIS']
    except:
        pass
    try:
        successful_cases+= d['Case Was Updated To Show Fingerprints Were Taken']
    except:
        pass

    in_process_cases = d['Case Was Received']
    percent_completed = round(((successful_cases*100)/(successful_cases + in_process_cases)), 2)

    return percent_completed

# Main script
driver = check_mine()
d = check_range()

print('\n')
for i in d:
    print(i + ': '+ str(d[i]))


percent_completed = check_case_percentage(d)

print('\n')
print('Percent Cases Completed: ' + str(percent_completed) + ' %')

