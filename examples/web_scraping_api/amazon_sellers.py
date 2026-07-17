import json
import os

from decodo import AmazonSellersParams, DecodoClient, DecodoConfig, Target, WebScrapingApiConfig

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

result = client.web_scraping_api.scrape(
    AmazonSellersParams(
        target=Target.AmazonSellers,
        query='A1R0Z7FJGTKESH',
        headless='html',
        parse=True,
    )
)

print(json.dumps(result, indent=2))
