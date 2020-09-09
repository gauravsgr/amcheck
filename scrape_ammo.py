from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import config 

def getDriver():
   DRIVER_PATH = '/home/gaurav/Desktop/sample/chromedriver'
   options = Options()
   options.add_argument('--no-sandbox')
   options.add_argument('--headless')
   options.add_argument('--disable-dev-shm-usage')
   options.add_experimental_option("excludeSwitches", ["enable-automation"])
   options.add_experimental_option('useAutomationExtension', False)
   driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
   return driver


def scrapeSite(driver, minValue):
   driver.get("https://ammoseek.com/ammo/9mm-luger?ca=brass")
   print("Hello")
   print(driver.page_source)
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
   driver.quit()
   print("Hello again")
   temp = min(prices.values()) 
   if temp > minValue: 
      return None
   res = [key for key in prices if prices[key] == temp] 
   # printing result  
   print("Keys with minimum values are : " + str(res)) 
   return (str(temp) + '¢ @ ' + str(res))


import boto3
def sendMessage(message, cellNumbers):
   # Create an SNS client
   client = boto3.client(
      "sns",
      aws_access_key_id=config.AWS_Access_KEY,
      aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
      region_name=config.REGION_NAME
   )

   for cellNumber in cellNumbers:  
      # Send your sms message.
      result = client.publish(
         PhoneNumber = cellNumber,
         Message = message
      )
      print(result)
   return 


def main():
   res = scrapeSite(getDriver(), 70) #the min threshold value
   if res is not None:
      print(res)
      sendMessage(res, ['+1phonenumber']) # list of phonenumbers


if __name__ == "__main__":
   main()


