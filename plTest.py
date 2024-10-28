from footballApi import FootballApi 
from datetime import datetime
import re
from ollamaHelper import OllamaHelper
from wpApi import WPApi
import time

footballData = FootballApi()
ollama = OllamaHelper()
wpApi = WPApi()

currentRound = footballData.getCurrentRound()
print(currentRound)

currentRoundFixtures = footballData.getCurrentRoundFixtures(currentRound)
with open("promptTemplatePL.txt", 'r', encoding='utf-8') as file:
	promptTemplate = file.read()

for fixture in currentRoundFixtures["response"]:
	

	print("-------------FIXTURE " + fixture["teams"]["home"]["name"] + " vs " + fixture["teams"]["away"]["name"] + "-------------")
	
	homeTeamStanding = footballData.getTeamStanding(fixture["teams"]["home"]["id"])
	awayTeamStanding = footballData.getTeamStanding(fixture["teams"]["away"]["id"])

	date_object = datetime.fromisoformat(fixture["fixture"]["date"])

	fixtureDate = date_object.strftime("%d/%m/%Y")
	
	lastFiveGamesFormHomeTeam = footballData.getTeamStats(fixture["teams"]["home"]["id"])["response"]["form"][-5:]
	lastFiveGamesFormAwayTeam = footballData.getTeamStats(fixture["teams"]["away"]["id"])["response"]["form"][-5:]	

	homeTeamGoalsForInHome = footballData.getTeamStats(fixture["teams"]["home"]["id"])["response"]["goals"]["for"]["average"]["home"]
	homeTeamGoalsForAway = footballData.getTeamStats(fixture["teams"]["home"]["id"])["response"]["goals"]["for"]["average"]["away"]
	homeTeamGoalsAgainstInHome = footballData.getTeamStats(fixture["teams"]["home"]["id"])["response"]["goals"]["against"]["average"]["home"]
	homeTeamGoalsAgainstAway = footballData.getTeamStats(fixture["teams"]["home"]["id"])["response"]["goals"]["against"]["average"]["away"]

	awayTeamGoalsForInHome = footballData.getTeamStats(fixture["teams"]["away"]["id"])["response"]["goals"]["for"]["average"]["home"]
	awayTeamGoalsForAway = footballData.getTeamStats(fixture["teams"]["away"]["id"])["response"]["goals"]["for"]["average"]["away"]
	awayTeamGoalsAgainstInHome = footballData.getTeamStats(fixture["teams"]["away"]["id"])["response"]["goals"]["against"]["average"]["home"]
	awayTeamGoalsAgainstAway = footballData.getTeamStats(fixture["teams"]["away"]["id"])["response"]["goals"]["against"]["average"]["away"]
	
	h2h = footballData.getHeadToHead(fixture["teams"]["home"]["id"], fixture["teams"]["away"]["id"])
	homeTeamWins = 0
	awayTeamWins = 0
	drawsCount = 0
	for h2hFixture in h2h["response"]:	
		if(fixture["teams"]["home"]["name"] == h2hFixture["teams"]["home"]["name"] and h2hFixture["teams"]["home"]["winner"]):
			homeTeamWins+=1
		if(fixture["teams"]["home"]["name"] == h2hFixture["teams"]["home"]["name"] and h2hFixture["teams"]["home"]["winner"] is None):
			drawsCount+=1
		if(fixture["teams"]["home"]["name"] == h2hFixture["teams"]["away"]["name"] and h2hFixture["teams"]["away"]["winner"]):
			homeTeamWins+=1	
		if(fixture["teams"]["away"]["name"] == h2hFixture["teams"]["home"]["name"] and h2hFixture["teams"]["home"]["winner"]):
			awayTeamWins+=1
		if(fixture["teams"]["away"]["name"] == h2hFixture["teams"]["home"]["name"] and h2hFixture["teams"]["home"]["winner"] is None):
			drawsCount+=1
		if(fixture["teams"]["away"]["name"] == h2hFixture["teams"]["away"]["name"] and h2hFixture["teams"]["away"]["winner"]):
			awayTeamWins+=1	

	xGData = footballData.getXG()
	homeTeamPlayers = footballData.getPlayersStatsByTeam(fixture["teams"]["home"]["id"])
	homeTeamFilteredPlayers = {name: player for name, player in homeTeamPlayers.items() if player["games"]["rating"] is not None}
	homeTeamSortedPlayersBasedOnMinutes = dict(sorted(homeTeamFilteredPlayers.items(), key=lambda item: item[1]["games"]["minutes"], reverse=True)[:15])
	homeTeamSortedPlayersBasedOnRating = dict(sorted(homeTeamSortedPlayersBasedOnMinutes.items(), key=lambda item: item[1]["games"]["rating"], reverse=True)[:5])
	homeTeamXG = xGData[fixture["teams"]["home"]["name"]]

	awayTeamPlayers = footballData.getPlayersStatsByTeam(fixture["teams"]["away"]["id"])
	awayTeamFilteredPlayers = {name: player for name, player in awayTeamPlayers.items() if player["games"]["rating"] is not None}
	awayTeamSortedPlayersBasedOnMinutes = dict(sorted(awayTeamFilteredPlayers.items(), key=lambda item: item[1]["games"]["minutes"], reverse=True)[:15])
	awayTeamSortedPlayersBasedOnRating = dict(sorted(awayTeamSortedPlayersBasedOnMinutes.items(), key=lambda item: item[1]["games"]["rating"], reverse=True)[:5])
	absences = footballData.getInjuriesByFixture(fixture["fixture"]["id"])
	if(absences["results"] > 0):
		homeTeamAbsences = [item for item in absences["response"] if item['team']['id'] == fixture["teams"]["home"]["id"]]
		awayTeamAbsences = [item for item in absences["response"] if item['team']['id'] == fixture["teams"]["away"]["id"]]
	awayTeamXG = xGData[fixture["teams"]["away"]["name"]]

	# prepare prompt template
	placeholders = {
		"{homeTeam}": fixture["teams"]["home"]["name"],
		"{awayTeam}": fixture["teams"]["away"]["name"],
		"{homeTeamRank}": str(homeTeamStanding["rank"]),
		"{homeTeamPoints}": str(homeTeamStanding["points"]),
		"{homeTeamRankStatus}": str(homeTeamStanding["status"]),
		"{awayTeamRank}": str(awayTeamStanding["rank"]),
		"{awayTeamPoints}": str(awayTeamStanding["points"]),
		"{awayTeamRankStatus}": str(awayTeamStanding["status"]),
		"{head2head}": fixture["teams"]["home"]["name"] + " wins: " 
								 + str(homeTeamWins) + ", " + fixture["teams"]["away"]["name"] + " wins: " + str(awayTeamWins)
								 + ", draws: " + str(drawsCount),
		"{homeTeamForm}": lastFiveGamesFormHomeTeam,
		"{awayTeamForm}": lastFiveGamesFormAwayTeam,
		"{homeTeamGoalsStats}": "goals scored in home " + homeTeamGoalsForInHome + ", goals scored away " + homeTeamGoalsForAway
								+ ", goals against in home" + homeTeamGoalsAgainstInHome + ", goals against away " + homeTeamGoalsAgainstAway,
		"{awayTeamGoalsStats}": "goals scored in home " + awayTeamGoalsForInHome + ", goals scored away " + awayTeamGoalsForAway
								+ ", goals against in home" + awayTeamGoalsAgainstInHome + ", goals against away " + awayTeamGoalsAgainstAway,
		"{homeXG}": homeTeamXG,
		"{awayXG}": awayTeamXG,
	}
	
	for key, value in placeholders.items():
		promptTemplate = re.sub(key, value, promptTemplate)

		promptTemplate.replace("{homeTeam}", fixture["teams"]["home"]["name"])
		promptTemplate.replace("{awayTeam}", fixture["teams"]["away"]["name"])
		promptTemplate.replace("{head2head}", fixture["teams"]["home"]["name"] + " wins: " 
									+ str(homeTeamWins) + ", " + fixture["teams"]["away"]["name"] + " wins: " + str(awayTeamWins)
									+ ", draws: " + str(drawsCount))	
		promptTemplate.replace("{homeTeamForm}", lastFiveGamesFormHomeTeam)
		promptTemplate.replace("{awayTeamForm}", lastFiveGamesFormAwayTeam)
	
	res = ollama.ChatOllama(promptTemplate)
	postTitle = fixture["teams"]["home"]["name"] + " - " + fixture["teams"]["away"]["name"] + " " + fixtureDate + " Prediction"
	# print("CREATING WP POST...")
	# wpApi.createPost(postTitle, res)
	# print("WP POST CREATED")