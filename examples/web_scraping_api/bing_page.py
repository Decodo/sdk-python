import json
import os

from decodo import BingParams, DecodoClient, DecodoConfig, Target, WebScrapingApiConfig

api_key = os.environ["DECODO_API_KEY"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(api_key=api_key),
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
