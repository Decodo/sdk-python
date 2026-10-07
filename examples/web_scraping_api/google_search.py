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

api_key = os.environ["DECODO_API_KEY"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(api_key=api_key),
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
