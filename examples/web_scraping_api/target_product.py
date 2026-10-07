import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    Target,
    TargetProductParams,
    WebScrapingApiConfig,
)

api_key = os.environ["DECODO_API_KEY"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(api_key=api_key),
    )
)

result = client.web_scraping_api.scrape(
    TargetProductParams(
        target=Target.TargetProduct,
        product_id='92186007',
        headless='html',
        parse=True,
    )
)

print(json.dumps(result, indent=2))
