from helpers.wpApi import WPApi
from datetime import datetime
from helpers.footballApi import FootballApi
wpApi = WPApi()
footballData = FootballApi()
finishedMatches = wpApi.getFinishedMatchesPosts()

past_matches = []

succeededMatches = 0
for match in finishedMatches:
    if(match.get('meta')['predictionSuccess'] == 'true'):
        succeededMatches += 1

print(str(succeededMatches) + "/" + str(len(finishedMatches)) + " succeeded matches")

for match in finishedMatches:
    current_date = datetime.now().strftime('%Y-%m-%d')

    match_date = datetime.strptime(match['meta']["matchDate"], '%Y-%m-%d')
    current_date = datetime.now()
    if match_date > current_date and match.get('meta')['predictionSuccess'] != '':
        continue

    if match['meta']['fixtureId'] == '':
        continue
    else:
        fixture = footballData.getFixtureById(match['meta']['fixtureId'])
        score = fixture['response'][0]['goals']
        if score['home'] == score['away']:
            result = 'X'
        elif score['home'] > score['away']:
            result = '1'
        else:
            result = '2'

        if result == match['meta']['prediction']:
            wpApi.updatePredictionSuccess(match.get('id'), 'true')
        else:
            wpApi.updatePredictionSuccess(match.get('id'), 'false')

        
print(past_matches)