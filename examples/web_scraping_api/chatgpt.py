import json
import os

from decodo import ChatgptParams, DecodoClient, DecodoConfig, Target, WebScrapingApiConfig

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

result = client.web_scraping_api.scrape(
    ChatgptParams(
        target=Target.Chatgpt,
        prompt='What are the top three dog breeds?',
        parse=True,
    )
)

print(json.dumps(result, indent=2))
