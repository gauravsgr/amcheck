# amcheck

This is a project to show how selenium can be used as a reliable way to get data from a website and some action be taken
based on results. The website used for exampliying is an ammunition deals aggregated and the goal is to get the price per
round offered by the various sellers and identify the sellers that are offering the price lower or equal to the price per 
round threshold specified. 

If there are sellers idenfied who are offering a price lower than the threshold specified, pick the ones with the lowest 
price and send a SMS notification. 

Note: 
1. The chrome driver matching the chrome browser should be kept in the directory (where the python file resides). The 
chrome driver can be downloaded from https://chromedriver.chromium.org/downloads.
2. This app is for demonstration purpose only. Refer to the website t&c.
3. This app can also be run in docker. Preferred mode if you want to run the application as it. Docker installs both chrome and chromedriver (and a webapp if you use docker-compose). If docker-compose is used, the data.txt log can be accessed through the flask app at http://localhost:8888/data. (change with IP address if running on a remote/cloud host). Alternatively you can bash in the scraper container and check the logs at /tmp/data.txt.
4. This repo is under automated build at docker hub. Images can be downloaded directly instead of building it. 
General docker commands are:

[A1] Build docker Image by going (cd) into app directory
* docker build -t ammscraper .

[A2] Run docker image in container in interactive mode
* docker run --rm -it ammscraper
* python3 scrape_ammo.py

OR Run docker image in detached mode

* docker run -d ammscraper 
* docker logs <continerid>

[B1] Build and run docker containers (flask web-app and scraper app) using docker-compose
* docker-compose up -d 

[B2] Build and run docker containers (flask web-app and scraper app) using docker-compose
* docker exec -it <container name> bash

[B2] Command to shutdown all docker-compose containers 
* docker-compose down

[C] Command to clean up all containers
* docker system prune -a

[D] Command to list all volumes (data attached to containers)
* docker volume ls

[D] Command to remove a volume (data attached to containers)
* docker volume rm <volume name>
  
[E] List docker images
* docker images  
  
[F] List docker containers
* docker ps

[G] Kill docker container
* docker kill <container id>
  
  



