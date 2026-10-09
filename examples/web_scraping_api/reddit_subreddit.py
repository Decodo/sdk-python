import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    RedditSubredditParams,
    Target,
    WebScrapingApiConfig,
)

api_key = os.environ["DECODO_API_KEY"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(api_key=api_key),
    )
)

result = client.web_scraping_api.scrape(
    RedditSubredditParams(
        target=Target.RedditSubreddit,
        url='https://www.reddit.com/r/nba/',
    )
)

print(json.dumps(result, indent=2))
