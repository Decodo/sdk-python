import json
import os

from decodo import (
    BingSearchParams,
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
    BingSearchParams(
        target=Target.BingSearch,
        query='electric vehicles',
        geo='United States',
        parse=True,
        locale='en-US',
    )
)

print(json.dumps(result, indent=2))
