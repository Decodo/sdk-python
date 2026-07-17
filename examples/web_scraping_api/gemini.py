import json
import os

from decodo import DecodoClient, DecodoConfig, GeminiParams, Target, WebScrapingApiConfig

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

result = client.web_scraping_api.scrape(
    GeminiParams(
        target=Target.Gemini,
        prompt='What are the top three dog breeds?',
        parse=True,
        geo='United States',
    )
)

print(json.dumps(result, indent=2))
