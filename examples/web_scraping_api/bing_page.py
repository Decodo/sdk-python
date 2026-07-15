import json
import os

from decodo import BingParams, DecodoClient, DecodoConfig, Target, WebScrapingApiConfig

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

result = client.web_scraping_api.scrape(
    BingParams(
        target=Target.Bing,
        url='https://www.bing.com/search?q=laptop',
        headless='html',
        parse=True,
    )
)

print(json.dumps(result, indent=2))
