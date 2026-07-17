import json
import os

from decodo import DecodoClient, DecodoConfig, GoogleTravelHotelsParams, Target, WebScrapingApiConfig

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
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
