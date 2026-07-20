import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    GoogleAiModeParams,
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
    GoogleAiModeParams(
        target=Target.GoogleAiMode,
        query='What are the top three dog breeds?',
        parse=True,
    )
)

print(json.dumps(result, indent=2))
