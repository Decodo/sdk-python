import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    Target,
    WebScrapingApiConfig,
    YoutubeSubtitlesParams,
)

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

result = client.web_scraping_api.scrape(
    YoutubeSubtitlesParams(
        target=Target.YoutubeSubtitles,
        query='L8zSWbQN-v8',
    )
)

print(json.dumps(result, indent=2))
