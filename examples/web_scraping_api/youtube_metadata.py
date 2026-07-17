import json
import os

from decodo import DecodoClient, DecodoConfig, Target, WebScrapingApiConfig, YoutubeMetadataParams

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

result = client.web_scraping_api.scrape(
    YoutubeMetadataParams(
        target=Target.YoutubeMetadata,
        query='dFu9aKJoqGg',
    )
)

print(json.dumps(result, indent=2))
