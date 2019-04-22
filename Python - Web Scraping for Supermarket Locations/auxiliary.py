#### Importing standard packages ----
import numpy as np
import pandas as pd
import time
from datetime import date
import datetime
import xlsxwriter
import os
import shutil

from os import listdir
from os.path import isfile, join
from fuzzywuzzy import fuzz
import string
import re
import math

import googlemaps
from datetime import datetime

#### Importing web scraping packages ----
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

import bs4
import urllib.request
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup as soup

import requests
import json

downloads_directory = r'/Users/tanmay/Downloads/Grocery Stores//'

wait_time = 3
#   gmaps = googlemaps.Client(key='') #Enter the Google Maps API client key here

US_STATES = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','Florida','Georgia','Hawaii',
'Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota','Mississippi',
'Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma',
'Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia', 
'Wisconsin', 'Wyoming', 'District of Columbia', 'Puerto Rico', 'Guam', 'American Samoa','U.S. Virgin Islands','Northern Mariana Islands']


def create_driver(downloads_directory, url, wait_time = 3):
    '''
    This function creates a Selenium Webdriver.
    The window in which this url opens is set at a size of 1920*1080, so that all elements on the website are visible to the code.
    '''
    if not os.path.exists(downloads_directory):
        os.makedirs(downloads_directory)

    options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_settings.popups": 0,
             "download.default_directory": downloads_directory,
             "directory_upgrade": True}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(chrome_options=options)
    driver.set_window_size(1920,1080)
    driver.implicitly_wait(10)
    time.sleep(wait_time)
    driver.get(url)
    time.sleep(wait_time*2)
    return driver

def gmaps_latlong(x):
    '''
    This function returns the Latitude and Longitude values upon passing an address.
    '''
    temp = gmaps.geocode(x)[0].get('geometry').get('location')
    return(temp.get('lat'), temp.get('lng'))

def bs4_page(url, wait_time = 1, downloads_directory=downloads_directory):
    '''
    This function returns a BeautifulSoup object for the passed URL.
    '''

    if not os.path.exists(downloads_directory):
        os.makedirs(downloads_directory)

    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    web_byte = urlopen(req).read()
    time.sleep(wait_time)
    page_soup=soup(web_byte, 'html.parser')

    return page_soup

def top_cities(size=5000, file_location = r'/Users/tanmay/Downloads/Grocery Stores/Top5000Population.xls', space_char="%20", top=500):
    '''
    I obtained a ranked list of top 5000 cities by population in the US from this URL - http://img.ezlocal.com/data/Top5000Population.xls.
    This function returns the list of specified top cities in a form that is desired by the user.

    Method definitions -
    size: Overall number of cities desired
    top: Number of cities per state desired
    space_char: the character desired between the city and the state.
                For example, the default will return new%20york,ny for New York City.
    '''

    df_cities = pd.read_excel(file_location, header=None)
    df_cities.columns = ['City', 'State', 'Population']
    df_cities = df_cities.groupby('State').head(top).reset_index(drop = True)
    df_cities['City, State'] = df_cities['City'].apply(lambda x: x.strip()) + ',' + df_cities['State'].apply(lambda x: x.strip())
    df_cities['City, State'] = df_cities['City, State'].apply(lambda x:x.lower().replace(" ",space_char))

    cities_list = df_cities['City, State'].tolist()

    return cities_list[0:size]

def states_data(df_states_loc = r'/Users/tanmay/Downloads/Grocery Stores/50_us_states_all_data.csv'):
    '''
    I obtained the list of all US states from this URL - https://scottontechnology.com/list-of-50-us-states-in-excel/
    Returns a Python dictionary of all states and their abbreviations.
    '''
    df_states = pd.read_csv(df_states_loc, header=None)
    df_states.columns = ['Uppercase','State','Abbr','Short_Form']
    states_dict = dict(zip(df_states['State'], df_states['Abbr']))
    return states_dict

def zipcode_df(source_directory = r'/Users/tanmay/Downloads/Grocery Stores/zipcode_database.csv', omit=-1):
    '''
    I obtained the list of all zipcodes in the US from this URL - https://github.com/EqualPayChallengeHeinz/equalpay_webapp/blob/master/zipcode_database.csv.
    
    Method definitions -
    omit: Specifies how many digits can be omitted from the right for a zipcode.
          In most cases, the leftmost digit is not required, as zipcodes with the first four digits same cluster in the same area.
    '''
    df_zip = pd.read_csv(source_directory)
    df_zip['filter'] = df_zip['Zipcode'].apply(lambda x: str(x)[:omit])
    df_zip = df_zip.drop_duplicates(subset=['filter'])
    df_zip = df_zip[df_zip['ZipCodeType'] == 'STANDARD']
    return df_zip
