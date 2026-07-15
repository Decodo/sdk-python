import json
import os

from decodo import BbbParams, DecodoClient, DecodoConfig, Target, WebScrapingApiConfig

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

result = client.web_scraping_api.scrape(
    BbbParams(
        target=Target.Bbb,
        url='https://www.bbb.org/search?find_text=Tree+Service&find_entity=&find_type=&find_loc=New+York%2C+NY&find_country=USA',
    )
)

print(json.dumps(result, indent=2))
