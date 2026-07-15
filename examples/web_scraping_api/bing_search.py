import json
import os

from decodo import BingSearchParams, DecodoClient, DecodoConfig, Target, WebScrapingApiConfig

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
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
