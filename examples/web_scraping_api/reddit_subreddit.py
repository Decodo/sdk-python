import json
import os

from decodo import DecodoClient, DecodoConfig, RedditSubredditParams, Target, WebScrapingApiConfig

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

result = client.web_scraping_api.scrape(
    RedditSubredditParams(
        target=Target.RedditSubreddit,
        url='https://www.reddit.com/r/nba/',
    )
)

print(json.dumps(result, indent=2))
