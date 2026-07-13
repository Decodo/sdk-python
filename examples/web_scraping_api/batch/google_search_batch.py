"""Batch Google Search scrape example."""
from __future__ import annotations

import os

from decodo import DecodoClient, DecodoConfig, WebScrapingApiConfig

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

batch = client.web_scraping_api.scrape_batch(
    {
        "target": "google_search",
        "query": ["Python web scraping", "httpx tutorial", "decodo api"],
    }
)

print(f"Batch ID: {batch.get('id')}")
for query_result in batch.get("queries", []):
    print(f"  Task {query_result.get('id')}: {query_result.get('status')}")
