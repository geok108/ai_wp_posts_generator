from footballApi import FootballApi 
from datetime import datetime, timezone
import re
from ollamaHelper import OllamaHelper
from wpApi import WPApi
import re
import time

footyStatsLeagueSlug = "/spain/la-liga"
wpLeagueCategory = 1
footballData = FootballApi("140", "2024")
import os
import requests

def download_image(image_url, folder_path):
    # Get the image content from the URL
    response = requests.get(image_url)
    
    if response.status_code == 200:  # If the image is downloaded successfully
        # Create the folder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        # Extract the image name from the URL
        image_name = image_url.split("/")[-1]
        
        # Create the complete path for saving the image
        image_path = os.path.join(folder_path, "league-"+image_name)
        
        # Write the image data to a file
        with open(image_path, 'wb') as file:
            file.write(response.content)
        
        print(f"Image saved as: {image_path}")
    else:
        print(f"Failed to download image from {image_url}")


start_time = time.time()
currentRound = footballData.getCurrentRound()
print(currentRound)

currentRoundFixtures = footballData.getCurrentRoundFixtures(currentRound)
teamsStr = ""
for fixture in currentRoundFixtures["response"]:
    print("-------------FIXTURE " + fixture["teams"]["home"]["name"] + " vs " + fixture["teams"]["away"]["name"] + "-------------")
    league = fixture["league"]["name"]
    leagueLogo = fixture["league"]["logo"]
    round = fixture["league"]["round"]
    flag=fixture["league"]["flag"]
    venue = fixture['fixture']['venue']['name'] + ', ' + fixture['fixture']['venue']['city']
    referee = fixture['fixture']['referee']
    homeImage = fixture['teams']['home']['logo']
    awayImage = fixture['teams']['away']['logo']
    teamsStr = teamsStr+""","""  + fixture['teams']['home']["name"]+""",""" + fixture['teams']['away']["name"]+""",""" 

# with open('example.txt', 'w') as file:
#     file.write(teamsStr)
    # download_image(homeImage, "./badges")
    # download_image(awayImage, "./badges")
   
    download_image(leagueLogo, "./badges")
    exit()
        
    