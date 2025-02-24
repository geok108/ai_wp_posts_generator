import json
import requests
import os
from bs4 import BeautifulSoup

class FootballApi:
    def __init__(self, league, season, local = False):
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
        self.headers = {
            "X-RapidAPI-Key": config["rapidApiKey"],
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }

        self.baseUrl = "https://api-football-v1.p.rapidapi.com/v3"
        self.league = league
        self.season = season
        self.local = local

    def getCurrentRound(self):
        if self.local and os.path.exists("currentRound.json"):
            with open("currentRound.json", 'r') as file:
                currentRound = json.load(file)["response"][0]
                return currentRound
            
        #get current round
        currentRoundUrl = self.baseUrl + "/fixtures/rounds"

        currentRoundQuerystring = {"league":self.league,"season":self.season,"current":"true"}

        currentRoundResponse = requests.get(currentRoundUrl, headers=self.headers, params=currentRoundQuerystring)

        currentRound = currentRoundResponse.json()
        
        # The file path where you want to save the JSON file
        currRoundPath = "currentRound.json"

        # Write the JSON data to a file
        with open(currRoundPath, 'w') as file:
            json.dump(currentRound, file)

        return currentRound["response"][0]

    def getCurrentRoundFixtures(self, currentRound):
        if self.local and os.path.exists("currentRoundFixtures.json"):
            with open("currentRoundFixtures.json", 'r') as file:
                currentRoundFixtures = json.load(file)
                return currentRoundFixtures

        #get current round fixtures
        url = self.baseUrl + "/fixtures"
    
        querystring = {"league":self.league,"season":self.season,"round":currentRound}

        response = requests.get(url, headers=self.headers, params=querystring)
        fixtures = response.json()

        # The file path where you want to save the JSON file
        currRoundFixturesPath = "currentRoundFixtures.json"

        # Write the JSON data to a file
        with open(currRoundFixturesPath, 'w') as file:
            json.dump(fixtures, file)

        return fixtures

    def getHeadToHead(self, home, away):

        url = self.baseUrl + "/fixtures/headtohead"

        querystring = {"h2h":str(home)+"-"+str(away)}

        response = requests.get(url, headers=self.headers, params=querystring)

        return response.json()

    def getInjuriesByFixture(self, fixture):
        if self.local and os.path.exists("injuries.json"):
            with open("injuries.json", 'r') as file:
                playerInjuries = json.load(file)
                return playerInjuries
            
        url = self.baseUrl + "/injuries"

        querystring = {"fixture": fixture}

        injuries = requests.get(url, headers=self.headers, params=querystring).json()
        # The file path where you want to save the JSON file
        injuriesPath = "injuries.json"

        # Write the JSON data to a file
        with open(injuriesPath, 'w') as file:
            json.dump(injuries, file)
        return injuries
    
    def getOdds(self, fixtureId):
        url = self.baseUrl + "/odds"

        querystring = {"fixture": fixtureId}

        odds = requests.get(url, headers=self.headers, params=querystring).json()

        return odds["response"]

    def getTeamStats(self, teamId):
        if self.local and os.path.exists("teamStats.json"):
            with open("teamStats.json", 'r') as file:
                teamStats = json.load(file)
                return teamStats
        url = self.baseUrl + "/teams/statistics"

        querystring = {"league":self.league,"season":self.season,"team":str(teamId)}

        stats = requests.get(url, headers=self.headers, params=querystring).json()

        # The file path where you want to save the JSON file
        teamStatsPath = "teamStats.json"

        # Write the JSON data to a file
        with open(teamStatsPath, 'w') as file:
            json.dump(stats, file)
        return stats
    
    def getTeamStanding(self, teamId=None):
        if self.local and os.path.exists("standings.json"):
            with open("standings.json", 'r') as file:
                standings = json.load(file)
                if(teamId is not None):
                    return self.findTeamStanding(standings, int(teamId))
                return standings
        url = self.baseUrl + "/standings"

        # querystring = {"season":"2024","league":"39", "team":str(teamId)}
        querystring = {"league":self.league, "season":self.season}

        standings = requests.get(url, headers=self.headers, params=querystring).json()["response"][0]["league"]["standings"][0]
      
        # The file path where you want to save the JSON file
        standingsPath = "standings.json"

        # Write the JSON data to a file
        with open(standingsPath, 'w') as file:
            json.dump(standings, file)

        if(teamId is not None):
            return self.findTeamStanding(standings, int(teamId))
        return standings
    
    def getPlayersStatsByTeam(self, teamId):
        url = self.baseUrl + "/players"

        querystring = {"league":self.league,"season":self.season, "team": teamId}

        response = requests.get(url, headers=self.headers, params=querystring).json()
        results = []
        for player in response["response"]:
            results.append(player)
        for i in range(2, response["paging"]["total"]+1):
           
            querystring = {"league":self.league,"season":self.season, "team": teamId, "page": str(i)}
            response = requests.get(url, headers=self.headers, params=querystring).json()
            for player in response["response"]:
                results.append(player)
        return results
    
    def getSidelinedPlayer(self, playerId):
        url = self.baseUrl + "/sidelined"

        querystring = {"player": playerId}

        response = requests.get(url, headers=self.headers, params=querystring).json()
     
        return response
    
    def getSlug(self, leagueId):
        switcher = {
            "39": "/england/premier-league",
            "140": "/spain/la-liga",
            "135": "/italy/serie-a",
            "78": "/germany/bundesliga",
            "525": "/europe/uefa-champions-league",
            "61": "/france/ligue-1",
            "2":"/europe/uefa-champions-league"
        }

        return switcher.get(leagueId, "")
    
    def getXG(self, leagueId):
        # URL of the webpage to scrape
        url = "https://footystats.org" + self.getSlug(leagueId) + "/xg"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Send a GET request
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            # Parse the content with BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")
            
            table = soup.find('table', class_='xg-all')
     
            results = {}
            if table:
                # Extract team names and xG values
                teams = table.find_all('td', class_='detailed-stats-team-name-size')   # Assuming team names are in <span class="team-name">
                xg_values = table.find_all('td', class_='green')  # Assuming xG values are in <td class="xg-value">
                
                # Ensure the number of teams matches the number of xG values
                if len(teams) == len(xg_values):
                    for team, xg in zip(teams, xg_values):
                        # with open("team_names.txt", "a") as file:
                        #     file.write(f'"{team.find('a').next}": "",\n')
                        
                        team_name = self.getTeamShortName(team.find('a').next)
                        # team_name = team.find('a').next

                        xg_number = xg.get_text().strip()
                        print(f"Team: {team_name}, xG: {xg_number}")
                        if xg_number:
                            
                            results[team_name] = xg_number
                        else:
                            results[team_name] = "Not found"  # Store a default value if xG is not found
                
                else:
                    print("Mismatch between teams and xG values.")
                return results
            else:
                print("Table with the specified class not found.")
        else:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

    def getFixturePredictions(self, fixture):
        if self.local and os.path.exists("predictions.json"):
            with open("predictions.json", 'r') as file:
                standings = json.load(file)
                return standings
        url = self.baseUrl + "/predictions"

        # querystring = {"season":"2024","league":"39", "team":str(teamId)}
        querystring = {"fixture": fixture}

        fixturePredictions = requests.get(url, headers=self.headers, params=querystring).json()
      
        # The file path where you want to save the JSON file
        predictionsPath = "predictions.json"

        # Write the JSON data to a file
        with open(predictionsPath, 'w') as file:
            json.dump(fixturePredictions, file)

        return fixturePredictions

    def getTeamShortName(self, fullname):
        switcher = {
            "Manchester City FC": "Manchester City",
            "Tottenham Hotspur FC": "Tottenham",
            "Arsenal FC": "Arsenal",
            "Liverpool FC": "Liverpool",
            "Manchester United FC": "Manchester United",
            "Chelsea FC": "Chelsea",
            "AFC Bournemouth": "Bournemouth",
            "Brighton & Hove Albion FC": "Brighton",
            "West Ham United FC": "West Ham",
            "Fulham FC": "Fulham",
            "Nottingham Forest FC": "Nottingham Forest",
            "Brentford FC": "Brentford",
            "Crystal Palace FC": "Crystal Palace",
            "Aston Villa FC": "Aston Villa",
            "Newcastle United FC": "Newcastle",
            "Everton FC": "Everton",
            "Wolverhampton Wanderers FC": "Wolves",
            "Southampton FC": "Southampton",
            "Leicester City FC": "Leicester",
            "Ipswich Town FC": "Ipswich",
            "Venezia FC": "Venezia" ,
            "Empoli FC":"Empoli",
            "ACF Fiorentina": "Fiorentina" , 
            "SSC Napoli": "Napoli",
            "Hellas Verona FC": "Verona" , 
            "Udinese Calcio": "Udinese",
            "SS Monza 1912": "Monza" , 
            "Cagliari Calcio": "Cagliari",
            "US Lecce": "Lecce" , 
            "Genoa CFC": "Genoa",
            "Torino FC": "Torino" , 
            "Parma Calcio 1913": "Parma",
            "AS Roma": "AS Roma" , 
            "SS Lazio": "Lazio",
            "Calcio Como": "Como" , 
            "AC Milan": "AC Milan",
            "Atalanta Bergamasca Calcio": "Atalanta" , 
            "Juventus FC": "Juventus",
            "FC Internazionale Milano":"Inter" , 
            "Bologna FC 1909": "Bologna",
            "Deportivo Alavés" : "Alaves",
            "Real Club Deportivo Mallorca" : "Mallorca",
            "CA Osasuna" : "Osasuna",
            "Real Valladolid Club de Fútbol" : "Valladolid",
            "Girona FC" : "Girona",
            "CD Leganés" : "Leganes",
            "Club Atlético de Madrid" : "Atletico Madrid",
            "UD Las Palmas" : "Las Palmas",
            "FC Barcelona" : "Barcelona",
            "Reial Club Deportiu Espanyol" : "Espanyol",
            "Sevilla FC" : "Sevilla",
            "Real Sociedad de Fútbol" : "Real Sociedad",
            "Athletic Club Bilbao" : "Athletic Club",
            "Real Betis Balompié" : "Real Betis",
            "Real Club Celta de Vigo" : "Celta Vigo",
            "Getafe Club de Fútbol" : "Getafe",
            "Villarreal CF" : "Villarreal",
            "Rayo Vallecano" : "Rayo Vallecano",
            "Valencia CF" : "Valencia",
            "Real Madrid CF" : "Real Madrid",
            "BVB 09 Borussia Dortmund": "Borussia Dortmund",
            "Bayer 04 Leverkusen": "Bayer Leverkusen",
            "SC Freiburg": "SC Freiburg",
            "Kieler SV Holstein 1900": "Holstein Kiel",
            "1. FSV Mainz 05": "FSV Mainz 05",
            "VfL Bochum 1848": "VfL Bochum",
            "TSG 1899 Hoffenheim": "1899 Hoffenheim",
            "VfL Wolfsburg": "VfL Wolfsburg",
            "1. FC Heidenheim 1846": "1. FC Heidenheim",
            "1. FC Union Berlin": "Union Berlin",
            "FC St. Pauli": "FC St. Pauli",
            "Eintracht Frankfurt": "Eintracht Frankfurt",
            "Borussia VfL Mönchengladbach": "Borussia Mönchengladbach",
            "FC Bayern München": "Bayern München",
            "Rasen Ballsport Leipzig": "RB Leipzig",
            "SV Werder Bremen": "Werder Bremen",
            "FC Augsburg": "FC Augsburg",
            "VfB Stuttgart 1893": "VfB Stuttgart",
            "Paris Saint-Germain FC": "Paris Saint Germain",
            "Olympique Lyonnais": "Lyon",
            "Racing Club de Lens": "Lens",
            "OGC Nice Côte d'Azur": "Nice",
            "AS Monaco FC": "Monaco",
            "Lille OSC Métropole": "Lille",
            "Stade Brestois 29": "Stade Brestois 29",
            "Olympique de Marseille": "Marseille",
            "Stade Rennais FC": "Rennes",
            "Montpellier HSC": "Montpellier",
            "Toulouse FC": "Toulouse",
            "FC Nantes": "Nantes",
            "Stade de Reims": "Reims",
            "Association Jeunesse Auxerroise": "Auxerre",
            "RC Strasbourg Alsace": "Strasbourg",
            "AS Saint-Étienne": "Saint Etienne",
            "Angers Sporting Club de l'Ouest": "Angers",
            "Le Havre AC": "LE Havre"
        }
        return switcher.get(fullname, "")
        
    # Function to find a field by id
    def findTeamStanding(self, standings, teamId):
        for item in standings:
            if item["team"]["id"] == teamId:
                return item
        return None