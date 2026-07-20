import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    Target,
    TiktokShopProductParams,
    WebScrapingApiConfig,
)

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
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
