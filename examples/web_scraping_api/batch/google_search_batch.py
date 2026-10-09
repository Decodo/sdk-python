import json
import os
import time

from decodo import (
    DecodoClient,
    DecodoConfig,
    GoogleSearchBatchParams,
    Target,
    WebScrapingApiConfig,
)

api_key = os.environ["DECODO_API_KEY"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(api_key=api_key),
    )
)

metadata = client.web_scraping_api.scrape_batch(
    GoogleSearchBatchParams(
        target=Target.GoogleSearch,
        query=["shoes", "laptop"],
        parse=True,
    )
)

while True:
    print("Polling for results...")
    queries = metadata.get("queries") or []
    if not queries:
        break
    first_task_id = queries[0].get("id")
    if not first_task_id:
        break
    results = client.web_scraping_api.get_results(first_task_id)
    if results:
        print(json.dumps(results["results"][0]["content"], indent=2))
        break
    time.sleep(3)
