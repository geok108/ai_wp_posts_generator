import requests

class WPApi:

    def __init__(self):
        self.site_url = 'http://localhost/wpdevninja'
        self.endpoint = '/wp-json/wp/v2/posts'

    def createPost(self, title, content):
        # The post you want to create
        post_data = {
            'title': title,
            'content': content,
            'status': 'draft'  # Use 'draft' to create a draft post
        }
        # Complete URL
        url = f"{self.site_url}{self.endpoint}"
        headers={
            "Authorization":"Basic YWRtaW46YWRtaW4="
        }
        # Make the POST request
        print(url)
        response = requests.post(url, headers=headers, params=post_data)

        # Check the response
        if response.status_code == 201:
            print("Post created successfully. Details:", response.json())
        else:
            print("Failed to create post. Status Code:", response.status_code, "Response:", response.text)
