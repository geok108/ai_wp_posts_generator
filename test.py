from footballApi import FootballApi 
from openai import OpenAI
from wpApi import WPApi
from datetime import datetime
import re

footballData = FootballApi()
client = OpenAI()
wpApi = WPApi()

teamsDict = {
	"Pafos": "Πάφος",
	"Aris": "Άρης",
	"Anorthosis": "Ανόρθωσις",
	"Omonoia Nicosia": "Ομόνοια",
	"AE Zakakiou": "ΑΕΖ",
	"Doxa": "Δόξα",
	"Ethnikos Achna": "Εθνικός Άχνας",
	"Nea Salamis": "Νέα Σαλαμίνα",
	"Karmiotissa": "Καρμιώτησσα",
	"Apollon Limassol": "Απόλλων",
	"Apoel Nicosia": "ΑΠΟΕΛ",
	"AEK Larnaca": "ΑΕΚ",
	"Othellos": "Οθέλλος",
	"AEL": "ΑΕΛ"
}
currentRound = footballData.getCurrentRound(True)
print(currentRound)

currentRoundFixtures = footballData.getCurrentRoundFixtures(currentRound)
with open("promptTemplate.txt", 'r', encoding='utf-8') as file:
	promptTemplate = file.read()

for fixture in currentRoundFixtures["response"]:
	print("-------------FIXTURE " + fixture["teams"]["home"]["name"] + " vs " + fixture["teams"]["away"]["name"] + "-------------")
	
	homeTeamStanding = footballData.getTeamStanding(fixture["teams"]["home"]["id"])["response"][0]["league"]["standings"][0][0]
	awayTeamStanding = footballData.getTeamStanding(fixture["teams"]["away"]["id"])["response"][0]["league"]["standings"][0][0]

	date_object = datetime.fromisoformat(fixture["fixture"]["date"])

	fixtureDate = date_object.strftime("%d/%m/%Y")
	
	lastFiveGamesFormHomeTeam = footballData.getTeamStats(fixture["teams"]["home"]["id"])["response"]["form"][-5:]
	lastFiveGamesFormAwayTeam = footballData.getTeamStats(fixture["teams"]["away"]["id"])["response"]["form"][-5:]
	# print("---HOME TEAM STATS---")
	

	homeTeamGoalsForInHome = footballData.getTeamStats(fixture["teams"]["home"]["id"])["response"]["goals"]["for"]["average"]["home"]
	homeTeamGoalsForAway = footballData.getTeamStats(fixture["teams"]["home"]["id"])["response"]["goals"]["for"]["average"]["away"]
	homeTeamGoalsAgainstInHome = footballData.getTeamStats(fixture["teams"]["home"]["id"])["response"]["goals"]["against"]["average"]["home"]
	homeTeamGoalsAgainstAway = footballData.getTeamStats(fixture["teams"]["home"]["id"])["response"]["goals"]["against"]["average"]["away"]
	# print("homeTeam goals for in home " + homeTeamGoalsForInHome)
	# print("homeTeam goals for away " + homeTeamGoalsForAway)
	# print("homeTeam goals against in home " + homeTeamGoalsAgainstInHome)
	# print("homeTeam goals against in away " + homeTeamGoalsAgainstAway)

	# print("---AWAY TEAM STATS---")
	awayTeamGoalsForInHome = footballData.getTeamStats(fixture["teams"]["away"]["id"])["response"]["goals"]["for"]["average"]["home"]
	awayTeamGoalsForAway = footballData.getTeamStats(fixture["teams"]["away"]["id"])["response"]["goals"]["for"]["average"]["away"]
	awayTeamGoalsAgainstInHome = footballData.getTeamStats(fixture["teams"]["away"]["id"])["response"]["goals"]["against"]["average"]["home"]
	awayTeamGoalsAgainstAway = footballData.getTeamStats(fixture["teams"]["away"]["id"])["response"]["goals"]["against"]["average"]["away"]
	# print("awayTeam goals for in home " + awayTeamGoalsForInHome)
	# print("awayTeam goals for away " + awayTeamGoalsForAway)
	# print("awayTeam goals against in home " + awayTeamGoalsAgainstInHome)
	# print("awayTeam goals against in away " + awayTeamGoalsAgainstAway)

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

	# prepare prompt template
	placeholders = {
		"{homeTeam}": teamsDict[fixture["teams"]["home"]["name"]],
		"{awayTeam}": teamsDict[fixture["teams"]["away"]["name"]],
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
								+ ", goals against in home" + awayTeamGoalsAgainstInHome + ", goals against away " + awayTeamGoalsAgainstAway
	}
	
	for key, value in placeholders.items():
  	  promptTemplate = re.sub(key, value, promptTemplate)

	# promptTemplate.replace("{homeTeam}", fixture["teams"]["home"]["name"])
	# promptTemplate.replace("{awayTeam}", fixture["teams"]["away"]["name"])
	# promptTemplate.replace("{head2head}", fixture["teams"]["home"]["name"] + " wins: " 
	# 							 + str(homeTeamWins) + ", " + fixture["teams"]["away"]["name"] + " wins: " + str(awayTeamWins)
	# 							 + ", draws: " + str(drawsCount))	
	# promptTemplate.replace("{homeTeamForm}", lastFiveGamesFormHomeTeam)
	# promptTemplate.replace("{awayTeamForm}", lastFiveGamesFormAwayTeam)

	print("CHAT GPT PROMPT: " + promptTemplate)
	break
	# chatgpt endpoint call
	print("GENERATING ARTICLE...")
	completion = client.chat.completions.create(
	model="gpt-3.5-turbo",
	messages=[
		{"role": "system", "content": promptTemplate}  ]
	)
	print("ARTICLE GENERATED")

	postTitle = teamsDict[fixture["teams"]["home"]["name"]] + " - " + teamsDict[fixture["teams"]["away"]["name"]] + " " + fixtureDate + " Πρόβλεψη"
	print("CREATING WP POST...")
	wpApi.createPost(postTitle, completion.choices[0].message.content)
	print("WP POST CREATED")
