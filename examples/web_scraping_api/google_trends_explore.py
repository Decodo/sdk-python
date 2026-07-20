import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    GoogleTrendsExploreParams,
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
    GoogleTrendsExploreParams(
        target=Target.GoogleTrendsExplore,
        query='seo optimization',
    )
)

print(json.dumps(result, indent=2))
