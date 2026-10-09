import json
import os

from decodo import BbbParams, DecodoClient, DecodoConfig, Target, WebScrapingApiConfig

api_key = os.environ["DECODO_API_KEY"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(api_key=api_key),
    )
)

result = client.web_scraping_api.scrape(
    BbbParams(
        target=Target.Bbb,
        url='https://www.bbb.org/search?find_text=Tree+Service&find_entity=&find_type=&find_loc=New+York%2C+NY&find_country=USA',
    )
)

print(json.dumps(result, indent=2))
