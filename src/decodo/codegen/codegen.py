from __future__ import annotations

import os
import shutil

from .web_scraping_api.generate_parameters import generate_parameters_file
from .web_scraping_api.generate_targets import generate_targets_enum_file, generate_targets_file
from .web_scraping_api.shared import local_ir_path, out_dir


def main() -> None:
    os.makedirs(out_dir, exist_ok=True)
    init_path = os.path.join(out_dir, "__init__.py")
    if not os.path.exists(init_path):
        open(init_path, "w").close()

    generate_parameters_file()
    generate_targets_enum_file()
    generate_targets_file()

    # Copy the downloaded IR JSON into generated/ so BundledSchema can load
    # schemas directly at runtime without a generated Python file.
    ir_out_path = os.path.join(out_dir, "decodo.ir.json")
    shutil.copy2(local_ir_path, ir_out_path)
    print(f"Saved IR JSON to {ir_out_path}")


if __name__ == "__main__":
    main()
