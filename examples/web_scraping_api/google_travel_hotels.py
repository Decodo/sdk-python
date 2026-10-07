import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    GoogleTravelHotelsParams,
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
    GoogleTravelHotelsParams(
        target=Target.GoogleTravelHotels,
        query='trivago',
        headless='html',
        adults=2,
    )
)

print(json.dumps(result, indent=2))
