import json
import os

from decodo import (
    AutotraderParams,
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
    AutotraderParams(
        target=Target.Autotrader,
        url='https://www.autotrader.co.uk/car-search?channel=cars&postcode=SE15+6GY&make=',
    )
)

print(json.dumps(result, indent=2))
