import json
import os

from decodo import (
    AppleAppStoreParams,
    DecodoClient,
    DecodoConfig,
    Target,
    WebScrapingApiConfig,
)

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

result = client.web_scraping_api.scrape(
    AppleAppStoreParams(
        target=Target.AppleAppStore,
        url='https://apps.apple.com/us/iphone/games',
    )
)

print(json.dumps(result, indent=2))
