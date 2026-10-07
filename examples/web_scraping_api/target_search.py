import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    Target,
    TargetSearchParams,
    WebScrapingApiConfig,
)

api_key = os.environ["DECODO_API_KEY"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(api_key=api_key),
    )
)

result = client.web_scraping_api.scrape(
    TargetSearchParams(
        target=Target.TargetSearch,
        query='laptop',
        headless='html',
        parse=True,
    )
)

print(json.dumps(result, indent=2))
