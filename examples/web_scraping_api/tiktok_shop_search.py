import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    Target,
    TiktokShopSearchParams,
    WebScrapingApiConfig,
)

api_key = os.environ["DECODO_API_KEY"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(api_key=api_key),
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
