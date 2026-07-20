import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    Target,
    TiktokPostParams,
    WebScrapingApiConfig,
)

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

result = client.web_scraping_api.scrape(
    TiktokPostParams(
        target=Target.TiktokPost,
        url='https://www.tiktok.com/@nba/video/7255379108241198378',
    )
)

print(json.dumps(result, indent=2))
