from helpers.footballApi import FootballApi 
from datetime import datetime, timezone
import re
from helpers.ollamaHelper import OllamaHelper
from helpers.wpApi import WPApi
import re
import time
import json

class MatchAnalysisPostGenerator:
    def __init__(self):
        self.ollama = OllamaHelper()
        self.wpApi = WPApi()

    def _isSidelined(self, playerId, fixtureDate):
        sidelinedPlayer = self.footballData.getSidelinedPlayer(playerId)
        absenceEndDate = None if sidelinedPlayer["results"] == 0 or sidelinedPlayer["response"][0]["end"] is None else datetime.strptime(sidelinedPlayer["response"][0]["end"], "%Y-%m-%d")
        fixtureDate = datetime.strptime(fixtureDate, "%Y-%m-%d")

        if(absenceEndDate is None or absenceEndDate > fixtureDate):
            return True
        
        return False

    def _calculate_points(self, results):
        points = {
            'W': 3,
            'D': 1,
            'L': 0
        }
        
        total_points = 0
        for result in results:
            total_points += points.get(result, 0)  # Get points based on result
    
        return total_points

    def read_prompt_by_lines(self, file_path):
        prompt = ""
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                prompt += line  # Add each line to the prompt string, preserving newlines
        return prompt
    
    def generate(self, leagueId, season, currentRound=None):
        start_time = time.time()
       
        self.footballData = FootballApi(leagueId, season)
        if currentRound is None:
            currentRound = self.footballData.getCurrentRound()
        print(currentRound) 

        currentRoundFixtures = self.footballData.getCurrentRoundFixtures(currentRound)

        for fixture in currentRoundFixtures["response"]:
            # if(fixture["fixture"]["id"] != 1208659):
            #     continue
            print("-------------FIXTURE " + fixture["teams"]["home"]["name"] + " vs " + fixture["teams"]["away"]["name"] + "-------------")

            league = fixture["league"]["name"]
            # leagueLogo = fixture["league"]["logo"]
            round = fixture["league"]["round"]
            flag=fixture["league"]["flag"]
            venue = fixture['fixture']['venue']['name'] + ', ' + fixture['fixture']['venue']['city']
            referee = fixture['fixture']['referee']
            # homeImage = fixture['teams']['home']['logo']
            # awayImage = fixture['teams']['away']['logo']

            leagueLogo = "https://betonfacts.com/league-" + str(fixture["league"]["id"])
            homeTeamImage = "https://betonfacts.com/team-" + str(fixture['teams']['home']['id'])
            awayTeamImage = "https://betonfacts.com/team-" + str(fixture['teams']['away']['id'])
            homeTeamStanding = self.footballData.getTeamStanding(fixture["teams"]["home"]["id"])
            awayTeamStanding = self.footballData.getTeamStanding(fixture["teams"]["away"]["id"])

            date_object = datetime.fromisoformat(fixture["fixture"]["date"])
            if date_object.tzinfo is None:
                date_object = date_object.replace(tzinfo=timezone.utc)
                
            now = datetime.now(timezone.utc)
            
            if date_object <= now or (date_object - now).days > 3:
                continue
            fixtureDateLong = date_object.strftime("%A, %d %B %Y")
            
            fixtureDate = date_object.strftime("%Y-%m-%d")
            fixtureTime = date_object.strftime("%H:%M")

            homeTeamLastFiveGames = self.footballData.getTeamStats(fixture["teams"]["home"]["id"])["response"]["form"][-5:][::-1]
            awayTeamLastFiveGames = self.footballData.getTeamStats(fixture["teams"]["away"]["id"])["response"]["form"][-5:][::-1]

            homeTeamMostRecentResult = homeTeamLastFiveGames[0]
            homeTeamConsecutiveWins = 0

            homeTeamFormText = ""
            if homeTeamMostRecentResult == 'W':
                homeTeamConsecutiveWins = 0
                for result in homeTeamLastFiveGames:
                    if result == 'W':
                        homeTeamConsecutiveWins += 1
                    else:
                        break
                homeTeamFormText = " is coming from " + str(homeTeamConsecutiveWins) + "consecutive wins" if homeTeamConsecutiveWins > 1 else " is coming from a win"
            elif homeTeamMostRecentResult == 'L':
                homeTeamFormText = " is coming from a loss"
            else:
                homeTeamFormText = " is coming from a draw"

            awayTeamMostRecentResult = awayTeamLastFiveGames[0]
            awayTeamConsecutiveWins = 0

            awayTeamFormText = ""
            if awayTeamMostRecentResult == 'W':
                awayTeamConsecutiveWins = 0
                for result in awayTeamLastFiveGames:
                    if result == 'W':
                        awayTeamConsecutiveWins += 1
                    else:
                        break
                awayTeamFormText = " is coming from " + str(awayTeamConsecutiveWins) + "consecutive wins" if awayTeamConsecutiveWins > 1 else " won last game"
            elif awayTeamMostRecentResult == 'L':
                awayTeamFormText = " lost last game"
            else:
                awayTeamFormText = " got a draw in last game"

            homeTeamLastFiveGamesPoints = self._calculate_points(homeTeamLastFiveGames)
            awayTeamLastFiveGamesPoints = self._calculate_points(awayTeamLastFiveGames)

            homeTeamFormText += " in the league and got " + str(homeTeamLastFiveGamesPoints) + " points in the last 5 games out of the 15 points available"
            awayTeamFormText += " in the league and got " + str(awayTeamLastFiveGamesPoints) + " points in the last 5 games out of the 15 points available"

            homeTeamGoalsForInHome = self.footballData.getTeamStats(fixture["teams"]["home"]["id"])["response"]["goals"]["for"]["average"]["home"]
            # homeTeamGoalsForAway = self.footballData.getTeamStats(fixture["teams"]["home"]["id"])["response"]["goals"]["for"]["average"]["away"]
            homeTeamGoalsAgainstInHome = self.footballData.getTeamStats(fixture["teams"]["home"]["id"])["response"]["goals"]["against"]["average"]["home"]
            # homeTeamGoalsAgainstAway = self.footballData.getTeamStats(fixture["teams"]["home"]["id"])["response"]["goals"]["against"]["average"]["away"]

            # awayTeamGoalsForInHome = self.footballData.getTeamStats(fixture["teams"]["away"]["id"])["response"]["goals"]["for"]["average"]["home"]
            awayTeamGoalsForAway = self.footballData.getTeamStats(fixture["teams"]["away"]["id"])["response"]["goals"]["for"]["average"]["away"]
            # awayTeamGoalsAgainstInHome = self.footballData.getTeamStats(fixture["teams"]["away"]["id"])["response"]["goals"]["against"]["average"]["home"]
            awayTeamGoalsAgainstAway = self.footballData.getTeamStats(fixture["teams"]["away"]["id"])["response"]["goals"]["against"]["average"]["away"]
            
            h2h = self.footballData.getHeadToHead(fixture["teams"]["home"]["id"], fixture["teams"]["away"]["id"])
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

            xGData = self.footballData.getXG(leagueId)
            homeTeamPlayers = self.footballData.getPlayersStatsByTeam(fixture["teams"]["home"]["id"])
            homeTeamFilteredPlayers = list(filter(lambda player: player["statistics"][0]["games"]["rating"] is not None, homeTeamPlayers))

            homeTeamSortedPlayersBasedOnMinutes = sorted(homeTeamFilteredPlayers, key=lambda item: item["statistics"][0]["games"]["minutes"] or 0, reverse=True)[:15]
            homeTeamSortedPlayersBasedOnRating = sorted(homeTeamSortedPlayersBasedOnMinutes, key=lambda item: item["statistics"][0]["games"]["rating"], reverse=True)[:5]
            homeTeamKeyPlayersAbsences = []
            for player in homeTeamSortedPlayersBasedOnRating:
                if(self._isSidelined(player["player"]["id"], date_object.strftime("%Y-%m-%d"))):			
                    homeTeamKeyPlayersAbsences.append(player["player"]["lastname"])
            
            homeTeamXG = xGData[fixture["teams"]["home"]["name"]]


            awayTeamPlayers = self.footballData.getPlayersStatsByTeam(fixture["teams"]["away"]["id"])
            awayTeamFilteredPlayers = list(filter(lambda player: player["statistics"][0]["games"]["rating"] is not None, awayTeamPlayers))
            awayTeamSortedPlayersBasedOnMinutes = sorted(awayTeamFilteredPlayers, key=lambda item: item["statistics"][0]["games"]["minutes"] or 0, reverse=True)[:15]
            awayTeamSortedPlayersBasedOnRating = sorted(awayTeamSortedPlayersBasedOnMinutes, key=lambda item: item["statistics"][0]["games"]["rating"], reverse=True)[:5]
            awayTeamKeyPlayersAbsences = []
            for player in awayTeamSortedPlayersBasedOnRating:
                if(self._isSidelined(player["player"]["id"], date_object.strftime("%Y-%m-%d"))):			
                    awayTeamKeyPlayersAbsences.append(player["player"]["lastname"] + " (" + player["statistics"][0]["games"]["position"] + ")")

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
                "{homeTeamForm}": homeTeamFormText,
                "{awayTeamForm}": awayTeamFormText,
                # "{homeTeamGoalsStats}": "goals scored in home " + homeTeamGoalsForInHome + ", and goals scored away " + homeTeamGoalsForAway
                # 						+ ", goals conceded in home " + homeTeamGoalsAgainstInHome + ", and goals conceded away " + homeTeamGoalsAgainstAway,
                # "{awayTeamGoalsStats}": "goals scored in home " + awayTeamGoalsForInHome + ", and goals scored away " + awayTeamGoalsForAway
                # 						+ ", goals conceded in home " + awayTeamGoalsAgainstInHome + ", and goals conceded away " + awayTeamGoalsAgainstAway,
                "{homeTeamGoalsStats}": fixture["teams"]["home"]["name"] + " scored an average of " + homeTeamGoalsForInHome + " goals in home and conceded an average of " + homeTeamGoalsAgainstInHome + " goals in home",
                "{awayTeamGoalsStats}": fixture["teams"]["away"]["name"] + " scored an average of " + awayTeamGoalsForAway+ " goals away and conceded an average of " + awayTeamGoalsAgainstAway + " goals in away matches",
                "{homeXG}": homeTeamXG,
                "{awayXG}": awayTeamXG,
                "{homeTeamSidelinedPlayers}": ",".join(homeTeamKeyPlayersAbsences) if len(homeTeamKeyPlayersAbsences) > 0 else " None",
                "{awayTeamSidelinedPlayers}": ",".join(awayTeamKeyPlayersAbsences) if len(awayTeamKeyPlayersAbsences) > 0 else " None"
            }

            #prepare post header
            # with open('post-header.html', 'r') as file:
            # 	file_content = file.read()
            # file_content = file_content.replace("{homeTeamBadge}", homeImage)
            # file_content = file_content.replace("{matchDate}", fixtureDateLong)
            # file_content = file_content.replace("{round}", round)
            # file_content = file_content.replace("{referee}", referee)
            # file_content = file_content.replace("{venue}", venue)
            # file_content = file_content.replace("{matchTime}", fixtureTime)
            # file_content = file_content.replace("{awayTeamBadge}", awayImage)
            
            #prepare team stats table
            with open('htmlWidgets/team-stats-comparison.html', 'r') as file:
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
            
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)

            with open('htmlWidgets/game-widget.html', 'r') as file:
                game_widget = file.read()
                game_widget = game_widget.replace("{fixtureId}", str(fixture["fixture"]["id"]))
                game_widget = game_widget.replace("{key}", config["rapidApiKey"])

            with open('htmlWidgets/standings-widget.html', 'r') as file:
                standings_widget = file.read()
                standings_widget = standings_widget.replace("{leagueId}", str(fixture["league"]["id"]))
                standings_widget = standings_widget.replace("{season}", str(fixture["league"]["season"]))
                standings_widget = standings_widget.replace("{key}", config["rapidApiKey"])

            #generate post with ollama
            with open("promptTemplate.txt", 'r', encoding='utf-8') as file:
                promptTemplate = file.read().strip().replace("\n", " ")

            for key, value in placeholders.items():
                promptTemplate = re.sub(key, value, promptTemplate)
            
            res = self.ollama.ChatOllama(promptTemplate)

            match = re.search(r'Prediction:\s*([1X2])', res)
            finalPrediction = None
            if match:
                finalPrediction = match.group(1).strip()

            # file_content = file_content.rstrip()
            res = res.rstrip()
            team_stats_file_content = team_stats_file_content.rstrip()
            postContent = game_widget + res + team_stats_file_content + standings_widget
            postTitle = fixture["teams"]["home"]["name"] + " - " + fixture["teams"]["away"]["name"] + " Analysis and Prediction"
            print("CREATING WP POST...")
            # wpApi.createPost(postTitle, postContent, [league], [fixture["teams"]["home"]["name"], fixture["teams"]["away"]["name"]])
            wpPostCreated = self.wpApi.createPost(postTitle, postContent, fixture["fixture"]["id"], fixture["teams"]["home"]["name"], fixture["teams"]["away"]["name"], leagueLogo, homeTeamImage, awayTeamImage, fixtureDate, round, fixtureTime, finalPrediction, [leagueId], [round])
            if(wpPostCreated):
                print("WP POST CREATED")

            
                
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Operation took {elapsed_time:.4f} seconds")