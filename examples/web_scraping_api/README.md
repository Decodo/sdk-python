# Examples

These examples use typed parameter classes (`GoogleSearchParams`, `AmazonProductParams`, etc.) which require running the type generator first:

```bash
python -m decodo.codegen.codegen
```

To run any example without the generator, replace the typed params with a plain dict:

```python
# instead of:
result = client.web_scraping_api.scrape(
    GoogleSearchParams(target=Target.GoogleSearch, query="coffee shops", parse=True)
)

# use:
result = client.web_scraping_api.scrape({
    "target": "google_search",
    "query": "coffee shops",
    "parse": True,
})
```

See the [root README](../../README.md) for the full list of target strings.
