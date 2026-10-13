import os

from decodo import DecodoClient, DecodoConfig, MapRequest, WebScrapingApiConfig

api_key = os.environ["DECODO_API_KEY"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(api_key=api_key),
    )
)

result = client.web_scraping_api.map(
    MapRequest(url="https://www.example.com", limit=100, sitemap="include")
)

mapped = result["results"][0]
print(f"Mapped {mapped['url']} (sitemap: {mapped['sitemap_status']})")

for link in mapped["content"]["links"]:
    print(link["url"])
