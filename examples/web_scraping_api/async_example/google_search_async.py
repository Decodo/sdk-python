import json
import os
import time

from decodo import (
    DecodoClient,
    DecodoConfig,
    GoogleSearchParams,
    Target,
    WebScrapingApiConfig,
)

api_key = os.environ["DECODO_API_KEY"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(api_key=api_key),
    )
)

metadata = client.web_scraping_api.scrape_async(
    GoogleSearchParams(
        target=Target.GoogleSearch,
        query='shoes',
        geo='United States',
        parse=True,
    )
)

print('Polling for results...')

while True:
    print('Polling for results...')
    results = client.web_scraping_api.get_results(metadata['id'])
    if results:
        print(json.dumps(results['results'][0]['content'], indent=2))
        break
    time.sleep(3)
