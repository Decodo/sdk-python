import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    GoogleMapsParams,
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
    GoogleMapsParams(
        target=Target.GoogleMaps,
        query='coffee shops brooklyn',
        geo='United States',
        locale='en',
    )
)

print(json.dumps(result, indent=2))
