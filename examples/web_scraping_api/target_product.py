import json
import os

from decodo import DecodoClient, DecodoConfig, Target, TargetProductParams, WebScrapingApiConfig

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
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
