# inputs/

This directory contains files fetched at codegen time and is excluded from version control.

- `decodo.ir.json` — the Intermediate Representation (IR) fetched from the Decodo GCS bucket.
  Run `decodo-codegen` (or `python -m decodo.codegen.codegen`) to populate it.
