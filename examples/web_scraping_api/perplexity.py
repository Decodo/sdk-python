import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    PerplexityParams,
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
    PerplexityParams(
        target=Target.Perplexity,
        prompt='What are the main causes of seasonal allergies?',
        parse=True,
        geo='United States',
    )
)

print(json.dumps(result, indent=2))
