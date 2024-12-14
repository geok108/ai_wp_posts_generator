import requests

class WPApi:

    def __init__(self):
        self.site_url = '{sitelink}'
        self.endpoint = '/wp-json/wp/v2/posts'

    def createPost(self, title, content, teamA, teamB, teamABadge, teamBBadge, matchDate, matchTime, prediction, categories=[], tags=[]):
        # The post you want to create
        post_data = {
            "title": title,
            "content": content,
            "categories": categories,
            "tags": tags,
            "meta": {
                "teamA": teamA,
                "teamB": teamB,
                "teamABadge": teamABadge,
                "teamBBadge": teamBBadge,
                "matchDate": matchDate,
                "matchTime": matchTime,
                "prediction": prediction
            },
            'status': 'draft'  # Use 'draft' to create a draft post
        }
        # Complete URL
        url = f"{self.site_url}{self.endpoint}"
        headers={
            "Authorization":"{token}"
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
