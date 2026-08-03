# Decodo Python SDK

![Python](https://img.shields.io/badge/python-%3E%3D3.12-green)
![License](https://img.shields.io/badge/license-MIT-blue)

[![](https://dcbadge.limes.pink/api/server/https://discord.gg/Ja8dqKgvbZ)](https://discord.gg/Ja8dqKgvbZ)

<p align="center">
<a href="https://dashboard.decodo.com/integrations?utm_source=github&utm_medium=social&utm_campaign=pythion_sdk"> <img src="https://github.com/user-attachments/assets/a1e52a9e-3da1-4081-b3c6-053aafb8f196"/></a>

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

Get your Web Scraping API token from the [Decodo dashboard](https://dashboard.decodo.com/welcome). The token is the base64-encoded `user:password` value from the Basic Auth credentials shown in the dashboard.

```python
# main.py
from decodo import DecodoClient, DecodoConfig, WebScrapingApiConfig

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token="<basic_auth_token>"),
    )
)

result = client.web_scraping_api.scrape({
    "target": "google_search",
    "query": "coffee shops",
    "geo": "United States",
    "parse": True,
})
print(result)
```

Run the script:

```
python main.py
```

### With typed parameters (recommended)

Typed parameter classes are included in the package — no extra steps needed after `pip install decodo-sdk`:

```python
from decodo import DecodoClient, DecodoConfig, GoogleSearchParams, Target, WebScrapingApiConfig

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token="<basic_auth_token>"),
    )
)

result = client.web_scraping_api.scrape(
    GoogleSearchParams(
        target=Target.GoogleSearch,
        query="coffee shops",
        geo="United States",
        parse=True,
    )
)
print(result)
```

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
from decodo import DecodoClient, DecodoConfig, WebScrapingApiConfig

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token="<basic_auth_token>"),
        timeout_ms=120_000,  # optional, request timeout in ms (default: 180000)
    )
)
```

| Parameter | Description |
| --- | --- |
| `token` | Web Scraping API basic auth token - the base64-encoded `user:password` string from the Decodo dashboard |
| `timeout_ms` | Request timeout in milliseconds (default: 180000) |

## Web Scraping API

Access the API via `client.web_scraping_api`.

The snippets below assume you have already constructed a client. See [Configuration](#configuration) for how to build one.

### Sync scrape

Waits for the scraping result before returning:

```python
result = client.web_scraping_api.scrape({
    "target": "amazon_product",
    "query": "B09H74FXNW",
    "parse": True,
})
```

### Async scrape

Creates a scraping task and returns immediately. Poll separately for task status and results:

```python
task = client.web_scraping_api.scrape_async({
    "target": "google_search",
    "query": "laptop reviews",
    "parse": True,
})

meta = client.web_scraping_api.get_status(task["id"])
print(meta["status"])  # 'pending' | 'done' | 'faulted'

results = client.web_scraping_api.get_results(task["id"])
```

### Batch scrape

Send multiple queries or URLs in a single request:

```python
batch = client.web_scraping_api.scrape_batch({
    "target": "google_search",
    "query": ["coffee", "tea", "juice"],
    "parse": True,
})

coffee_task_id = batch["queries"][0]["id"]

client.web_scraping_api.get_results(coffee_task_id)
```

## Supported targets

Each target accepts one primary input parameter (`url`, `query`, `product_id`, or `prompt`) together with optional configuration. The examples below show the minimum payload to call `client.web_scraping_api.scrape(...)`.

### Search engines

| Target | Description | Example |
| --- | --- | --- |
| `Target.GoogleSearch` | Google Search results for a query | `{"target": Target.GoogleSearch, "query": "coffee shops"}` |
| `Target.GoogleMaps` | Google Maps search results | `{"target": Target.GoogleMaps, "query": "coffee shops brooklyn"}` |
| `Target.GoogleShoppingSearch` | Google Shopping search results | `{"target": Target.GoogleShoppingSearch, "query": "laptop"}` |
| `Target.GoogleShoppingProduct` | Google Shopping product page | `{"target": Target.GoogleShoppingProduct, "query": "B09H74FXNW"}` |
| `Target.GoogleSuggest` | Google Autocomplete suggestions | `{"target": Target.GoogleSuggest, "query": "coffee"}` |
| `Target.GoogleLens` | Google Lens reverse image search | `{"target": Target.GoogleLens, "query": "https://example.com/cat.jpg"}` |
| `Target.GoogleTravelHotels` | Google Travel hotel listings | `{"target": Target.GoogleTravelHotels, "query": "hotels in paris"}` |
| `Target.GoogleTrendsExplore` | Google Trends explore data | `{"target": Target.GoogleTrendsExplore, "query": "coffee"}` |
| `Target.GoogleAds` | Google Ads results for a query | `{"target": Target.GoogleAds, "query": "laptop"}` |
| `Target.BingSearch` | Bing Search results | `{"target": Target.BingSearch, "query": "electric vehicles"}` |
| `Target.Bing` | Raw Bing URL scraping | `{"target": Target.Bing, "url": "https://bing.com/search?q=laptop"}` |

### eCommerce

| Target | Description | Example |
| --- | --- | --- |
| `Target.AmazonProduct` | Amazon product detail page by ASIN | `{"target": Target.AmazonProduct, "query": "B09H74FXNW"}` |
| `Target.AmazonSearch` | Amazon search results | `{"target": Target.AmazonSearch, "query": "laptop"}` |
| `Target.AmazonPricing` | Amazon pricing and offers | `{"target": Target.AmazonPricing, "query": "B09H74FXNW"}` |
| `Target.AmazonSellers` | Amazon seller listings | `{"target": Target.AmazonSellers, "query": "B09H74FXNW"}` |
| `Target.AmazonBestsellers` | Amazon bestsellers by category | `{"target": Target.AmazonBestsellers, "query": "electronics"}` |
| `Target.WalmartProduct` | Walmart product page by product ID | `{"target": Target.WalmartProduct, "product_id": "15296401808"}` |
| `Target.WalmartSearch` | Walmart search results | `{"target": Target.WalmartSearch, "query": "laptop"}` |
| `Target.Walmart` | Raw Walmart URL scraping | `{"target": Target.Walmart, "url": "https://walmart.com/ip/15296401808"}` |
| `Target.TargetProduct` | Target.com product page by product ID | `{"target": Target.TargetProduct, "product_id": "92186007"}` |
| `Target.TargetSearch` | Target.com search results | `{"target": Target.TargetSearch, "query": "laptop"}` |
| `Target.Target` | Raw Target.com URL scraping | `{"target": Target.Target, "url": "https://target.com/p/-/A-92186007"}` |
| `Target.LowesSearch` | Lowe's search results | `{"target": Target.LowesSearch, "query": "drill"}` |
| `Target.Ecommerce` | Generic eCommerce page with parser | `{"target": Target.Ecommerce, "url": "https://example.com/product/123"}` |

### Social media

| Target | Description | Example |
| --- | --- | --- |
| `Target.RedditPost` | Reddit post by URL | `{"target": Target.RedditPost, "url": "https://reddit.com/r/nba/..."}` |
| `Target.RedditSubreddit` | Reddit subreddit by URL | `{"target": Target.RedditSubreddit, "url": "https://reddit.com/r/nba/"}` |
| `Target.RedditUser` | Reddit user profile by URL | `{"target": Target.RedditUser, "url": "https://reddit.com/user/example/"}` |
| `Target.YoutubeVideo` | YouTube video by ID | `{"target": Target.YoutubeVideo, "query": "dFu9aKJoqGg"}` |
| `Target.YoutubeSearch` | YouTube search results | `{"target": Target.YoutubeSearch, "query": "ambient music"}` |
| `Target.YoutubeSearchMax` | YouTube search results (extended) | `{"target": Target.YoutubeSearchMax, "query": "ambient music"}` |
| `Target.YoutubeMetadata` | YouTube video metadata by ID | `{"target": Target.YoutubeMetadata, "query": "dFu9aKJoqGg"}` |
| `Target.YoutubeTranscript` | YouTube video transcript by ID | `{"target": Target.YoutubeTranscript, "query": "dFu9aKJoqGg"}` |
| `Target.YoutubeSubtitles` | YouTube video subtitles by ID | `{"target": Target.YoutubeSubtitles, "query": "dFu9aKJoqGg"}` |
| `Target.YoutubeChannel` | YouTube channel by URL | `{"target": Target.YoutubeChannel, "url": "https://youtube.com/@mkbhd"}` |
| `Target.TiktokPost` | TikTok post by URL | `{"target": Target.TiktokPost, "url": "https://www.tiktok.com/@nba/video/..."}` |
| `Target.TiktokShopSearch` | TikTok Shop search results | `{"target": Target.TiktokShopSearch, "query": "wireless earbuds"}` |
| `Target.TiktokShopProduct` | TikTok Shop product page | `{"target": Target.TiktokShopProduct, "url": "https://www.tiktok.com/view/product/..."}` |
| `Target.Tiktok` | Raw TikTok URL scraping | `{"target": Target.Tiktok, "url": "https://www.tiktok.com/@nba"}` |
| `Target.InstagramGraphqlProfile` | Instagram profile via GraphQL | `{"target": Target.InstagramGraphqlProfile, "query": "nba"}` |

### AI tools

| Target | Description | Example |
| --- | --- | --- |
| `Target.Chatgpt` | ChatGPT response for a prompt | `{"target": Target.Chatgpt, "prompt": "What are the top three dog breeds?"}` |
| `Target.Perplexity` | Perplexity response for a prompt | `{"target": Target.Perplexity, "prompt": "What causes seasonal allergies?"}` |
| `Target.Gemini` | Gemini response for a prompt | `{"target": Target.Gemini, "prompt": "What are the top three dog breeds?"}` |
| `Target.GoogleAiMode` | Google AI Mode response | `{"target": Target.GoogleAiMode, "query": "What are the top three dog breeds?"}` |

### Other

| Target | Description | Example |
| --- | --- | --- |
| `Target.Bbb` | Better Business Bureau listing by URL | `{"target": Target.Bbb, "url": "https://bbb.org/us/ny/new-york/..."}` |
| `Target.Autotrader` | Autotrader listing by URL | `{"target": Target.Autotrader, "url": "https://autotrader.com/cars-for-sale/..."}` |
| `Target.Mobile` | Mobile.de listing by URL | `{"target": Target.Mobile, "url": "https://mobile.de/auto/..."}` |
| `Target.Airbnb` | Airbnb listing by URL | `{"target": Target.Airbnb, "url": "https://airbnb.com/rooms/12345"}` |
| `Target.AppleAppStore` | Apple App Store app by URL | `{"target": Target.AppleAppStore, "url": "https://apps.apple.com/app/id12345"}` |

### Universal scraping

| Target | Description | Example |
| --- | --- | --- |
| `Target.Universal` | Any URL via the universal scraper | `{"target": Target.Universal, "url": "https://example.com"}` |
| `Target.Google` | Raw Google URL scraping | `{"target": Target.Google, "url": "https://google.com/search?q=laptop"}` |
| `Target.Amazon` | Raw Amazon URL scraping | `{"target": Target.Amazon, "url": "https://amazon.com/dp/B09H74FXNW"}` |

> `Target.UniversalEcommerce` isn't listed above because it doesn't accept a primary input parameter like `url`, `query`, `product_id`, or `prompt`. It only accepts optional configuration fields such as `callback_url`.

For the full target list and parameter details, see the API documentation:

- [Target list](https://help.decodo.com/docs/web-scraping-api-targets)
- [Parameters](https://help.decodo.com/docs/web-scraping-api-parameters)

## Error handling

The SDK raises typed errors that map to API error codes:

```python
from decodo import (
    AuthenticationError,
    RateLimitError,
    ValidationError,
    TimeoutError,
)

try:
    client.web_scraping_api.scrape({
        "target": "google_search",
        "query": "test",
        "parse": True,
    })
except AuthenticationError:
    pass  # 401/403 - bad credentials
except RateLimitError:
    pass  # 429 - too many requests
except ValidationError as err:
    print(err.errors)  # 422 - invalid parameters
except TimeoutError:
    pass  # request timed out
```

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
