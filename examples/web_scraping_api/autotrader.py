import json
import os

from decodo import (
    AutotraderParams,
    DecodoClient,
    DecodoConfig,
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
    AutotraderParams(
        target=Target.Autotrader,
        url='https://www.autotrader.co.uk/car-search?channel=cars&postcode=SE15+6GY&make=',
    )
)

print(json.dumps(result, indent=2))
