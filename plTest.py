from footballApi import FootballApi 
from datetime import datetime, timezone
import re
from ollamaHelper import OllamaHelper
from wpApi import WPApi
import re
import time

footballData = FootballApi("39", "2024")
ollama = OllamaHelper()
wpApi = WPApi()

def isSidelined(playerId, fixtureDate):
	sidelinedPlayer = footballData.getSidelinedPlayer(playerId)
	absenceEndDate = None if sidelinedPlayer["results"] == 0 or sidelinedPlayer["response"][0]["end"] is None else datetime.strptime(sidelinedPlayer["response"][0]["end"], "%Y-%m-%d")
	fixtureDate = datetime.strptime(fixtureDate, "%Y-%m-%d")

	if(absenceEndDate is None or absenceEndDate > fixtureDate):
		return True
	
	return False

def getCategories(leagues):
	leagueIdsDict = {'Premier League': 1}
	leagueIds = [leagueIdsDict[key] for key in leagues if key in leagueIdsDict]
	return leagueIds

def getCategories(tags):
	tagIdsDict = {'Premier League': 1}
	tagIds = [tagIdsDict[key] for key in tags if key in tagIdsDict]
	return tagIds

def calculate_points(results):
    points = {
        'W': 3,
        'D': 1,
        'L': 0
    }
    
    total_points = 0
    for result in results:
        total_points += points.get(result, 0)  # Get points based on result
    
    return total_points

start_time = time.time()
currentRound = footballData.getCurrentRound()
print(currentRound)

currentRoundFixtures = footballData.getCurrentRoundFixtures(currentRound)

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

	homeTeamStanding = footballData.getTeamStanding(fixture["teams"]["home"]["id"])
	awayTeamStanding = footballData.getTeamStanding(fixture["teams"]["away"]["id"])

	date_object = datetime.fromisoformat(fixture["fixture"]["date"])
	if date_object.tzinfo is None:
   		date_object = date_object.replace(tzinfo=timezone.utc)
		   
	now = datetime.now(timezone.utc)

	if date_object < now:
		continue
	fixtureDateLong = date_object.strftime("%A, %d %B %Y")
	
	fixtureDate = date_object.strftime("%Y-%m-%d")
	fixtureTime = date_object.strftime("%H:%M")

	mapping = {
		'W': 'win',
		'D': 'draw',
		'L': 'loss'
	}

	homeTeamLastFiveGames = footballData.getTeamStats(fixture["teams"]["home"]["id"])["response"]["form"][-5:]
	awayTeamLastFiveGames = footballData.getTeamStats(fixture["teams"]["away"]["id"])["response"]["form"][-5:]
	lastFiveGamesFormHomeTeam = ', '.join([mapping[char] for char in homeTeamLastFiveGames])
	lastFiveGamesFormAwayTeam = ', '.join([mapping[char] for char in awayTeamLastFiveGames])

	homeTeamLastFiveGamesPoints = calculate_points(homeTeamLastFiveGames)
	awayTeamLastFiveGamesPoints = calculate_points(awayTeamLastFiveGames)

	homeTeamGoalsForInHome = footballData.getTeamStats(fixture["teams"]["home"]["id"])["response"]["goals"]["for"]["average"]["home"]
	# homeTeamGoalsForAway = footballData.getTeamStats(fixture["teams"]["home"]["id"])["response"]["goals"]["for"]["average"]["away"]
	homeTeamGoalsAgainstInHome = footballData.getTeamStats(fixture["teams"]["home"]["id"])["response"]["goals"]["against"]["average"]["home"]
	# homeTeamGoalsAgainstAway = footballData.getTeamStats(fixture["teams"]["home"]["id"])["response"]["goals"]["against"]["average"]["away"]

	# awayTeamGoalsForInHome = footballData.getTeamStats(fixture["teams"]["away"]["id"])["response"]["goals"]["for"]["average"]["home"]
	awayTeamGoalsForAway = footballData.getTeamStats(fixture["teams"]["away"]["id"])["response"]["goals"]["for"]["average"]["away"]
	# awayTeamGoalsAgainstInHome = footballData.getTeamStats(fixture["teams"]["away"]["id"])["response"]["goals"]["against"]["average"]["home"]
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
	homeTeamFilteredPlayers = list(filter(lambda player: player["statistics"][0]["games"]["rating"] is not None, homeTeamPlayers))

	homeTeamSortedPlayersBasedOnMinutes = sorted(homeTeamFilteredPlayers, key=lambda item: item["statistics"][0]["games"]["minutes"], reverse=True)[:15]
	homeTeamSortedPlayersBasedOnRating = sorted(homeTeamSortedPlayersBasedOnMinutes, key=lambda item: item["statistics"][0]["games"]["rating"], reverse=True)[:5]
	homeTeamKeyPlayersAbsences = []
	for player in homeTeamSortedPlayersBasedOnRating:
		if(isSidelined(player["player"]["id"], date_object.strftime("%Y-%m-%d"))):			
			homeTeamKeyPlayersAbsences.append(player["player"]["lastname"])
	
	homeTeamXG = xGData[fixture["teams"]["home"]["name"]]


	awayTeamPlayers = footballData.getPlayersStatsByTeam(fixture["teams"]["away"]["id"])
	awayTeamFilteredPlayers = list(filter(lambda player: player["statistics"][0]["games"]["rating"] is not None, awayTeamPlayers))
	awayTeamSortedPlayersBasedOnMinutes = sorted(awayTeamFilteredPlayers, key=lambda item: item["statistics"][0]["games"]["minutes"], reverse=True)[:15]
	awayTeamSortedPlayersBasedOnRating = sorted(awayTeamSortedPlayersBasedOnMinutes, key=lambda item: item["statistics"][0]["games"]["rating"], reverse=True)[:5]
	awayTeamKeyPlayersAbsences = []
	for player in awayTeamSortedPlayersBasedOnRating:
		if(isSidelined(player["player"]["id"], date_object.strftime("%Y-%m-%d"))):			
			awayTeamKeyPlayersAbsences.append(player["player"]["lastname"])

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
		"{head2head}": fixture["teams"]["home"]["name"] + " won " 
								 + str(homeTeamWins) + " times, " + fixture["teams"]["away"]["name"] + " won " + str(awayTeamWins)
								 + ", and " + str(drawsCount) + " draws.",
		"{homeTeamForm}": lastFiveGamesFormHomeTeam,
		"{homeTeamLastFiveGamesPoints}": str(homeTeamLastFiveGamesPoints),
		"{awayTeamLastFiveGamesPoints}": str(awayTeamLastFiveGamesPoints),
		"{awayTeamForm}": lastFiveGamesFormAwayTeam,
		# "{homeTeamGoalsStats}": "goals scored in home " + homeTeamGoalsForInHome + ", and goals scored away " + homeTeamGoalsForAway
		# 						+ ", goals conceded in home " + homeTeamGoalsAgainstInHome + ", and goals conceded away " + homeTeamGoalsAgainstAway,
		# "{awayTeamGoalsStats}": "goals scored in home " + awayTeamGoalsForInHome + ", and goals scored away " + awayTeamGoalsForAway
		# 						+ ", goals conceded in home " + awayTeamGoalsAgainstInHome + ", and goals conceded away " + awayTeamGoalsAgainstAway,
		"{homeTeamGoalsStats}": "goals scored in home " + homeTeamGoalsForInHome 
								+ ", goals conceded in home " + homeTeamGoalsAgainstInHome,
		"{awayTeamGoalsStats}": "goals scored away " + awayTeamGoalsForAway
								+ ", goals conceded away " + awayTeamGoalsAgainstAway,						
		"{homeXG}": homeTeamXG,
		"{awayXG}": awayTeamXG,
		"{homeTeamSidelinedPlayers}": ",".join(homeTeamKeyPlayersAbsences) if len(homeTeamKeyPlayersAbsences) > 0 else " None",
		"{awayTeamSidelinedPlayers}": ",".join(awayTeamKeyPlayersAbsences) if len(awayTeamKeyPlayersAbsences) > 0 else " None"
	}

	#prepare post header
	with open('post-header.html', 'r') as file:
		file_content = file.read()
	file_content = file_content.replace("{homeTeamBadge}", homeImage)
	file_content = file_content.replace("{matchDate}", fixtureDateLong)
	file_content = file_content.replace("{round}", round)
	file_content = file_content.replace("{referee}", referee)
	file_content = file_content.replace("{venue}", venue)
	file_content = file_content.replace("{matchTime}", fixtureTime)
	file_content = file_content.replace("{awayTeamBadge}", awayImage)
	
	#prepare team stats table
	with open('team-stats-comparison.html', 'r') as file:
		team_stats_file_content = file.read()
	team_stats_file_content = team_stats_file_content.replace("{homeTeam}", fixture["teams"]["home"]["name"])
	team_stats_file_content = team_stats_file_content.replace("{awayTeam}", fixture["teams"]["away"]["name"])
	team_stats_file_content = team_stats_file_content.replace("{homeTeamPoints}", str(homeTeamStanding["points"]))
	team_stats_file_content = team_stats_file_content.replace("{awayTeamPoints}", str(awayTeamStanding["points"]))
	team_stats_file_content = team_stats_file_content.replace("{homeTeamLastFiveGamesPoints}", str(homeTeamLastFiveGamesPoints))
	team_stats_file_content = team_stats_file_content.replace("{awayTeamLastFiveGamesPoints}", str(awayTeamLastFiveGamesPoints))
	team_stats_file_content = team_stats_file_content.replace("{homeTeamXG}", homeTeamXG)
	team_stats_file_content = team_stats_file_content.replace("{awayTeamXG}", awayTeamXG)
	team_stats_file_content = team_stats_file_content.replace("{homeTeamAvgGoalsScored}", homeTeamGoalsForInHome)
	team_stats_file_content = team_stats_file_content.replace("{awayTeamAvgGoalsScored}", awayTeamGoalsForAway)
	team_stats_file_content = team_stats_file_content.replace("{homeTeamAvgGoalsConceded}", homeTeamGoalsAgainstInHome)
	team_stats_file_content = team_stats_file_content.replace("{awayTeamAvgGoalsConceded}", awayTeamGoalsAgainstAway)
	
	with open('game-widget.html', 'r') as file:
		game_widget = file.read()
		game_widget = game_widget.replace("{fixtureId}", str(fixture["fixture"]["id"]))

	with open('standings-widget.html', 'r') as file:
		standings_widget = file.read()
		standings_widget = standings_widget.replace("{leagueId}", str(fixture["league"]["id"]))
		standings_widget = standings_widget.replace("{season}", str(fixture["league"]["season"]))

	#generate post with ollama
	with open("promptTemplatePL.txt", 'r', encoding='utf-8') as file:
		promptTemplate = file.read()

	for key, value in placeholders.items():
		promptTemplate = re.sub(key, value, promptTemplate)
	
	res = ollama.ChatOllama(promptTemplate)

	match = re.search(r'Prediction:\s*(\d+)', res)
	finalPrediction = None
	if match:
		finalPrediction = match.group(1).strip()

	file_content = file_content.rstrip()
	res = res.rstrip()
	team_stats_file_content = team_stats_file_content.rstrip()
	postContent = game_widget + res + team_stats_file_content + standings_widget
	postTitle = fixture["teams"]["home"]["name"] + " - " + fixture["teams"]["away"]["name"] + " Analysis and Prediction"
	print("CREATING WP POST...")
	# wpApi.createPost(postTitle, postContent, [league], [fixture["teams"]["home"]["name"], fixture["teams"]["away"]["name"]])
	wpPostCreated = wpApi.createPost(postTitle, postContent, fixture["teams"]["home"]["name"], fixture["teams"]["away"]["name"], leagueLogo, homeImage, awayImage, fixtureDate, round, fixtureTime, finalPrediction, [1])
	if(wpPostCreated):
		print("WP POST CREATED")

	
		
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Operation took {elapsed_time:.4f} seconds")
