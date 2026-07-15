import json
import os

from decodo import DecodoClient, DecodoConfig, Target, TargetSearchParams, WebScrapingApiConfig

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
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
