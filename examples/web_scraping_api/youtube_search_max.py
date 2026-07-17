import json
import os

from decodo import DecodoClient, DecodoConfig, Target, WebScrapingApiConfig, YoutubeSearchMaxParams

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

result = client.web_scraping_api.scrape(
    YoutubeSearchMaxParams(
        target=Target.YoutubeSearchMax,
        query='How to care for chinchillas',
        video_sort_by='relevance',
    )
)

print(json.dumps(result, indent=2))
