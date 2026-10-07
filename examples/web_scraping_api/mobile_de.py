import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    MobileParams,
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
    MobileParams(
        target=Target.Mobile,
        url='https://suchen.mobile.de/fahrzeuge/search.html?dam=false&isSearchRequest=true&ref=quickSearch&s=Car&vc=Car',
    )
)

print(json.dumps(result, indent=2))
