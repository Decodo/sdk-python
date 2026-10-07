import json
import os

from decodo import (
    AmazonBestsellersParams,
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
    AmazonBestsellersParams(
        target=Target.AmazonBestsellers,
        query='mobile-apps',
        parse=True,
    )
)

print(json.dumps(result, indent=2))
