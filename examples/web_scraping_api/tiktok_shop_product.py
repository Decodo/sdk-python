import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    Target,
    TiktokShopProductParams,
    WebScrapingApiConfig,
)

api_key = os.environ["DECODO_API_KEY"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(api_key=api_key),
    )
)

result = client.web_scraping_api.scrape(
    TiktokShopProductParams(
        target=Target.TiktokShopProduct,
        product_id='1731541214379741272',
        headless='html',
    )
)

print(json.dumps(result, indent=2))
