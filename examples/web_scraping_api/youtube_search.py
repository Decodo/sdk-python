import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    Target,
    WebScrapingApiConfig,
    YoutubeSearchParams,
)

api_key = os.environ["DECODO_API_KEY"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(api_key=api_key),
    )
)

result = client.web_scraping_api.scrape(
    YoutubeSearchParams(
        target=Target.YoutubeSearch,
        query='How to care for chinchillas',
    )
)

print(json.dumps(result, indent=2))
