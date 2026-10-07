import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    GoogleAiModeParams,
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
    GoogleAiModeParams(
        target=Target.GoogleAiMode,
        query='What are the top three dog breeds?',
        parse=True,
    )
)

print(json.dumps(result, indent=2))
