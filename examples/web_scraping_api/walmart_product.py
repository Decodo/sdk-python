import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    Target,
    WalmartProductParams,
    WebScrapingApiConfig,
)

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

result = client.web_scraping_api.scrape(
    WalmartProductParams(
        target=Target.WalmartProduct,
        product_id='15296401808',
        headless='html',
        parse=True,
    )
)

print(json.dumps(result, indent=2))
