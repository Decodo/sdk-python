import json
import os

from decodo import DecodoClient, DecodoConfig, Target, UniversalParams, WebScrapingApiConfig

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

result = client.web_scraping_api.scrape(
    UniversalParams(
        target=Target.Universal,
        url='https://www.example.com',
        geo='United States',
        markdown=True,
    )
)

print(json.dumps(result, indent=2))
