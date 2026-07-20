import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    Target,
    TiktokShopSearchParams,
    WebScrapingApiConfig,
)

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

result = client.web_scraping_api.scrape(
    TiktokShopSearchParams(
        target=Target.TiktokShopSearch,
        query='necklace',
        headless='html',
    )
)

print(json.dumps(result, indent=2))
