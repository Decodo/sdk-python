import os

from decodo import (
    CrawlError,
    CrawlRequest,
    CrawlTimeoutError,
    DecodoClient,
    DecodoConfig,
    WebScrapingApiConfig,
)

api_key = os.environ["DECODO_API_KEY"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(api_key=api_key),
    )
)

try:
    pages = client.web_scraping_api.crawl(
        CrawlRequest(url="https://www.example.com", limit=20, max_depth=2, output="markdown"),
        poll_interval=5,
        timeout=600,
    )
except CrawlTimeoutError as err:
    print(f"Crawl {err.crawl_id} is still running: {err}")
    raise SystemExit(1)
except CrawlError as err:
    print(f"Crawl {err.crawl_id} ended {err.status} ({err.reason})")
    raise SystemExit(1)

for page in pages:
    print(page["url"], page["status"], len(page.get("content", "")), "chars")
