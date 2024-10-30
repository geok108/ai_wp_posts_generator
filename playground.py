from footballApi import FootballApi 
from datetime import datetime
import re
from ollamaHelper import OllamaHelper
from wpApi import WPApi
import time

footballData = FootballApi()
ollama = OllamaHelper()
wpApi = WPApi()


# res = footballData.getTeamStanding("51", True)
# footballData.getXG()
# awayTeamPlayers = footballData.getPlayersStatsByTeam(42)

res = footballData.getSidelinedPlayer("22090")
# res = footballData.getInjuriesByFixture(686308)
# if(res["results"] > 0):
#     team1_data = [item for item in res["response"] if item['team']['id'] == 165]
#     team2_data = [item for item in res["response"] if item['team']['id'] == 168]
print("dasd")
# res = ollama.ChatOllama('''You are a football betting tipster expert at what you do with many successes. Write a short post with you are prediction about the upcoming match between Chelsea and Newcastle. For your prediction you should consider the following: 
#                     a. absences of key players for both teams
#                     b. the form of both teams and how strong they teams they faced were
#                     c. their ranks and motives for the standings (eg. to win the championship, to get a place for Europa League)
#                     d. head 2 head between the two
#                     e. the expected goals(xG) that each team had until now this season
#                     f. performance of both teams based on whether they are playing home or away (eg. Team A had only one win away from home until now)
#                     ''')
# res = footballData.getPlayersStatsByTeam("51")
# filteredPlayers = {name: player for name, player in res.items() if player["games"]["rating"] is not None}
# sortedPlayersBasedOnMinutes = dict(sorted(filteredPlayers.items(), key=lambda item: item[1]["games"]["minutes"], reverse=True)[:15])
# sortedPlayersBasedOnRating = dict(sorted(sortedPlayersBasedOnMinutes.items(), key=lambda item: item[1]["games"]["rating"], reverse=True)[:5])

