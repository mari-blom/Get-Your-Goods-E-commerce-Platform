import requests


def get_reddit_posts(subreddit="python"):
    # Build the URL for the subreddit's JSON feed
    url = f"https://www.reddit.com/r/{subreddit}.json"
    headers = {"User-Agent": "DjangoEcommerceApp/1.0"}
    # Required by Reddit
    # Make the request
    response = requests.get(url, headers=headers)
    # Handle errors
    if response.status_code != 200:
        print("Status Code:", response.status_code)
        print("Response:", response.text[:300])
        return []

    # Parse the JSON response
    data = response.json()
    posts = []

    # Extract useful fields from each post
    for item in data["data"]["children"]:
        post = item["data"]
        posts.append({
            "title": post["title"],
            "author": post["author"],
            "url": post["url"]
            })
    return posts
