'''
WEB SCRAPING USING BEAUTIFULSOUP

This code returns an Excel file with all Trader Joe's stores in the United States.
A csv file with cities in which there was an error returning the stores is also returned for debugging purposes.
'''
from auxiliary import *
wait_time = 3
grocery_chain = 'Trader Joes'

#Returning state abbreviations
store_states = [i.lower() for i in list(states_data().values())]

tj_cities = list()

for each_state in store_states:
    try:
        url = 'https://locations.traderjoes.com/' + each_state
        #Creating a beautifulsoup object
        page_soup = bs4_page(url)
        print(url)
        
        for element in page_soup.find_all("div", {"class": "itemlist"}):
            #Getting all states in which there is at least one trader joe's
            string = element.text
            string = string.lower().replace(" ","-")
            tj_cities.append(each_state + '/' + string)
    except:
        a = 1

#Creating empty lists
df = pd.DataFrame()
not_found = list()
STORE_NAME = list()
ADDRESS = list()
CITY = list()
STATE = list()
store_zip = list()
ZIP_CODE = list()

for each_city in tj_cities:
    try:
        url = 'https://locations.traderjoes.com/' + each_city
        page_soup = bs4_page(url)

        for element in page_soup.find_all("div", {"class": "address-left"}):
            print(element.text)
            STORE_NAME.append(element.text.split('\n')[5].split('= ')[1].rsplit('"',1)[0].split('"')[1].replace('\n',' ').strip())
            ADDRESS.append(element.text.split('\n')[12].replace('\n',' ').strip())
            CITY.append(element.text.split('\n')[14].split(',')[0].replace('\n',' ').strip())
            STATE.append(element.text.split('\n')[15].strip().replace('\n',' ').strip())
            ZIP_CODE.append(element.text.split('\n')[16].replace('\n',' ').strip())
    except:
        not_found.append(url)

#Dataframe creation phase
data = [STORE_NAME, ADDRESS, CITY, STATE, ZIP_CODE]
df = pd.DataFrame(data)
df = df.transpose()
df.columns = ['Name','Address', 'City', 'State', 'ZIP']

df.drop_duplicates().to_excel(downloads_directory + '//' + grocery_chain + '.xlsx', index = False)
pd.DataFrame(not_found).to_csv(downloads_directory + '//' + grocery_chain + '_not_found.csv', index = False)

print('Scraping Done')
