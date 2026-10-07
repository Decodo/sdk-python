import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    Target,
    UniversalParams,
    WebScrapingApiConfig,
)

api_key = os.environ["DECODO_API_KEY"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(api_key=api_key),
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
