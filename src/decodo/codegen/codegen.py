from __future__ import annotations

from .web_scraping_api.generate_parameter_schemas import generate_parameter_schemas_file
from .web_scraping_api.generate_parameters import generate_parameters_file
from .web_scraping_api.generate_targets import generate_targets_file


def main() -> None:
    generate_parameters_file()
    generate_targets_file()
    generate_parameter_schemas_file()


if __name__ == "__main__":
    main()
