import json
import os
import time

from decodo import DecodoClient, DecodoConfig, GoogleSearchParams, Target, WebScrapingApiConfig

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

metadata = client.web_scraping_api.scrape_batch(
    GoogleSearchParams(
        target=Target.GoogleSearch,
        query=['shoes', 'laptop'],
        parse=True,
    )
)

print('Polling for results...')

while True:
    print('Polling for results...')
    queries = metadata.get('queries') or []
    if not queries:
        break
    first_task_id = queries[0].get('id')
    if not first_task_id:
        break
    results = client.web_scraping_api.get_results(first_task_id)
    if results:
        print(json.dumps(results['results'][0]['content'], indent=2))
        break
    time.sleep(3)
