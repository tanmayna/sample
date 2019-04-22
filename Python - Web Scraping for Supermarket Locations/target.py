'''
WEB SCRAPING USING SELENIUM

This code returns an Excel file with all Target stores in the vicinity of the top 5 cities in New York State.
This code can be used to return all Target stores in the US by modifying line 13.
A csv file with cities in which there was an error returning the stores is also returned for debugging purposes.
'''

from auxiliary import *
grocery_chain = 'Target'

#Creating a Selenium WebDriver
driver = create_driver(downloads_directory, r'https://www.target.com')

#Zipcodes or Cities to loop over for a store
cities_list = [i for i in top_cities(top=5) if i.rsplit(',')[1]=='ny']

#Creating empty lists
store_name = list()
store_address = list()
store_city = list()
store_state = list()
store_zip = list()
not_found = list()

for specific_city in cities_list:
    #Looping through all cities

    print(specific_city)
    try:
        driver.get('https://www.target.com/store-locator/find-stores/' + specific_city)
        time.sleep(wait_time*1.5)
        
        #Just change the value of these variables as desired per website
        store_elements = list()
        for element in driver.find_elements_by_class_name('h-padding-b-default'):
            store_elements.append(element)

        '''
        Getting store name, address, city, state, and ZIP code.

        If there is an issue with a specific store, the code skips over that store as there are try-except blocks for each line.
        This ensures that the code doesn't get interrupted.
        '''
        for i in store_elements:
            specific_store = i.text.split('\n')
            try:
                store_name.append(specific_store[0].replace('\n',' ').strip())
            except:
                store_name.append(None)

            try:
                store_address.append(specific_store[1].rsplit(',',2)[0].replace('\n',' ').strip())
            except:
                store_address.append(None)

            try:
                store_city.append(specific_store[1].rsplit(',',2)[1].replace('\n',' ').strip())
            except:
                store_city.append(None)

            try:
                store_state.append(specific_store[1].rsplit(',',2)[2].strip().split(' ',1)[0].replace('\n',' ').strip())
            except:
                store_state.append(None)

            try:
                store_zip.append(specific_store[1].rsplit(',',2)[2].strip().split(' ',1)[1].replace('\n',' ').strip())
            except:
                store_zip.append(None)
    except:
        #Cities in which there was an error are stored in this list and returned as a CSV file
        not_found.append(specific_city)

#Dataframe creation phase
data = [store_name, store_address, store_city, store_state, store_zip]
df = pd.DataFrame(data)
df = df.transpose()
df.columns = ['Name','Address', 'City', 'State', 'ZIP']

df.drop_duplicates().to_excel(downloads_directory + '//' + grocery_chain + '.xlsx', index = False)
pd.DataFrame(not_found).to_csv(downloads_directory + '//' + grocery_chain + '_not_found.csv', index = False)

print('Scraping Done')
