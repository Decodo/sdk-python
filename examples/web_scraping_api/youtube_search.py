import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    Target,
    WebScrapingApiConfig,
    YoutubeSearchParams,
)

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

result = client.web_scraping_api.scrape(
    YoutubeSearchParams(
        target=Target.YoutubeSearch,
        query='How to care for chinchillas',
    )
)

print(json.dumps(result, indent=2))
