# amcheck

This is a project to show how selenium can be used as a reliable way to get data from a website and some action be taken
based on results. The website used for exampliying is an ammunition deals aggregated and the goal is to get the price per
round offered by the various sellers and identify the sellers that are offering the price lower or equal to the price per 
round threshold specified. 

If there are sellers idenfied who are offering a price lower than the threshold specified, pick the ones with the lowest 
price and send a SMS notification. 

Note: 
1. The chrome driver matching the chrome browser should be kept in the directory (where the python file resides). THe 
chrome driver can be downloaded from https://chromedriver.chromium.org/downloads.
2. This program is for demonstration purpose only. Check with the website for any t&c.
