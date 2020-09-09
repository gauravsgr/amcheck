from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import config 

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


def scrapeSite(driver, minValue):
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
   prices = {}
   items = driver.find_elements(By.ID, 'cprField')
   for item in items:
      site = item.get_attribute('onclick')
      price = item.text
      site = site.replace("window.open('", '')
      site = site.replace("');", '')
      site = "http://ammoseek.com" + site
      if price.find('$') != -1: 
         prices[site] = float(price.replace('$',''))*100 
      elif item.text.find('¢') != -1: 
         prices[site] = float(price.replace('¢','')) 
      print(price, site)
   driver.quit() # closing the driver

   temp = min(prices.values()) # checking if there is a price <= threshold
   if temp > minValue: 
      return None
   res = [key for key in prices if prices[key] == temp]     
   return (str(temp) + '¢ @ ' + str(res))


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


def main():
   """The main function. We may want to pass in min threshold and cell numbers as arguments here. 
      Future work: Have phonenumbers in a separate file.

   The chromium browser needs to be installed and chrome driver executable availabe to work.
   """

   res = scrapeSite(getDriver(), 70) #the min threshold value
   if res is not None:
      print(res)
      sendMessage(res, ['+1phonenumber']) # list of phonenumbers


if __name__ == "__main__":
   main()
   