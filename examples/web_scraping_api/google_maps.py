import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    GoogleMapsParams,
    Target,
    WebScrapingApiConfig,
)

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

result = client.web_scraping_api.scrape(
    GoogleMapsParams(
        target=Target.GoogleMaps,
        query='coffee shops brooklyn',
        geo='United States',
        locale='en',
    )
)

print(json.dumps(result, indent=2))
