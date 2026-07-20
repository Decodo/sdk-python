import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    InstagramGraphqlProfileParams,
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
    InstagramGraphqlProfileParams(
        target=Target.InstagramGraphqlProfile,
        query='nba',
    )
)

print(json.dumps(result, indent=2))
