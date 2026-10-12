import json
import os

from decodo import DecodoClient, DecodoConfig, SearchRequest, WebScrapingApiConfig

api_key = os.environ["DECODO_API_KEY"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(api_key=api_key),
    )
)

result = client.web_scraping_api.search(
    SearchRequest(query="coffee shops", geo="United States", page=1)
)

for item in result.get("organic", []):
    print(item.get("rank"), item.get("title"), item.get("link"))

print(json.dumps(result.get("search_parameters"), indent=2))
