import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    Target,
    WebScrapingApiConfig,
    YoutubeChannelParams,
)

api_key = os.environ["DECODO_API_KEY"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(api_key=api_key),
    )
)

result = client.web_scraping_api.scrape(
    YoutubeChannelParams(
        target=Target.YoutubeChannel,
        query='@decodo_official',
        limit=20,
        parse=True,
    )
)

print(json.dumps(result, indent=2))
