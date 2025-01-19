import requests
import json
from datetime import datetime

class WPApi:

    def __init__(self):
        self.site_url = 'https://betonfacts.com'
        self.endpoint = '/wp-json/wp/v2/posts'

    def getLeagueCategory(self, categories):
        switcher = {
            "39": 1,
            "140": 6,
            "135": 3,
            "78": 5,
            "61": 7,
            "2": 8
        }

        return [switcher.get(category, "") for category in categories]
    
    def createPost(self, title, content, fixtureId, teamA, teamB, leagueBadge, teamABadge, teamBBadge, matchDate, round, matchTime, prediction, categories=[], tags=[]):
        leagueCategories = self.getLeagueCategory(categories)

        # The post you want to create
        post_data = {
            "title": title,
            "content": content,
            "categories": leagueCategories,
            # "tags": tags,
            "meta": {
                "fixtureId": str(fixtureId),
                "teamA": teamA,
                "teamB": teamB,
                "teamABadge": teamABadge,
                "teamBBadge": teamBBadge,
                "leagueBadge": leagueBadge,
                "matchDate": matchDate,
                "round": round,
                "matchTime": matchTime,
                "prediction": prediction
            },
            'status': 'publish'  # Use 'draft' to create a draft post
        }
        # Complete URL
        url = f"{self.site_url}{self.endpoint}"
        # Load configuration from a JSON file
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)

        headers={
            "Authorization": config["wpApiKey"]
        }
        # Make the POST request
        print(url)
        response = requests.post(url, headers=headers, json=post_data)

        # Check the response
        if response.status_code == 201:
            print("Post created successfully. Details:", response.json())
            return True
        else:
            print("Failed to create post. Status Code:", response.status_code, "Response:", response.text)
            return False

    def getFinishedMatchesPosts(self):
        url =  f"{self.site_url}{self.endpoint}"
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        params = {
            'meta_key': "matchDate",
            'meta_value': current_date,
            'meta_compare': '<',
            'per_page': 100,
        }
        
        # Load configuration from a JSON file
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)

        headers={
            "Authorization": config["wpApiKey"]
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def update_post(self, post_id, data):
        url = f"{self.site_url}/posts/{post_id}"
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()
