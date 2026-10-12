"""Drive a crawl step by step instead of using crawl()."""

import os
import time

from decodo import CrawlRequest, DecodoClient, DecodoConfig, WebScrapingApiConfig

api_key = os.environ["DECODO_API_KEY"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(api_key=api_key),
    )
)

started = client.web_scraping_api.start_crawl(
    CrawlRequest(url="https://www.example.com", limit=20)
)
crawl_id = started["crawl_id"]
print("Started crawl", crawl_id)

while True:
    status = client.web_scraping_api.get_crawl_status(crawl_id)
    print(
        f"{status['status']}: {status['completed']} completed, "
        f"{status['failed']} failed, {status['in_flight']} in flight"
    )
    if status["status"] in ("done", "truncated", "faulted", "cancelled"):
        break
    time.sleep(5)


pages = client.web_scraping_api.get_crawl_results(crawl_id)
for page in pages:
    print(page["url"], page["status"])
