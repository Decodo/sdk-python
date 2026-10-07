import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    Target,
    WalmartParams,
    WebScrapingApiConfig,
)

api_key = os.environ["DECODO_API_KEY"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(api_key=api_key),
    )
)

result = client.web_scraping_api.scrape(
    WalmartParams(
        target=Target.Walmart,
        url='https://www.walmart.com/cp/christmas-shop/1386088',
        headless='html',
    )
)

print(json.dumps(result, indent=2))
