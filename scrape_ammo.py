from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import config # AWS credentials saved in the config file

def getDriver():
   """Creates and returns the chrome headless driver."""

   DRIVER_PATH = './chromedriver'
   options = Options()
   options.add_argument('--no-sandbox')
   options.add_argument('--headless')
   options.add_argument('--disable-dev-shm-usage')
   options.add_experimental_option("excludeSwitches", ["enable-automation"])
   options.add_experimental_option('useAutomationExtension', False)
   driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
   return driver


import boto3
def sendMessage(message, cellNumbers):
   """Sends SMS to the cell numbers about the price and the sites that selling at that price.

      The chromium browser needs to be installed and chrome driver executable availabe to work.

      Parameters
      ----------
      message : str
         The message detailing the price and the sites (URLs) selling at that price. 
      cellNumbers : list
         List of cell numbers of the people who wish to ge notified about the sites with low price.
   """

   # Create an SNS client
   client = boto3.client(
      "sns",
      aws_access_key_id=config.AWS_Access_KEY,
      aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
      region_name=config.REGION_NAME
   )

   for cellNumber in cellNumbers:  
      result = client.publish(PhoneNumber = cellNumber, Message = message)
      print(result)
   return 

import time
import pandas as pd
def scrapeSite(driver, price_threshold):   
   """returns the min price and the sites that offer that price under the specificed threshold.

      The chromium browser needs to be installed and chrome driver executable availabe to work.

      Parameters
      ----------
      driver : WebDriver object
         The driver object of chrome browser
      minValue : float
         The min threshold to filter in sites (sellers) that have low price

      Returns
      -------
      list
        a string of the concatenation of min price (that meets threshold) and sites offering it
   """

   driver.get("https://ammoseek.com/ammo/9mm-luger?ca=brass")
   items = driver.find_elements(By.CLASS_NAME, 'description-link') # ammoseller
   cprs = driver.find_elements(By.ID, 'cprField') # cost per round
   prices = {} # dictionary to store price per round and the site
   for i in range(len(items)):
      site = items[i].get_attribute('href')
      price = cprs[i].text
      if price.find('$') != -1: 
         prices[site] = float(price.replace('$',''))*100 
      elif price.find('¢') != -1: 
         prices[site] = float(price.replace('¢','')) 
      print(site, price)
   driver.quit() # closing the driver
   
   min_site_price = min(prices.values()) # checking if there is a price <= threshold
   if min_site_price > price_threshold: 
      return None
   siteList = [key for key in prices if prices[key] == min_site_price]   

   df = pd.DataFrame()
   seconds = int(time.time())
   df['site'] = siteList
   df['price'] = min_site_price
   df['seconds'] = seconds
   df['updated'] = 1
   filename = "data.txt"
   with open(filename, 'a') as f:
      df.to_csv(f, mode='a', header=f.tell()==0, index=None)
   f.close()

   old_df = pd.read_csv(filename)
   old_df = old_df.groupby(['site', 'price']).agg(
      seconds = ('seconds', 'max'), updated = ('updated', 'sum')
      ).reset_index()
   old_df = old_df[(old_df['seconds'] >= (seconds - 86400))] # removing rows older than rolling 24 hours
   old_df.to_csv(filename, encoding='utf-8', index=False)
   print(old_df)
   temp = old_df[((old_df['updated'] == 1) & (old_df['seconds'] == seconds))]
   if(temp.shape[0] == 0):
      return None
   return str(min_site_price) + '¢ @ ' + str(temp.site.tolist())


import time
import pandas as pd
def updateDataStore(siteList, min_site_price):
   df = pd.DataFrame()
   seconds = int(time.time())
   df['site'] = siteList
   df['price'] = min_site_price
   df['seconds'] = seconds
   df['updated'] = 1
   filename = "data.txt"
   with open(filename, 'a') as f:
      df.to_csv(f, mode='a', header=f.tell()==0, index=None)
   f.close()

   old_df = pd.read_csv(filename)
   old_df = old_df.groupby(['site', 'price']).agg(
      seconds = ('seconds', 'max'), updated = ('updated', 'sum')
      ).reset_index()
   old_df = old_df[(old_df['seconds'] >= (seconds - 86400))] # removing rows older than rolling 24 hours
   old_df.to_csv(filename, encoding='utf-8', index=False)
   print(old_df)
   temp = old_df[((old_df['updated'] == 1) & (old_df['seconds'] == seconds))]
   if(temp.shape[0] == 0):
      return None
   return str(min_site_price) + '¢ @ ' + str(temp.site.tolist())
 






def main():
   """The main function. We may want to pass in min threshold and cell numbers as arguments here. 
      Future work: Have phonenumbers in a separate file.

   The chromium browser needs to be installed and chrome driver executable availabe to work.
   """

   siteList = scrapeSite(getDriver(), 60) #the min threshold value
   if siteList is not None:
      print(siteList)
      #sendMessage(res, ['+1phonenumber']) # list of phonenumbers
   


if __name__ == "__main__":
   main()
#   siteLst = ['https://ammoseek.com/go.to/125477048188/a', 'https://ammoseek.com/go.to/125477048192/b']
#   a = updateDataStore(siteLst, 30)
#   print(a)



