from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

from .web_scraping_api.generate_parameters import generate_parameters_file
from .web_scraping_api.generate_targets import generate_targets_enum_file, generate_targets_file
from .web_scraping_api.shared import local_ir_path
from .web_scraping_api.shared import out_dir as _default_out_dir


def _in_site_packages() -> bool:
    return "site-packages" in str(Path(__file__).resolve())


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m decodo.codegen.codegen",
        description="Generate typed parameter classes from the Decodo IR schema.",
    )
    parser.add_argument(
        "--out-dir",
        metavar="PATH",
        default=None,
        help=(
            "Directory to write generated files into. "
            "Defaults to the package's built-in generated/ directory "
            "(editable installs only). Required for non-editable installs."
        ),
    )
    args = parser.parse_args()

    if args.out_dir is not None:
        out_dir = str(Path(args.out_dir).resolve())
    elif _in_site_packages():
        print(
            "error: running from a non-editable install.\n"
            "Generated files would be written into site-packages and silently reverted\n"
            "on the next `pip install --upgrade`.\n"
            "Use --out-dir <path> to specify a project-local output directory.",
            file=sys.stderr,
        )
        sys.exit(1)
    else:
        out_dir = _default_out_dir

    os.makedirs(out_dir, exist_ok=True)
    init_path = os.path.join(out_dir, "__init__.py")
    if not os.path.exists(init_path):
        open(init_path, "w").close()

    generate_parameters_file(out_dir)
    # The Target enum lives in decodo/targets.py (committed source). Only regenerate
    # it when we have write access to the source tree (editable install). Non-editable
    # installs already ship the enum baked into the package.
    if not _in_site_packages():
        generate_targets_enum_file()
    generate_targets_file(out_dir)

    # Copy the downloaded IR JSON into generated/ so BundledSchema can load
    # schemas directly at runtime without a generated Python file.
    ir_out_path = os.path.join(out_dir, "decodo.ir.json")
    shutil.copy2(local_ir_path, ir_out_path)
    print(f"Saved IR JSON to {ir_out_path}")


if __name__ == "__main__":
    main()
