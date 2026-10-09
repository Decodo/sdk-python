import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    Target,
    WebScrapingApiConfig,
    YoutubeSearchMaxParams,
)

api_key = os.environ["DECODO_API_KEY"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(api_key=api_key),
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
