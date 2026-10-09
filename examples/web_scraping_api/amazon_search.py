import json
import os

from decodo import (
    AmazonSearchParams,
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
    AmazonSearchParams(
        target=Target.AmazonSearch,
        query='laptop',
        geo='10001',
        headless='html',
        parse=True,
    )
)

print(json.dumps(result, indent=2))
