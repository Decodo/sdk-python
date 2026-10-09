import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    GoogleLensParams,
    Target,
    WebScrapingApiConfig,
)

api_key = os.environ["DECODO_API_KEY"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(api_key=api_key),
    )
)

result = client.web_scraping_api.scrape(
    GoogleLensParams(
        target=Target.GoogleLens,
        query='https://www.humanesociety.org/sites/default/files/2021-06/hamster-540188.jpg',
        headless='html',
    )
)

print(json.dumps(result, indent=2))
