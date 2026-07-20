import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    GoogleShoppingSearchParams,
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
    GoogleShoppingSearchParams(
        target=Target.GoogleShoppingSearch,
        query='laptop',
        headless='html',
        parse=True,
    )
)

print(json.dumps(result, indent=2))
