import json
import os

from decodo import AirbnbParams, DecodoClient, DecodoConfig, Target, WebScrapingApiConfig

token = os.environ["DECODO_TOKEN"]

client = DecodoClient(
    DecodoConfig(
        web_scraping_api=WebScrapingApiConfig(token=token),
    )
)

result = client.web_scraping_api.scrape(
    AirbnbParams(
        target=Target.Airbnb,
        url='https://www.airbnb.com/s/New-York-City--New-York--United-States/homes?refinement_paths%5B%5D=%2Fhomes&place_id=ChIJOwg_06VPwokRYv534QaPC8g&location_bb=QiOru8KTZn1CIegEwpSEhw%3D%3D&acp_id=6333bccb-ed88-460f-950a-ed9788913f4d&date_picker_type=calendar&search_type=autocomplete_click',
    )
)

print(json.dumps(result, indent=2))
