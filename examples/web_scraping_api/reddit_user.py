import json
import os

from decodo import (
    DecodoClient,
    DecodoConfig,
    RedditUserParams,
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
    RedditUserParams(
        target=Target.RedditUser,
        url='https://www.reddit.com/user/IWasRightOnce/',
    )
)

print(json.dumps(result, indent=2))
