# Decodo Python SDK

![Python](https://img.shields.io/badge/python-%3E%3D3.12-green)
![License](https://img.shields.io/badge/license-MIT-blue)

[![](https://dcbadge.limes.pink/api/server/https://discord.gg/Ja8dqKgvbZ)](https://discord.gg/Ja8dqKgvbZ)

<p align="center">
<a href="https://dashboard.decodo.com/integrations?utm_source=github&utm_medium=social&utm_campaign=python_sdk"> <img src="https://github.com/user-attachments/assets/a1e52a9e-3da1-4081-b3c6-053aafb8f196"/></a>

The official Python SDK for the Decodo Web Scraping API.

Build scraping workflows for search engines, eCommerce platforms, social media, AI tools, and more using the Decodo Web Scraping API.

- Fully typed targets and parameters with IDE autocomplete
- Sync, async, and batch scraping methods
- Built on `httpx`, Python 3.12+
- Typed error hierarchy for safer integrations
- Built for Python and modern tooling

# What is Decodo Python SDK?

Decodo Python SDK is the official Python SDK for the Decodo Web Scraping API. It provides a typed interface for interacting with Decodo targets like Google, Amazon, TikTok, Reddit, YouTube, ChatGPT, Perplexity, and more.

Instead of manually constructing HTTP requests and validating payloads, you can work with fully typed methods and target-specific parameters directly in your editor.

# Why use the SDK?

- **Typing and autocomplete**. Target parameters are fully typed for better DX and fewer mistakes.
- **Unified scraping interface**. Work with search engines, eCommerce platforms, social media, and AI tools through one SDK.
- **Async and batch workflows**. Create scraping tasks, poll statuses, and process batches at scale.
- **Typed errors**. Handle authentication, validation, timeout, and rate-limit failures safely.
- **Minimal setup**. Single dependency on `httpx`, no additional HTTP client required.

## Requirements

- Python 3.12+

## Installation

```bash
pip install decodo-sdk
```

## Quick start

Create a new project:

```sh
mkdir scrape-with-decodo
cd scrape-with-decodo

pip install decodo-sdk

touch main.py
```

Copy your Web Data API key from your Web Data API subscription on the [Decodo dashboard](https://dashboard.decodo.com/web-data/playground). Older plans only have a basic authentication token, which you can pass as `token` instead (see [Configuration](#configuration)).

Every target has a corresponding parameter class. Import the one you need, fill in its fields, and pass it to `scrape()`:

```python
# main.py
from decodo import (
    DecodoClient,
    DecodoConfig,
    GoogleSearchParams,
    WebScrapingApiConfig,
)

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(
            api_key="<api_key>",
        ),
    )
)

result = client.web_scraping_api.scrape(
    GoogleSearchParams(
        query="coffee shops",
        geo="United States",
        parse=True,
    )
)

print(result)
```

Run the script:

```
python main.py
```

Parameter classes are bundled with the package, so no extra step is needed after `pip install decodo-sdk`. Each class pins its own target and accepts only the fields that target supports. Your IDE can flag misspelled or unsupported fields, while runtime validation catches them before the request is sent.

`GoogleSearchParams` is the parameter class for `Target.GoogleSearch`. The naming follows a simple pattern covered in [Targets and parameter classes](#targets-and-parameter-classes).

### Alternative: dictionary payloads

Scraping methods also accept a plain Python dictionary. The payload is validated against the bundled schema before the request is sent, but nothing is checked while you write the code, so typos and unsupported fields surface only at runtime:

```python
result = client.web_scraping_api.scrape({
    "target": "google_search",
    "query": "coffee shops",
    "geo": "United States",
    "parse": True,
})

print(result)
```

Use the `Target` enum instead of a raw string to avoid mistyping the target name:

```python
from decodo import Target

result = client.web_scraping_api.scrape({
    "target": Target.GoogleSearch,
    "query": "coffee shops",
    "parse": True,
})

print(result)
```

Typed parameters are recommended for anything beyond a quick experiment. The rest of this README uses the typed parameter approach throughout.

### Updating types to a newer schema

The types bundled in the package reflect the schema at release time. To update them to the latest schema without waiting for a new release, run the type generator:

```bash
python -m decodo.codegen.codegen --out-dir ./decodo_generated
```

Then import from that directory instead:

```python
from decodo_generated.targets import GoogleSearchParams
```

> The directory name passed to `--out-dir` becomes the import namespace. `./decodo_generated` → `from decodo_generated.targets import ...`. You can use any name, but keep it consistent across your project.

<details>
<summary>Example response</summary>

```json
{
  "results": [
    {
      "content": {
        "results": {
          "last_visible_page": 10,
          "page": 1,
          "parse_status_code": 12000,
          "results": {
            "local_pack": [
              {
                "items": [
                  {
                    "address": "Rochester, NY",
                    "paid": false,
                    "pos": 1,
                    "rating": 4.9,
                    "rating_count": 1700,
                    "subtitle": "Coffee shop",
                    "title": "Albunn Coffee House"
                  },
                  {
                    "address": "Rochester, NY",
                    "paid": false,
                    "pos": 2,
                    "rating": 4.8,
                    "rating_count": 937,
                    "subtitle": "Coffee shop",
                    "title": "Layali Coffee House"
                  },
                  {
                    "address": "Ocean Township, NJ",
                    "paid": false,
                    "pos": 3,
                    "rating": 4.9,
                    "rating_count": 124,
                    "subtitle": "Coffee shop",
                    "title": "Ocean Brew Co."
                  }
                ],
                "pos_overall": 1
              }
            ],
            "organic": [
              {
                "desc": "For an alternate, local view, Eater has an interesting list of what it considers Philadelphia's 21 Essential Coffee Shops.",
                "pos": 1,
                "pos_overall": 2,
                "title": "Philadelphia",
                "url": "https://www.brian-coffee-spot.com/the-coffee-spot-guide-to/usa-canada/philadelphia/"
              }
            ],
            "search_information": {
              "query": "coffee shops",
              "total_results_count": 403000000
            }
          },
          "url": "https://www.google.com/search?q=coffee+shops&hl=en&gl=us"
        },
        "errors": [],
        "status_code": 12000,
        "task_id": "7463508496927950850"
      },
      "status_code": 200,
      "url": "https://www.google.com/search?q=coffee+shops&hl=en&gl=us",
      "task_id": "7463508496927950850",
      "created_at": "2026-05-22 08:38:10",
      "updated_at": "2026-05-22 08:38:13"
    }
  ]
}
```

</details>

## Configuration

```python
from decodo import (
    DecodoClient,
    DecodoConfig,
    WebScrapingApiConfig,
)

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(
            api_key="<api_key>",
        ),
        timeout_ms=120_000,  # optional, request timeout in ms (default: 180000)
    )
)
```

Pass either `api_key` or `token`, not both. The client raises `ValueError` if you set both.

```python
# Basic auth token (older plans)
client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(
            token="<basic_auth_token>",
        ),
    )
)
```

| Parameter    | Description                                                                                                                                         |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `api_key`    | Web Data API key. Recommended                                                                                                                       |
| `token`      | Web Scraping API basic auth token for older plans, the base64-encoded `user:password` string from the Decodo dashboard. Use it instead of `api_key` |
| `timeout_ms` | Request timeout in milliseconds (default: 180000)                                                                                                   |

## Web Scraping API

Access the API via `client.web_scraping_api`.

The snippets below assume you have already constructed a client. See [Configuration](#configuration) for how to build one.

### Sync scrape

Waits for the scraping result before returning:

```python
from decodo import (
    AmazonProductParams,
    DecodoClient,
    DecodoConfig,
    WebScrapingApiConfig,
)

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(
            api_key="<api_key>",
        ),
    )
)

# Run the scrape and wait for the result.
result = client.web_scraping_api.scrape(
    AmazonProductParams(
        query="B09H74FXNW",
        parse=True,
    )
)

# Print the completed response.
print(result)
```

### Async scrape

Creates a scraping task and returns immediately, then you poll for status and results:

```python
import time

from decodo import (
    DecodoClient,
    DecodoConfig,
    GoogleSearchParams,
    WebScrapingApiConfig,
)

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(
            api_key="<api_key>",
        ),
    )
)

# Submit the scraping task and return immediately.
task = client.web_scraping_api.scrape_async(
    GoogleSearchParams(
        query="laptop reviews",
        parse=True,
    )
)

# Save the returned task ID.
task_id = task["id"]

# Poll until the task finishes.
while True:
    status = client.web_scraping_api.get_status(task_id)["status"]

    if status == "done":
        break

    if status == "faulted":
        raise RuntimeError(f"Scraping task {task_id} failed.")

    time.sleep(2)

# Retrieve and print the completed result.
result = client.web_scraping_api.get_results(task_id)

print(result)
```

`get_status` returns `pending`, `done`, or `faulted`.

### Batch scrape

Send multiple inputs in a single request. Batch calls use the batch variant of the target's parameter class, where the primary input accepts a list:

```python
import time

from decodo import (
    DecodoClient,
    DecodoConfig,
    GoogleSearchBatchParams,
    WebScrapingApiConfig,
)

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(
            api_key="<api_key>",
        ),
    )
)

# Submit multiple queries in a single batch request.
# For another target, use its batch parameter class and primary input.
batch = client.web_scraping_api.scrape_batch(
    GoogleSearchBatchParams(
        query=["coffee", "tea", "juice"],
        parse=True,
    )
)

# Wait for each task and print its completed result.
for task in batch["queries"]:
    task_id = task["id"]

    while True:
        status = client.web_scraping_api.get_status(task_id)["status"]

        if status == "done":
            break

        if status == "faulted":
            raise RuntimeError(f"Scraping task {task_id} failed.")

        time.sleep(2)

    result = client.web_scraping_api.get_results(task_id)

    print(result)
```

## Data API: search, map and crawl

These endpoints are served by the Data API at `data.decodo.com` and need an `api_key`. Calling them on a client configured with a basic auth `token` raises `ValueError` saying an API key is required. They live on the same `client.web_scraping_api` namespace.

Parameters are plain dictionaries. The `SearchRequest`, `MapRequest` and `CrawlRequest` types are `TypedDict`s you can use for editor completion; they are always importable and need no code generation. Bodies are validated against the bundled schema before the request is sent, like `scrape`.

### Search

Runs a web search and returns the parsed result document:

```python
from decodo import DecodoClient, DecodoConfig, SearchRequest, WebScrapingApiConfig

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(
            api_key="<api_key>",
        ),
    )
)

result = client.web_scraping_api.search(
    SearchRequest(query="coffee shops", geo="United States", page=1)
)

for item in result.get("organic", []):
    print(item["rank"], item["title"], item["link"])
```

A search that ran but could not be scraped still answers with HTTP 200 and `status: "failed"` plus a `message`, so check `result["status"]` before reading the fields.

### Map

Discovers the links on a site, from its pages and sitemap:

```python
from decodo import DecodoClient, DecodoConfig, MapRequest, WebScrapingApiConfig

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(
            api_key="<api_key>",
        ),
    )
)

result = client.web_scraping_api.map(
    MapRequest(url="https://www.example.com", limit=100, sitemap="include")
)

for link in result["results"][0]["content"]["links"]:
    print(link["url"])
```

### Crawl

`crawl` starts a crawl, waits for it to finish and returns every page with its content:

```python
from decodo import (
    CrawlError,
    CrawlInterruptedError,
    CrawlRequest,
    CrawlTimeoutError,
    DecodoClient,
    DecodoConfig,
    WebScrapingApiConfig,
)

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(
            api_key="<api_key>",
        ),
    )
)

try:
    pages = client.web_scraping_api.crawl(
        CrawlRequest(url="https://www.example.com", limit=20, max_depth=2),
        poll_interval=5,
        timeout=600,
    )
except CrawlTimeoutError as err:
    print(f"Still running, fetch it later with get_crawl_results({err.crawl_id!r})")
except CrawlError as err:
    print(f"Crawl {err.crawl_id} ended {err.status}: {err.reason}")
else:
    for page in pages:
        print(page["url"], page["status"], page.get("content", "")[:80])
```

A crawl that stops early because of `max_duration` or a vendor limit ends with status `truncated`; `crawl` returns the pages it did collect. Pages are returned as the API lists them, each with its `status` (`pending`, `done` or `faulted`) and, when the fetch failed, a `content_error` instead of `content`.

The lower-level methods let you drive a crawl yourself, for example to start it in one process and collect it in another:

```python
started = client.web_scraping_api.start_crawl(CrawlRequest(url="https://www.example.com"))
crawl_id = started["crawl_id"]

status = client.web_scraping_api.get_crawl_status(crawl_id)
print(status["status"], status["completed"], status["in_flight"])

pages = client.web_scraping_api.get_crawl_results(crawl_id)

client.web_scraping_api.cancel_crawl(crawl_id)
```

`get_crawl_status` returns `pending`, `done`, `faulted`, `cancelled` or `truncated`, with a `reason` when the crawl stopped early.

## Targets and parameter classes

Every target in the `Target` enum has a matching parameter class. The name of the class is the enum member name followed by `Params`:

```
Target.GoogleSearch → GoogleSearchParams
Target.Chatgpt      → ChatgptParams
Target.Airbnb       → AirbnbParams
```

For batch calls, insert `Batch` before `Params`. The batch class takes a list for the primary input and otherwise behaves the same:

```
Target.GoogleSearch → GoogleSearchBatchParams
Target.Chatgpt      → ChatgptBatchParams
Target.Airbnb       → AirbnbBatchParams
```

Two things follow from this:

- **You don't need to pass a target**. Each class already pins its own target, so `GoogleSearchParams(query="coffee shops")` is complete. Passing `target=Target.GoogleSearch` explicitly is allowed and type-checked, just redundant.
- **The `Target` enum is still useful**. Reach for it when you build dictionary payloads, or when you read the `target` field back off a response.

One target breaks the rule. `Target.Target` maps to `TargetStoreParams` and `TargetStoreBatchParams`, not `TargetParams`. Every other target is mechanical.

Each target accepts one primary input parameter (`url`, `query`, `product_id`, or `prompt`) together with optional configuration. The tables below show that primary input.

### Search engines

| Target                         | Parameter class               | Description                       | Example input                            |
| ------------------------------ | ----------------------------- | --------------------------------- | ---------------------------------------- |
| `Target.GoogleSearch`          | `GoogleSearchParams`          | Google Search results for a query | `query="coffee shops"`                   |
| `Target.GoogleLens`            | `GoogleLensParams`            | Google Lens reverse image search  | `query="https://example.com/cat.jpg"`    |
| `Target.GoogleTravelHotels`    | `GoogleTravelHotelsParams`    | Google Travel hotel listings      | `query="hotels in paris"`                |
| `Target.GoogleAds`             | `GoogleAdsParams`             | Google Ads results for a query    | `query="laptop"`                         |
| `Target.BingSearch`            | `BingSearchParams`            | Bing Search results               | `query="electric vehicles"`              |
| `Target.Bing`                  | `BingParams`                  | Raw Bing URL scraping             | `url="https://bing.com/search?q=laptop"` |

### eCommerce

| Target                     | Parameter class           | Description                           | Example input                              |
| -------------------------- | ------------------------- | ------------------------------------- | ------------------------------------------ |
| `Target.AmazonProduct`     | `AmazonProductParams`     | Amazon product detail page by ASIN    | `query="B09H74FXNW"`                       |
| `Target.AmazonSearch`      | `AmazonSearchParams`      | Amazon search results                 | `query="laptop"`                           |
| `Target.AmazonPricing`     | `AmazonPricingParams`     | Amazon pricing and offers             | `query="B09H74FXNW"`                       |
| `Target.AmazonSellers`     | `AmazonSellersParams`     | Amazon seller listings                | `query="B09H74FXNW"`                       |
| `Target.AmazonBestsellers` | `AmazonBestsellersParams` | Amazon bestsellers by category        | `query="electronics"`                      |
| `Target.WalmartProduct`    | `WalmartProductParams`    | Walmart product page by product ID    | `product_id="15296401808"`                 |
| `Target.WalmartSearch`     | `WalmartSearchParams`     | Walmart search results                | `query="laptop"`                           |
| `Target.Walmart`           | `WalmartParams`           | Raw Walmart URL scraping              | `url="https://walmart.com/ip/15296401808"` |
| `Target.TargetProduct`     | `TargetProductParams`     | Target.com product page by product ID | `product_id="92186007"`                    |
| `Target.TargetSearch`      | `TargetSearchParams`      | Target.com search results             | `query="laptop"`                           |
| `Target.Target`            | `TargetStoreParams`       | Raw Target.com URL scraping           | `url="https://target.com/p/-/A-92186007"`  |

### Social media

| Target                           | Parameter class                 | Description                            | Example input                                 |
| -------------------------------- | ------------------------------- | -------------------------------------- | --------------------------------------------- |
| `Target.RedditPost`              | `RedditPostParams`              | Reddit post by URL                     | `url="https://reddit.com/r/nba/comments/..."` |
| `Target.RedditSubreddit`         | `RedditSubredditParams`         | Reddit subreddit by URL                | `url="https://reddit.com/r/nba/"`             |
| `Target.RedditUser`              | `RedditUserParams`              | Reddit user profile by URL             | `url="https://reddit.com/user/example/"`      |
| `Target.YoutubeSearch`           | `YoutubeSearchParams`           | YouTube search results                 | `query="ambient music"`                       |
| `Target.YoutubeMetadata`         | `YoutubeMetadataParams`         | YouTube video metadata by ID           | `query="dFu9aKJoqGg"`                         |
| `Target.YoutubeSubtitles`        | `YoutubeSubtitlesParams`        | YouTube video subtitles by ID          | `query="dFu9aKJoqGg"`                         |
| `Target.YoutubeChannel`          | `YoutubeChannelParams`          | YouTube channel by handle or ID        | `query="@decodo_official"`                    |
| `Target.TiktokPost`              | `TiktokPostParams`              | TikTok post by URL                     | `url="https://www.tiktok.com/@nba/video/..."` |
| `Target.TiktokShopSearch`        | `TiktokShopSearchParams`        | TikTok Shop search results             | `query="wireless earbuds"`                    |
| `Target.TiktokShopProduct`       | `TiktokShopProductParams`       | TikTok Shop product page by product ID | `product_id="7100000000000000000"`            |
| `Target.Tiktok`                  | `TiktokParams`                  | Raw TikTok URL scraping                | `url="https://www.tiktok.com/@nba"`           |

### AI tools

| Target                | Parameter class      | Description                      | Example input                                 |
| --------------------- | -------------------- | -------------------------------- | --------------------------------------------- |
| `Target.Chatgpt`      | `ChatgptParams`      | ChatGPT response for a prompt    | `prompt="What are the top three dog breeds?"` |
| `Target.Perplexity`   | `PerplexityParams`   | Perplexity response for a prompt | `prompt="What causes seasonal allergies?"`    |
| `Target.Gemini`       | `GeminiParams`       | Gemini response for a prompt     | `prompt="What are the top three dog breeds?"` |
| `Target.GoogleAiMode` | `GoogleAiModeParams` | Google AI Mode response          | `query="What are the top three dog breeds?"`  |

### Other

| Target                 | Parameter class       | Description                           | Example input                                    |
| ---------------------- | --------------------- | ------------------------------------- | ------------------------------------------------ |
| `Target.Bbb`           | `BbbParams`           | Better Business Bureau listing by URL | `url="https://bbb.org/us/ny/new-york/..."`       |
| `Target.Autotrader`    | `AutotraderParams`    | Autotrader listing by URL             | `url="https://autotrader.com/cars-for-sale/..."` |
| `Target.Mobile`        | `MobileParams`        | Mobile.de listing by URL              | `url="https://mobile.de/auto/..."`               |
| `Target.Airbnb`        | `AirbnbParams`        | Airbnb listing by URL                 | `url="https://airbnb.com/rooms/12345"`           |
| `Target.AppleAppStore` | `AppleAppStoreParams` | Apple App Store app by URL            | `url="https://apps.apple.com/app/id12345"`       |

### Universal scraping

| Target             | Parameter class   | Description                       | Example input                              |
| ------------------ | ----------------- | --------------------------------- | ------------------------------------------ |
| `Target.Universal` | `UniversalParams` | Any URL via the universal scraper | `url="https://example.com"`                |
| `Target.Google`    | `GoogleParams`    | Raw Google URL scraping           | `url="https://google.com/search?q=laptop"` |
| `Target.Amazon`    | `AmazonParams`    | Raw Amazon URL scraping           | `url="https://amazon.com/dp/B09H74FXNW"`   |

For the full target list and parameter details, see the API documentation:

- [Target list](https://help.decodo.com/docs/web-scraping-api-targets)
- [Parameters](https://help.decodo.com/docs/web-scraping-api-parameters)

## Error handling

The SDK raises typed errors that map to API error codes:

```python
import time

from decodo import (
    AuthenticationError,
    DecodoClient,
    DecodoConfig,
    DecodoError,
    GoogleSearchParams,
    RateLimitError,
    TimeoutError,
    ValidationError,
    WebScrapingApiConfig,
)

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(
            api_key="<api_key>",
        ),
    )
)

params = GoogleSearchParams(
    query="coffee shops",
    geo="United States",
    parse=True,
)


def print_organic_results(response):
    parsed = response["results"][0]["content"]["results"]["results"]

    for item in parsed["organic"]:
        print(item["pos"], item["title"], item["url"])


try:
    response = client.web_scraping_api.scrape(params)
    print_organic_results(response)

except AuthenticationError:
    # Handle authentication failures.
    raise SystemExit(
        "Invalid API key or token. Check your credentials in the dashboard."
    )

except RateLimitError:
    # Retry once after a short delay.
    time.sleep(5)
    response = client.web_scraping_api.scrape(params)
    print_organic_results(response)

except ValidationError as err:
    # Handle invalid request parameters.
    print("Payload rejected:", err.errors or err)

except TimeoutError:
    # Handle request timeouts.
    print(
        "Timed out. Increase timeout_ms or switch to scrape_async for slow targets."
    )

except DecodoError as err:
    # Catch any other SDK errors.
    print(f"Request failed with {err.status_code}: {err}")
```

The `["results"]["results"]` nesting above is the shape returned when `parse=True`. Without it, `content` holds the raw page instead.

| Error                 | Raised when                                                                          | Useful attributes              |
| --------------------- | ------------------------------------------------------------------------------------ | ------------------------------ |
| `AuthenticationError` | The API returns `401` or `403`                                                       | `status_code`                  |
| `RateLimitError`      | The API returns `429`                                                                | `status_code`                  |
| `ValidationError`     | The payload fails local schema validation, or the API returns `422`                  | `errors`, `status_code`        |
| `TimeoutError`        | The request exceeds `timeout_ms`                                                     | none                           |
| `CrawlTimeoutError`   | `crawl()` exceeds its `timeout`. Subclass of `TimeoutError`; the crawl keeps running | `crawl_id`                     |
| `CrawlError`          | `crawl()` ends `faulted` or `cancelled`. Subclass of `DecodoError`                   | `crawl_id`, `status`, `reason` |
| `DecodoError`         | Any other unsuccessful response. Base class for the three errors above               | `status_code`, `api_status`    |

Two things to keep in mind:

- **`TimeoutError` sits outside the `DecodoError` hierarchy**, so `except DecodoError` won't catch it. Catch it separately, as in the example above. Importing it from `decodo` also shadows the built-in `TimeoutError` in that module.
- **Typed parameters fail earlier than this**. An unknown field or a wrong type raises `pydantic.ValidationError` when you construct the parameter object, before any request is made. `decodo.ValidationError` covers payloads that are well-formed Python but rejected by the schema or the API.

## Related repositories

- [Web Scraping API](https://github.com/Decodo/Web-Scraping-API)
- [Decodo MCP Server](https://github.com/Decodo/mcp-server)
- [Decodo OpenClaw Skill](https://github.com/Decodo/decodo-openclaw-skill)

## Get started

Build scraping workflows with the Decodo Web Scraping API:

- [Start free plan](https://dashboard.decodo.com/)
- [Documentation](https://help.decodo.com/docs/introduction)
- [Discord](https://discord.gg/Ja8dqKgvbZ)

## License

Released under the [MIT License](https://github.com/Decodo/Decodo/blob/master/LICENSE).
