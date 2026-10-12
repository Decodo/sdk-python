# Minimal target enum — committed to source.
# Run `python -m decodo.codegen.codegen` to regenerate when the IR schema changes.
from __future__ import annotations

from enum import StrEnum


class Target(StrEnum):
    GoogleSearch = "google_search"
    GoogleTravelHotels = "google_travel_hotels"
    Google = "google"
    GoogleAiMode = "google_ai_mode"
    GoogleAds = "google_ads"
    GoogleLens = "google_lens"
    BingSearch = "bing_search"
    Bing = "bing"
    AmazonProduct = "amazon_product"
    AmazonPricing = "amazon_pricing"
    AmazonSearch = "amazon_search"
    AmazonSellers = "amazon_sellers"
    AmazonBestsellers = "amazon_bestsellers"
    Amazon = "amazon"
    WalmartProduct = "walmart_product"
    WalmartSearch = "walmart_search"
    Walmart = "walmart"
    TargetProduct = "target_product"
    TargetSearch = "target_search"
    Target = "target"
    Universal = "universal"
    Chatgpt = "chatgpt"
    Perplexity = "perplexity"
    Gemini = "gemini"
    Bbb = "bbb"
    Autotrader = "autotrader"
    Mobile = "mobile"
    Airbnb = "airbnb"
    AppleAppStore = "apple_app_store"
    TiktokPost = "tiktok_post"
    TiktokShopSearch = "tiktok_shop_search"
    TiktokShopProduct = "tiktok_shop_product"
    Tiktok = "tiktok"
    RedditPost = "reddit_post"
    RedditSubreddit = "reddit_subreddit"
    RedditUser = "reddit_user"
    YoutubeMetadata = "youtube_metadata"
    YoutubeSearch = "youtube_search"
    YoutubeSubtitles = "youtube_subtitles"
    YoutubeChannel = "youtube_channel"


targets: list[str] = [t.value for t in Target]
