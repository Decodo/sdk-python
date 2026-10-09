import json
import os

from decodo import (
    AppleAppStoreParams,
    DecodoClient,
    DecodoConfig,
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
    AppleAppStoreParams(
        target=Target.AppleAppStore,
        url='https://apps.apple.com/us/iphone/games',
    )
)

print(json.dumps(result, indent=2))
