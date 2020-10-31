import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import boto3
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
   
   # checking if there is a price <= threshold
   min_site_price = min(prices.values()) 
   if min_site_price > price_threshold: 
      return None
   siteList = [key for key in prices if prices[key] == min_site_price]   

   # Appending the list of sites that beat the threshold to our data file
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

   # Updating data file 1) update seconds of site to reflect the most recent time 2) update 'updated' to times same site has been shown 3) remove sites older than 24 hours
   df = pd.read_csv(filename)
   df = df.groupby(['site', 'price']).agg(
      seconds = ('seconds', 'max'), updated = ('updated', 'sum')
      ).reset_index()
   df = df[(df['seconds'] >= (seconds - 86400))] # removing rows older than rolling 24 hours
   df.to_csv(filename, encoding='utf-8', index=False)
   temp = df[((df['updated'] == 1) & (df['seconds'] == seconds))] # filtering sites who are updated only once (i.e. only added) and done most recently
   if(temp.shape[0] == 0):
      return None
   return str(min_site_price) + '¢ @ ' + str(temp.site.tolist())


def main():
   """The main function. We may want to pass in min threshold and cell numbers as arguments here. 
      Future work: Have phonenumbers in a separate file.

   The chromium browser needs to be installed and chrome driver executable availabe to work.
   """

   site_list_message = scrapeSite(getDriver(), 30) #the min threshold value
   if site_list_message is not None:
      print(site_list_message)
      sendMessage(site_list_message, config.cell_numbers_list) # list of phonenumbers
   
if __name__ == "__main__":
   while(True):
      main()
      time.sleep(random.randint(5,20)*60) # wait time before next method call; randomly between 5 - 20 mins
