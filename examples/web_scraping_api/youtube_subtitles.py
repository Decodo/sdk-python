import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    Target,
    WebScrapingApiConfig,
    YoutubeSubtitlesParams,
)

api_key = os.environ["DECODO_API_KEY"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(api_key=api_key),
    )
)

result = client.web_scraping_api.scrape(
    YoutubeSubtitlesParams(
        target=Target.YoutubeSubtitles,
        query='L8zSWbQN-v8',
    )
)

print(json.dumps(result, indent=2))
