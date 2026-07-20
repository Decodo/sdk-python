"""Synchronous Google Search scrape example."""
from __future__ import annotations

import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    GoogleSearchParams,
    Target,
    WebScrapingApiConfig,
)

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

result = client.web_scraping_api.scrape(
    GoogleSearchParams(
        target=Target.GoogleSearch,
        query="Python web scraping",
        parse=True,
    )
)

print(result)
