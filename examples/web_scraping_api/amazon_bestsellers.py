import json
import os

from decodo import AmazonBestsellersParams, DecodoClient, DecodoConfig, Target, WebScrapingApiConfig

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
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
