import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    GoogleParams,
    Target,
    WebScrapingApiConfig,
)

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

result = client.web_scraping_api.scrape(
    GoogleParams(
        target=Target.Google,
        url='https://www.google.com/search?q=laptop',
        headless='html',
        parse=True,
    )
)

print(json.dumps(result, indent=2))
