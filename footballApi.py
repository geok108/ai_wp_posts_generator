import json
import requests
import os

class FootballApi:
    def __init__(self):
        self.headers = {
            "X-RapidAPI-Key": "8f66ce5ebfmsh4588389513cdc5cp148ac5jsn8cc2bf891041",
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }

    def getCurrentRound(self, local=False):
        if local and os.path.exists("currentRound.json"):
            with open("currentRound.json", 'r') as file:
                currentRound = json.load(file)["response"][0]
                return currentRound
            
        #get current round
        currentRoundUrl = "https://api-football-v1.p.rapidapi.com/v3/fixtures/rounds"

        currentRoundQuerystring = {"league":"318","season":"2023","current":"true"}

        currentRoundResponse = requests.get(currentRoundUrl, headers=self.headers, params=currentRoundQuerystring)

        currentRound = currentRoundResponse.json()
        
        # The file path where you want to save the JSON file
        currRoundPath = "currentRound.json"

        # Write the JSON data to a file
        with open(currRoundPath, 'w') as file:
            json.dump(currentRound, file)

        return currentRound["response"][0]

    def getCurrentRoundFixtures(self, currentRound, local=False):
        if local and os.path.exists("currentRoundFixtures.json"):
            with open("currentRoundFixtures.json", 'r') as file:
                currentRoundFixtures = json.load(file)
                return currentRoundFixtures

        #get current round fixtures
        url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    
        querystring = {"league":"318","season":"2023","round":currentRound}

        response = requests.get(url, headers=self.headers, params=querystring)
        fixtures = response.json()

        # The file path where you want to save the JSON file
        currRoundFixturesPath = "currentRoundFixtures.json"

        # Write the JSON data to a file
        with open(currRoundFixturesPath, 'w') as file:
            json.dump(fixtures, file)

        return fixtures

    def getHeadToHead(self, home, away):

        url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/headtohead"

        querystring = {"h2h":str(home)+"-"+str(away)}

        response = requests.get(url, headers=self.headers, params=querystring)

        return response.json()

    def getInjuriesByFixture(self, fixture):
        url = "https://api-football-v1.p.rapidapi.com/v3/injuries"

        querystring = {"fixture":str(fixture)}

        response = requests.get(url, headers=self.headers, params=querystring)

        return response.json()

    def getTeamStats(self, teamId):

        url = "https://api-football-v1.p.rapidapi.com/v3/teams/statistics"

        querystring = {"league":"318","season":"2023","team":str(teamId)}

        response = requests.get(url, headers=self.headers, params=querystring)

        return(response.json())
    
    def getTeamStanding(self, teamId):
        url = "https://api-football-v1.p.rapidapi.com/v3/standings"

        querystring = {"season":"2023","league":"318", "team":str(teamId)}

        headers = {
            "X-RapidAPI-Key": "8f66ce5ebfmsh4588389513cdc5cp148ac5jsn8cc2bf891041",
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)

        return response.json()