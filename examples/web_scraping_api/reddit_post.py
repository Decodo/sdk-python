import json
import os

from decodo import DecodoClient, DecodoConfig, RedditPostParams, Target, WebScrapingApiConfig

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

result = client.web_scraping_api.scrape(
    RedditPostParams(
        target=Target.RedditPost,
        url='https://www.reddit.com/r/nba/comments/17jrqc5/serious_next_day_thread_postgame_discussion/',
    )
)

print(json.dumps(result, indent=2))
