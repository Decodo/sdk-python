import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    Target,
    WalmartSearchParams,
    WebScrapingApiConfig,
)

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

result = client.web_scraping_api.scrape(
    WalmartSearchParams(
        target=Target.WalmartSearch,
        query='wireless earbuds',
        parse=True,
    )
)

print(json.dumps(result, indent=2))
