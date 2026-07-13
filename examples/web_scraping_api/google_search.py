"""Synchronous Google Search scrape example."""
from __future__ import annotations

import os

from decodo import DecodoClient, DecodoConfig, WebScrapingApiConfig

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

result = client.web_scraping_api.scrape(
    {
        "target": "google_search",
        "query": "Python web scraping",
    }
)

print(result)
