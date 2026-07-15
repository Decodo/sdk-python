import json
import os

from decodo import AmazonPricingParams, DecodoClient, DecodoConfig, Target, WebScrapingApiConfig

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

result = client.web_scraping_api.scrape(
    AmazonPricingParams(
        target=Target.AmazonPricing,
        query='B09H74FXNW',
        geo='10001',
        headless='html',
        parse=True,
    )
)

print(json.dumps(result, indent=2))
