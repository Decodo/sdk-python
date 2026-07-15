"""Async (polling) Google Search scrape example."""
from __future__ import annotations

import os
import time

from decodo import DecodoClient, DecodoConfig, GoogleSearchParams, Target, WebScrapingApiConfig

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

task = client.web_scraping_api.scrape_async(
    GoogleSearchParams(
        target=Target.GoogleSearch,
        query="Python web scraping",
        parse=True,
    )
)

task_id = task["id"]
print(f"Task created: {task_id}")

while True:
    status = client.web_scraping_api.get_status(task_id)
    print(f"Status: {status.get('status')}")

    if status.get("status") in ("done", "faulted"):
        break

    time.sleep(2)

results = client.web_scraping_api.get_results(task_id)
print(results)
